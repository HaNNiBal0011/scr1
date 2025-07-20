"""
CloudScraper скрейпер для быстрой обработки простых страниц
"""

import time
import random
from typing import Optional
import cloudscraper
from bs4 import BeautifulSoup
import trafilatura

from scraper.base_scraper import BaseScraper, ScrapingResult, ScrapingStatus, ScrapingMethod, ProductInfo

class CloudScraperScraper(BaseScraper):
    """CloudScraper для обхода защиты Cloudflare"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scraper = None
        self._setup_scraper()
    
    def _setup_scraper(self):
        """Настройка CloudScraper"""
        try:
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                },
                delay=random.uniform(1, 3)
            )
            
            # Базовые заголовки
            self.scraper.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'uk-UA,uk;q=0.9,en;q=0.8,ru;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            })
            
            self._log("CloudScraper успешно настроен")
            
        except Exception as e:
            self._log(f"Ошибка настройки CloudScraper: {e}", "ERROR")
    
    def scrape_product(self, product_id: str, site: str) -> ScrapingResult:
        """Скрейпинг товара с помощью CloudScraper"""
        start_time = time.time()
        result = ScrapingResult(method_used=ScrapingMethod.CLOUDSCRAPER)
        
        if not self.validate_product_id(product_id):
            result.status = ScrapingStatus.ERROR
            result.error_message = "Некорректный ID товара"
            return result
        
        if not self.scraper:
            self._setup_scraper()
            if not self.scraper:
                result.status = ScrapingStatus.ERROR
                result.error_message = "Не удалось настроить CloudScraper"
                return result
        
        try:
            # Получение URL товара
            product_url = self.format_product_url(product_id, site)
            if not product_url:
                result.status = ScrapingStatus.ERROR
                result.error_message = f"Неподдерживаемый сайт: {site}"
                return result
            
            self._log(f"Загрузка страницы через CloudScraper: {product_url}")
            
            # Установка случайного User-Agent
            self.scraper.headers['User-Agent'] = self.get_random_user_agent()
            
            # Выполнение запроса
            response = self.scraper.get(product_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Проверка на блокировку
                if self._is_blocked(response.text):
                    result.status = ScrapingStatus.ERROR
                    result.error_message = "Страница заблокирована или требует JavaScript"
                    self._log("Обнаружена блокировка CloudScraper", "WARNING")
                else:
                    # Парсинг данных
                    product = self._parse_product_data(product_id, site, product_url, response.text)
                    
                    if product:
                        result.product = product
                        result.status = ScrapingStatus.SUCCESS
                        self._log(f"Товар успешно обработан: {product.name}")
                    else:
                        result.status = ScrapingStatus.ERROR
                        result.error_message = "Не удалось извлечь данные товара"
            else:
                result.status = ScrapingStatus.ERROR
                result.error_message = f"HTTP ошибка: {response.status_code}"
                self._log(f"HTTP ошибка: {response.status_code}", "ERROR")
        
        except Exception as e:
            result.status = ScrapingStatus.ERROR
            result.error_message = f"Ошибка CloudScraper: {str(e)}"
            self._log(f"Ошибка: {e}", "ERROR")
        
        finally:
            result.response_time = time.time() - start_time
            result.attempts = 1
            
            # Добавление задержки между запросами
            self.add_delay()
        
        return result
    
    def _is_blocked(self, html_content: str) -> bool:
        """Проверка на блокировку или защиту"""
        blocking_indicators = [
            "checking your browser",
            "captcha",
            "protection",
            "verify you are human",
            "blocked",
            "access denied",
            "pardon our interruption",
            "incapsula",
            "cloudflare",
            "bot detection",
            "challenge",
            "javascript is required"
        ]
        
        content_lower = html_content.lower()
        for indicator in blocking_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _parse_product_data(self, product_id: str, site: str, url: str, html_content: str) -> Optional[ProductInfo]:
        """Парсинг данных товара из HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if site.lower() == 'rozetka':
                return self._parse_rozetka_product(product_id, url, soup)
            elif site.lower() == 'allo':
                return self._parse_allo_product(product_id, url, soup)
            elif site.lower() == 'comfy':
                return self._parse_comfy_product(product_id, url, soup)
            elif site.lower() == 'epicentr':
                return self._parse_epicentr_product(product_id, url, soup)
            
            return None
            
        except Exception as e:
            self._log(f"Ошибка парсинга данных: {e}", "ERROR")
            return None
    
    def _parse_rozetka_product(self, product_id: str, url: str, soup: BeautifulSoup) -> Optional[ProductInfo]:
        """Парсинг товара Rozetka"""
        try:
            product = ProductInfo(id=product_id, url=url, site="rozetka")
            
            # Название товара
            title_selectors = [
                "h1[data-testid='product-title']",
                ".product-title",
                "h1.product__title",
                "h1"
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    product.name = self.clean_text(element.get_text())
                    break
            
            # Цена
            price_selectors = [
                "[data-testid='price'] .price__value",
                ".price .price__value",
                ".price-value",
                ".product-price__big"
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    price_text = element.get_text()
                    product.price = self.parse_price(price_text)
                    break
            
            # Старая цена
            old_price_element = soup.select_one(".price__old, .old-price")
            if old_price_element:
                product.old_price = self.parse_price(old_price_element.get_text())
            
            # Доступность
            status_element = soup.select_one(".status-label, .availability-status")
            if status_element:
                product.availability = self.clean_text(status_element.get_text())
            
            # Изображение
            img_element = soup.select_one(".product-photo img, .gallery img")
            if img_element:
                product.image_url = img_element.get('src', '')
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Rozetka: {e}", "ERROR")
            return None
    
    def _parse_allo_product(self, product_id: str, url: str, soup: BeautifulSoup) -> Optional[ProductInfo]:
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
                element = soup.select_one(selector)
                if element:
                    product.name = self.clean_text(element.get_text())
                    break
            
            # Цена
            price_selectors = [
                ".p-view__price .sum",
                ".price .sum",
                ".price-current"
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    product.price = self.parse_price(element.get_text())
                    break
            
            # Доступность
            status_element = soup.select_one(".p-view__status, .availability")
            if status_element:
                product.availability = self.clean_text(status_element.get_text())
            else:
                product.availability = "В наличии"
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Allo: {e}", "ERROR")
            return None
    
    def _parse_comfy_product(self, product_id: str, url: str, soup: BeautifulSoup) -> Optional[ProductInfo]:
        """Парсинг товара Comfy"""
        try:
            product = ProductInfo(id=product_id, url=url, site="comfy")
            
            # Название
            title_selectors = [
                ".product-title",
                "h1"
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    product.name = self.clean_text(element.get_text())
                    break
            
            # Цена
            price_selectors = [
                ".price-current",
                ".price"
            ]
            
            for selector in price_selectors:
                element = soup.select_one(selector)
                if element:
                    product.price = self.parse_price(element.get_text())
                    break
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Comfy: {e}", "ERROR")
            return None
    
    def _parse_epicentr_product(self, product_id: str, url: str, soup: BeautifulSoup) -> Optional[ProductInfo]:
        """Парсинг товара Epicentr"""
        try:
            product = ProductInfo(id=product_id, url=url, site="epicentr")
            
            # Название
            title_selectors = [
                "h1",
                ".product-title"
            ]
            
            for selector in title_selectors:
                element = soup.select_one(selector)
                if element:
                    product.name = self.clean_text(element.get_text())
                    break
            
            # Цена
            price_selectors = [
                "[class*='price']",
                ".price"
            ]
            
            for selector in price_selectors:
                elements = soup.select(selector)
                for element in elements:
                    price_text = element.get_text()
                    if price_text and any(char.isdigit() for char in price_text):
                        product.price = self.parse_price(price_text)
                        break
                if product.price:
                    break
            
            return product if product.name else None
            
        except Exception as e:
            self._log(f"Ошибка парсинга Epicentr: {e}", "ERROR")
            return None
