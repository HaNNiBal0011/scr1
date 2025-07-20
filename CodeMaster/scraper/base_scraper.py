"""
Базовый класс для всех скрейперов
Определяет общий интерфейс и функциональность
"""

import time
import random
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class ScrapingMethod(Enum):
    """Методы скрейпинга"""
    CLOUDSCRAPER = "cloudscraper"
    SELENIUM = "selenium"
    HYBRID = "hybrid"

class ScrapingStatus(Enum):
    """Статусы скрейпинга"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class ProductInfo:
    """Информация о товаре"""
    id: str
    name: str
    price: Optional[float] = None
    old_price: Optional[float] = None
    availability: str = "Неизвестно"
    url: str = ""
    image_url: str = ""
    description: str = ""
    characteristics: Dict[str, str] = None
    site: str = ""
    
    def __post_init__(self):
        if self.characteristics is None:
            self.characteristics = {}

@dataclass
class ScrapingResult:
    """Результат скрейпинга"""
    product: Optional[ProductInfo] = None
    status: ScrapingStatus = ScrapingStatus.IDLE
    error_message: str = ""
    method_used: Optional[ScrapingMethod] = None
    response_time: float = 0.0
    attempts: int = 0

class BaseScraper(ABC):
    """Базовый класс скрейпера"""
    
    def __init__(self, progress_callback: Optional[Callable] = None, 
                 log_callback: Optional[Callable] = None):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.is_stopped = False
        
        # Настройки скрейпинга
        self.delay_range = (1, 3)  # Задержка между запросами
        self.max_retries = 3
        self.timeout = 30
        
        # User agents для ротации
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
    
    @abstractmethod
    def scrape_product(self, product_id: str, site: str) -> ScrapingResult:
        """Абстрактный метод для скрейпинга товара"""
        pass
    
    def get_random_user_agent(self) -> str:
        """Получение случайного User-Agent"""
        return random.choice(self.user_agents)
    
    def add_delay(self):
        """Добавление случайной задержки"""
        if not self.is_stopped:
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
    
    def stop(self):
        """Остановка скрейпинга"""
        self.is_stopped = True
        self._log("Получен сигнал остановки скрейпинга")
    
    def _log(self, message: str, level: str = "INFO"):
        """Логирование с callback"""
        if level.upper() == "INFO":
            self.logger.info(message)
        elif level.upper() == "ERROR":
            self.logger.error(message)
        elif level.upper() == "WARNING":
            self.logger.warning(message)
        elif level.upper() == "DEBUG":
            self.logger.debug(message)
        
        if self.log_callback:
            self.log_callback(message, level)
    
    def _update_progress(self, current: int, total: int, message: str = ""):
        """Обновление прогресса с callback"""
        if self.progress_callback:
            progress = (current / total * 100) if total > 0 else 0
            self.progress_callback(progress, message)
    
    def clean_text(self, text: str) -> str:
        """Очистка текста от лишних символов"""
        if not text:
            return ""
        
        # Удаление лишних пробелов и переносов строк
        text = ' '.join(text.split())
        
        # Удаление специальных символов
        text = text.replace('\xa0', ' ').replace('\u200b', '')
        
        return text.strip()
    
    def parse_price(self, price_text: str) -> Optional[float]:
        """Парсинг цены из текста"""
        if not price_text:
            return None
        
        # Удаление всех символов кроме цифр, точек и запятых
        import re
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        
        if not price_clean:
            return None
        
        # Замена запятой на точку для корректного парсинга
        price_clean = price_clean.replace(',', '.')
        
        try:
            return float(price_clean)
        except ValueError:
            return None
    
    def validate_product_id(self, product_id: str) -> bool:
        """Валидация ID товара"""
        if not product_id or not isinstance(product_id, str):
            return False
        
        # Проверка на корректность ID (только цифры)
        return product_id.strip().isdigit()
    
    def get_site_base_url(self, site: str) -> str:
        """Получение базового URL сайта"""
        site_urls = {
            'rozetka': 'https://rozetka.com.ua',
            'allo': 'https://allo.ua',
            'comfy': 'https://comfy.ua',
            'epicentr': 'https://epicentrk.ua'
        }
        return site_urls.get(site.lower(), '')
    
    def format_product_url(self, product_id: str, site: str) -> str:
        """Форматирование URL товара"""
        base_url = self.get_site_base_url(site)
        if not base_url:
            return ""
        
        url_patterns = {
            'rozetka': f"{base_url}/ua/p{product_id}/",
            'allo': f"{base_url}/ua/p/{product_id}",
            'comfy': f"{base_url}/ua/product/{product_id}",
            'epicentr': f"{base_url}/ua/shop/p{product_id}"
        }
        
        return url_patterns.get(site.lower(), "")
