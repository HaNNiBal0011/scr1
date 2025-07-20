"""
Главный класс скрейпера с гибридным подходом
"""

import time
import threading
from typing import List, Dict, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from scraper.base_scraper import BaseScraper, ScrapingResult, ScrapingStatus, ScrapingMethod, ProductInfo
from scraper.cloudscraper_scraper import CloudScraperScraper
from scraper.selenium_scraper import SeleniumScraper

class HybridScraper(BaseScraper):
    """Гибридный скрейпер с fallback стратегией"""
    
    def __init__(self, preferred_method: ScrapingMethod = ScrapingMethod.CLOUDSCRAPER,
                 use_selenium_fallback: bool = True, headless: bool = True, **kwargs):
        super().__init__(**kwargs)
        
        self.preferred_method = preferred_method
        self.use_selenium_fallback = use_selenium_fallback
        self.headless = headless
        
        # Инициализация скрейперов
        self.cloudscraper_scraper = None
        self.selenium_scraper = None
        
        # Статистика
        self.success_count = 0
        self.error_count = 0
        self.method_stats = {
            ScrapingMethod.CLOUDSCRAPER: {"success": 0, "error": 0},
            ScrapingMethod.SELENIUM: {"success": 0, "error": 0}
        }
    
    def _get_cloudscraper(self) -> CloudScraperScraper:
        """Получение экземпляра CloudScraper"""
        if not self.cloudscraper_scraper:
            self.cloudscraper_scraper = CloudScraperScraper(
                progress_callback=self.progress_callback,
                log_callback=self.log_callback
            )
        return self.cloudscraper_scraper
    
    def _get_selenium_scraper(self) -> SeleniumScraper:
        """Получение экземпляра Selenium скрейпера"""
        if not self.selenium_scraper:
            self.selenium_scraper = SeleniumScraper(
                headless=self.headless,
                progress_callback=self.progress_callback,
                log_callback=self.log_callback
            )
        return self.selenium_scraper
    
    def scrape_product(self, product_id: str, site: str) -> ScrapingResult:
        """Скрейпинг товара с использованием гибридного подхода"""
        if self.is_stopped:
            result = ScrapingResult()
            result.status = ScrapingStatus.STOPPED
            return result
        
        # Первая попытка с предпочтительным методом
        if self.preferred_method == ScrapingMethod.CLOUDSCRAPER:
            result = self._try_cloudscraper(product_id, site)
        else:
            result = self._try_selenium(product_id, site)
        
        # Fallback на другой метод при неудаче
        if (result.status != ScrapingStatus.SUCCESS and 
            self.use_selenium_fallback and not self.is_stopped):
            
            self._log(f"Первичный метод неуспешен, переключаемся на fallback для {product_id}")
            
            if self.preferred_method == ScrapingMethod.CLOUDSCRAPER:
                fallback_result = self._try_selenium(product_id, site)
            else:
                fallback_result = self._try_cloudscraper(product_id, site)
            
            # Используем результат fallback если он успешен
            if fallback_result.status == ScrapingStatus.SUCCESS:
                result = fallback_result
                result.attempts = 2
        
        # Обновление статистики
        self._update_stats(result)
        
        return result
    
    def _try_cloudscraper(self, product_id: str, site: str) -> ScrapingResult:
        """Попытка скрейпинга через CloudScraper"""
        try:
            if self.is_stopped:
                result = ScrapingResult()
                result.status = ScrapingStatus.STOPPED
                return result
            
            self._log(f"Попытка CloudScraper для {product_id} на {site}")
            scraper = self._get_cloudscraper()
            return scraper.scrape_product(product_id, site)
            
        except Exception as e:
            self._log(f"Ошибка CloudScraper: {e}", "ERROR")
            result = ScrapingResult()
            result.status = ScrapingStatus.ERROR
            result.error_message = f"CloudScraper ошибка: {str(e)}"
            result.method_used = ScrapingMethod.CLOUDSCRAPER
            return result
    
    def _try_selenium(self, product_id: str, site: str) -> ScrapingResult:
        """Попытка скрейпинга через Selenium"""
        try:
            if self.is_stopped:
                result = ScrapingResult()
                result.status = ScrapingStatus.STOPPED
                return result
            
            self._log(f"Попытка Selenium для {product_id} на {site}")
            scraper = self._get_selenium_scraper()
            return scraper.scrape_product(product_id, site)
            
        except Exception as e:
            self._log(f"Ошибка Selenium: {e}", "ERROR")
            result = ScrapingResult()
            result.status = ScrapingStatus.ERROR
            result.error_message = f"Selenium ошибка: {str(e)}"
            result.method_used = ScrapingMethod.SELENIUM
            return result
    
    def _update_stats(self, result: ScrapingResult):
        """Обновление статистики"""
        if result.status == ScrapingStatus.SUCCESS:
            self.success_count += 1
            if result.method_used:
                self.method_stats[result.method_used]["success"] += 1
        else:
            self.error_count += 1
            if result.method_used:
                self.method_stats[result.method_used]["error"] += 1
    
    def scrape_multiple_products(self, products: List[Tuple[str, str]], 
                                max_workers: int = 3) -> List[ScrapingResult]:
        """Скрейпинг множества товаров с многопоточностью"""
        results = []
        total_products = len(products)
        
        self._log(f"Начало скрейпинга {total_products} товаров")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Создание задач
            future_to_product = {
                executor.submit(self.scrape_product, product_id, site): (product_id, site)
                for product_id, site in products
            }
            
            # Обработка результатов
            completed = 0
            for future in as_completed(future_to_product):
                if self.is_stopped:
                    break
                
                product_id, site = future_to_product[future]
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    completed += 1
                    self._update_progress(
                        completed, total_products,
                        f"Обработано {completed}/{total_products} товаров"
                    )
                    
                    # Логирование результата
                    if result.status == ScrapingStatus.SUCCESS:
                        self._log(f"✓ {product_id} ({site}): {result.product.name}")
                    else:
                        self._log(f"✗ {product_id} ({site}): {result.error_message}")
                
                except Exception as e:
                    self._log(f"Ошибка обработки {product_id}: {e}", "ERROR")
                    error_result = ScrapingResult()
                    error_result.status = ScrapingStatus.ERROR
                    error_result.error_message = str(e)
                    results.append(error_result)
                    completed += 1
        
        self._log(f"Скрейпинг завершен. Успешно: {self.success_count}, Ошибки: {self.error_count}")
        return results
    
    def get_statistics(self) -> Dict:
        """Получение статистики скрейпинга"""
        total_attempts = self.success_count + self.error_count
        
        stats = {
            "total_attempts": total_attempts,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": (self.success_count / total_attempts * 100) if total_attempts > 0 else 0,
            "method_stats": {}
        }
        
        for method, data in self.method_stats.items():
            method_total = data["success"] + data["error"]
            stats["method_stats"][method.value] = {
                "total": method_total,
                "success": data["success"],
                "error": data["error"],
                "success_rate": (data["success"] / method_total * 100) if method_total > 0 else 0
            }
        
        return stats
    
    def stop(self):
        """Остановка всех скрейперов"""
        super().stop()
        
        if self.cloudscraper_scraper:
            self.cloudscraper_scraper.stop()
        
        if self.selenium_scraper:
            self.selenium_scraper.stop()
    
    def __del__(self):
        """Деструктор - очистка ресурсов"""
        try:
            self.stop()
            
            # Закрытие Selenium драйвера если есть
            if self.selenium_scraper:
                del self.selenium_scraper
                
        except Exception:
            pass
