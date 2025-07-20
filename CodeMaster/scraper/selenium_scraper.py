"""
Selenium скрейпер с поддержкой JavaScript и обходом защиты
"""

import time
import random
import os
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    WebDriverException, StaleElementReferenceException
)
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager

from scraper.base_scraper import BaseScraper, ScrapingResult, ScrapingStatus, ScrapingMethod, ProductInfo

class SeleniumScraper(BaseScraper):
    """Selenium скрейпер с undetected-chromedriver"""
    
    def __init__(self, headless: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.headless = headless
        self.driver = None
        self.wait = None
        
        # Настройки ожидания
        self.page_load_timeout = 30
        self.element_wait_timeout = 10
        self.js_wait_timeout = 5
    
    def _setup_driver(self) -> bool:
        """Настройка Chrome WebDriver"""
        try:
            self._log("Настройка Chrome WebDriver...")
            
            # Опции Chrome
            options = uc.ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless=new")
            
            # Базовые опции для обхода детекции
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Дополнительные опции для стабильности
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--disable-images")
            options.add_argument("--disable-javascript-harmony-shipping")
            options.add_argument("--disable-background-timer-throttling")
            options.add_argument("--disable-renderer-backgrounding")
            options.add_argument("--disable-backgrounding-occluded-windows")
            
            # Размер окна
            options.add_argument("--window-size=1920,1080")
            
            # User Agent
            options.add_argument(f"--user-agent={self.get_random_user_agent()}")
            
            # Создание драйвера
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Настройка таймаутов
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.implicitly_wait(2)
            
            # Создание объекта ожидания
            self.wait = WebDriverWait(self.driver, self.element_wait_timeout)
            
            # Выполнение JavaScript для обхода детекции
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            self._log("Chrome WebDriver успешно настроен")
            return True
            
        except Exception as e:
            self._log(f"Ошибка настройки WebDriver: {e}", "ERROR")
            return False
    
    def _close_driver(self):
        """Закрытие WebDriver"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                self.wait = None
        except Exception as e:
            self._log(f"Ошибка при закрытии WebDriver: {e}", "WARNING")
    
    def scrape_product(self, product_id: str, site: str) -> ScrapingResult:
        """Скрейпинг товара с помощью Selenium"""
        start_time = time.time()
        result = ScrapingResult(method_used=ScrapingMethod.SELENIUM)
        
        if not self.validate_product_id(product_id):
            result.status = ScrapingStatus.ERROR
            result.error_message = "Некорректный ID товара"
            return result
        
        try:
            # Настройка драйвера если не настроен
            if not self.driver and not self._setup_driver():
                result.status = ScrapingStatus.ERROR
                result.error_message = "Не удалось настроить WebDriver"
                return result
            
            # Получение URL товара
            product_url = self.format_product_url(product_id, site)
            if not product_url:
                result.status = ScrapingStatus.ERROR
                result.error_message = f"Неподдерживаемый сайт: {site}"
                return result
            
            self._log(f"Загрузка страницы: {product_url}")
            
            # Загрузка страницы
            self.driver.get(product_url)
            
            # Ожидание загрузки и проверка на блокировку
            if self._wait_for_page_load(site):
                # Парсинг данных в зависимости от сайта
                product = self._parse_product_data(product_id, site, product_url)
                
                if product:
                    result.product = product
                    result.status = ScrapingStatus.SUCCESS
                    self._log(f"Товар успешно обработан: {product.name}")
                else:
                    result.status = ScrapingStatus.ERROR
                    result.error_message = "Не удалось извлечь данные товара"
            else:
                result.status = ScrapingStatus.ERROR
                result.error_message = "Страница заблокирована или не загрузилась"
            
        except TimeoutException:
            result.status = ScrapingStatus.ERROR
            result.error_message = "Превышено время ожидания загрузки страницы"
            self._log("Превышено время ожидания", "ERROR")
            
        except Exception as e:
            result.status = ScrapingStatus.ERROR
            result.error_message = f"Ошибка скрейпинга: {str(e)}"
            self._log(f"Ошибка: {e}", "ERROR")
        
        finally:
            result.response_time = time.time() - start_time
            result.attempts = 1
        
        return result
    
    def _wait_for_page_load(self, site: str) -> bool:
        """Ожидание загрузки страницы и проверка на блокировку"""
        try:
            # Ожидание основного контента
            time.sleep(random.uniform(2, 4))
            
            # Проверка на капчу или блокировку
            blocking_indicators = [
                "captcha", "blocked", "bot", "protection", 
                "verify", "challenge", "incapsula", "cloudflare"
            ]
            
            page_source = self.driver.page_source.lower()
            for indicator in blocking_indicators:
                if indicator in page_source:
                    self._log(f"Обнаружена блокировка: {indicator}", "WARNING")
                    return False
            
            # Ожидание специфичных элементов для каждого сайта
            if site.lower() == 'rozetka':
                return self._wait_rozetka_load()
            elif site.lower() == 'allo':
                return self._wait_allo_load()
            elif site.lower() == 'comfy':
                return self._wait_comfy_load()
            elif site.lower() == 'epicentr':
                return self._wait_epicentr_load()
            
            return True
            
        except Exception as e:
            self._log(f"Ошибка ожидания загрузки: {e}", "ERROR")
            return False
    
    def _wait_rozetka_load(self) -> bool:
        """Ожидание загрузки Rozetka"""
        try:
            # Ожидание основных элементов товара
            selectors_to_wait = [
                "h1[data-testid='product-title']",
                ".product-title",
                "[data-testid='price']",
                ".price"
            ]
            
            for selector in selectors_to_wait:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _wait_allo_load(self) -> bool:
        """Ожидание загрузки Allo"""
        try:
            selectors_to_wait = [
                "h1.p-view__title",
                ".p-view__price",
                ".product-title",
                ".price"
            ]
            
            for selector in selectors_to_wait:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _wait_comfy_load(self) -> bool:
        """Ожидание загрузки Comfy"""
        try:
            # Comfy может показывать страницу блокировки
            if "pardon our interruption" in self.driver.page_source.lower():
                return False
            
            selectors_to_wait = [
                ".product-title",
                ".price",
                "h1"
            ]
            
            for selector in selectors_to_wait:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _wait_epicentr_load(self) -> bool:
        """Ожидание загрузки Epicentr"""
        try:
            selectors_to_wait = [
                "h1",
                ".product-title",
                "[class*='price']",
                ".price"
            ]
            
            for selector in selectors_to_wait:
                try:
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    return True
                except TimeoutException:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _parse_product_data(self, product_id: str, site: str, url: str) -> Optional[ProductInfo]:
        """Парсинг данных товара"""
        try:
            if site.lower() == 'rozetka':
                return self._parse_rozetka_product(product_id, url)
            elif site.lower() == 'allo':
                return self._parse_allo_product(product_id, url)
            elif site.lower() == 'comfy':
                return self._parse_comfy_product(product_id, url)
            elif site.lower() == 'epicentr':
                return self._parse_epicentr_product(product_id, url)
            
            return None
            
        except Exception as e:
            self._log(f"Ошибка парсинга данных: {e}", "ERROR")
            return None
    
    def _parse_rozetka_product(self, product_id: str, url: str) -> Optional[ProductInfo]:
        """Парсинг товара Rozetka"""
        try:
            product = ProductInfo(id=product_id, url=url, site="rozetka")
            
            # Название товара
            title_selectors = [
                "h1[data-testid='product-title']",
                ".product-title",
                "h1"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.name = self.clean_text(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            # Цена
            price_selectors = [
                "[data-testid='price'] .price__value",
                ".price .price__value",
                ".price-value",
                ".price"
            ]
            
            for selector in price_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    price_text = element.text
                    product.price = self.parse_price(price_text)
                    break
                except NoSuchElementException:
                    continue
            
            # Старая цена
            old_price_selectors = [
                ".price__old",
                ".old-price"
            ]
            
            for selector in old_price_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    old_price_text = element.text
                    product.old_price = self.parse_price(old_price_text)
                    break
                except NoSuchElementException:
                    continue
            
            # Доступность
            availability_selectors = [
                ".status-label",
                ".availability-status"
            ]
            
            for selector in availability_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.availability = self.clean_text(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            # Изображение
            try:
                img_element = self.driver.find_element(By.CSS_SELECTOR, ".product-photo img, .gallery img")
                product.image_url = img_element.get_attribute("src")
            except NoSuchElementException:
                pass
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Rozetka: {e}", "ERROR")
            return None
    
    def _parse_allo_product(self, product_id: str, url: str) -> Optional[ProductInfo]:
        """Парсинг товара Allo"""
        try:
            product = ProductInfo(id=product_id, url=url, site="allo")
            
            # Название
            title_selectors = [
                "h1.p-view__title",
                ".product-title",
                "h1"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.name = self.clean_text(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            # Цена
            price_selectors = [
                ".p-view__price .sum",
                ".price .sum",
                ".price-current"
            ]
            
            for selector in price_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.price = self.parse_price(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            # Доступность
            try:
                status_element = self.driver.find_element(By.CSS_SELECTOR, ".p-view__status, .availability")
                product.availability = self.clean_text(status_element.text)
            except NoSuchElementException:
                product.availability = "В наличии"
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Allo: {e}", "ERROR")
            return None
    
    def _parse_comfy_product(self, product_id: str, url: str) -> Optional[ProductInfo]:
        """Парсинг товара Comfy"""
        try:
            product = ProductInfo(id=product_id, url=url, site="comfy")
            
            # Название
            title_selectors = [
                ".product-title",
                "h1"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.name = self.clean_text(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            # Цена
            price_selectors = [
                ".price-current",
                ".price"
            ]
            
            for selector in price_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.price = self.parse_price(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Comfy: {e}", "ERROR")
            return None
    
    def _parse_epicentr_product(self, product_id: str, url: str) -> Optional[ProductInfo]:
        """Парсинг товара Epicentr"""
        try:
            product = ProductInfo(id=product_id, url=url, site="epicentr")
            
            # Название
            title_selectors = [
                "h1",
                ".product-title"
            ]
            
            for selector in title_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    product.name = self.clean_text(element.text)
                    break
                except NoSuchElementException:
                    continue
            
            # Цена
            price_selectors = [
                "[class*='price']",
                ".price"
            ]
            
            for selector in price_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        price_text = element.text
                        if price_text and any(char.isdigit() for char in price_text):
                            product.price = self.parse_price(price_text)
                            break
                    if product.price:
                        break
                except NoSuchElementException:
                    continue
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Epicentr: {e}", "ERROR")
            return None
    
    def __del__(self):
        """Деструктор - закрытие драйвера"""
        self._close_driver()
