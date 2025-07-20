"""
Система логирования для приложения
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import threading
from pathlib import Path

class ColoredFormatter(logging.Formatter):
    """Форматер с цветным выводом для консоли"""
    
    # Цветовые коды ANSI
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        # Добавляем цвет к уровню логирования
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            )
        
        return super().format(record)

class ThreadSafeHandler(logging.Handler):
    """Потокобезопасный обработчик логов"""
    
    def __init__(self, handler):
        super().__init__()
        self.handler = handler
        self.lock = threading.Lock()
    
    def emit(self, record):
        with self.lock:
            self.handler.emit(record)
    
    def __getattr__(self, name):
        return getattr(self.handler, name)

class CallbackHandler(logging.Handler):
    """Обработчик для отправки логов в callback функцию"""
    
    def __init__(self, callback_func):
        super().__init__()
        self.callback_func = callback_func
    
    def emit(self, record):
        if self.callback_func:
            try:
                message = self.format(record)
                self.callback_func(message, record.levelname)
            except Exception:
                # Игнорируем ошибки в callback
                pass

class ScraperLogger:
    """Основной класс для логирования в приложении"""
    
    def __init__(self, name: str = "ProductScraper", log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.logger = None
        self.callback_handlers = []
        
        # Создаем директорию логов
        self.log_dir.mkdir(exist_ok=True)
        
        # Инициализация логгера
        self._setup_logger()
    
    def _setup_logger(self):
        """Настройка логгера"""
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Очищаем существующие обработчики
        self.logger.handlers.clear()
        
        # Форматы логирования
        detailed_format = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        simple_format = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        )
        
        colored_format = ColoredFormatter(
            '[%(asctime)s] %(levelname)s: %(message)s'
        )
        
        # Файловый обработчик (подробный лог)
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_format)
        self.logger.addHandler(ThreadSafeHandler(file_handler))
        
        # Файловый обработчик для ошибок
        error_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_format)
        self.logger.addHandler(ThreadSafeHandler(error_handler))
        
        # Консольный обработчик
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(colored_format)
        self.logger.addHandler(console_handler)
        
        # Обработчик для статистики
        stats_file = self.log_dir / f"{self.name}_stats.log"
        stats_handler = logging.handlers.RotatingFileHandler(
            stats_file,
            maxBytes=1*1024*1024,  # 1MB
            backupCount=2,
            encoding='utf-8'
        )
        stats_handler.setLevel(logging.INFO)
        stats_handler.setFormatter(simple_format)
        
        # Фильтр для статистики
        stats_handler.addFilter(self._stats_filter)
        self.logger.addHandler(ThreadSafeHandler(stats_handler))
    
    def _stats_filter(self, record):
        """Фильтр для статистики - только определенные сообщения"""
        stats_keywords = ['успешно', 'обработан', 'завершен', 'статистика', 'результат']
        return any(keyword in record.getMessage().lower() for keyword in stats_keywords)
    
    def add_callback_handler(self, callback_func, level: int = logging.INFO):
        """Добавление callback обработчика"""
        handler = CallbackHandler(callback_func)
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter('%(message)s'))
        
        self.callback_handlers.append(handler)
        self.logger.addHandler(handler)
    
    def remove_callback_handler(self, callback_func):
        """Удаление callback обработчика"""
        handlers_to_remove = []
        for handler in self.callback_handlers:
            if handler.callback_func == callback_func:
                handlers_to_remove.append(handler)
                self.logger.removeHandler(handler)
        
        for handler in handlers_to_remove:
            self.callback_handlers.remove(handler)
    
    def log_scraping_start(self, product_count: int, method: str):
        """Логирование начала скрейпинга"""
        self.logger.info("=== Начало скрейпинга ===")
        self.logger.info(f"Количество товаров: {product_count}")
        self.logger.info(f"Метод: {method}")
        current_time = datetime.now()
        self.logger.info(f"Время начала: {current_time.year:04d}-{current_time.month:02d}-{current_time.day:02d} {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
    
    def log_scraping_end(self, success_count: int, error_count: int, total_time: float):
        """Логирование завершения скрейпинга"""
        self.logger.info("=== Завершение скрейпинга ===")
        self.logger.info(f"Успешно обработано: {success_count}")
        self.logger.info(f"Ошибок: {error_count}")
        self.logger.info(f"Общее время: {total_time:.2f} сек")
        current_time = datetime.now()
        self.logger.info(f"Время завершения: {current_time.year:04d}-{current_time.month:02d}-{current_time.day:02d} {current_time.hour:02d}:{current_time.minute:02d}:{current_time.second:02d}")
    
    def log_product_result(self, product_id: str, site: str, success: bool, 
                          method: str = "", response_time: float = 0, error: str = ""):
        """Логирование результата обработки товара"""
        if success:
            self.logger.info(f"✓ {product_id} ({site}) - успешно обработан за {response_time:.2f}с [{method}]")
        else:
            self.logger.error(f"✗ {product_id} ({site}) - ошибка: {error} [{method}]")
    
    def log_method_fallback(self, product_id: str, primary_method: str, fallback_method: str):
        """Логирование переключения на fallback метод"""
        self.logger.warning(f"🔄 {product_id} - переключение с {primary_method} на {fallback_method}")
    
    def log_site_status(self, site: str, status: str, details: str = ""):
        """Логирование статуса сайта"""
        status_emoji = {
            "available": "🟢",
            "slow": "🟡", 
            "blocked": "🔴",
            "error": "❌"
        }
        
        emoji = status_emoji.get(status, "ℹ️")
        message = f"{emoji} {site}: {status}"
        if details:
            message += f" - {details}"
        
        if status in ["blocked", "error"]:
            self.logger.error(message)
        elif status == "slow":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Логирование метрик производительности"""
        self.logger.info("=== Метрики производительности ===")
        for metric, value in metrics.items():
            self.logger.info(f"{metric}: {value}")
    
    def debug(self, message: str):
        """Debug логирование"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Info логирование"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Warning логирование"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Error логирование"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Critical логирование"""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str):
        """Логирование исключения"""
        self.logger.exception(message)
    
    def set_level(self, level: int):
        """Установка уровня логирования"""
        self.logger.setLevel(level)
        
        # Обновляем уровень для консольного обработчика
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
                handler.setLevel(level)
    
    def get_log_files(self) -> Dict[str, str]:
        """Получение путей к файлам логов"""
        return {
            "main": str(self.log_dir / f"{self.name}.log"),
            "errors": str(self.log_dir / f"{self.name}_errors.log"),
            "stats": str(self.log_dir / f"{self.name}_stats.log")
        }
    
    def cleanup_old_logs(self, days: int = 30):
        """Очистка старых логов"""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)
        
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    self.logger.info(f"Удален старый лог файл: {log_file}")
                except Exception as e:
                    self.logger.error(f"Ошибка удаления лог файла {log_file}: {e}")

class LogAnalyzer:
    """Анализатор логов для получения статистики"""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = Path(log_file_path)
    
    def get_error_summary(self, last_hours: int = 24) -> Dict[str, int]:
        """Получение сводки ошибок за последние часы"""
        if not self.log_file_path.exists():
            return {}
        
        import re
        from datetime import datetime, timedelta
        
        error_counts = {}
        cutoff_time = datetime.now() - timedelta(hours=last_hours)
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if 'ERROR' in line or 'CRITICAL' in line:
                        # Попытка извлечь timestamp
                        timestamp_match = re.search(r'\[(.*?)\]', line)
                        if timestamp_match:
                            try:
                                # Parse timestamp safely
                                timestamp_str = timestamp_match.group(1)
                                try:
                                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    # Try alternative format
                                    timestamp = datetime.strptime(timestamp_str, '%H:%M:%S')
                                    # Use today's date
                                    today = datetime.now().date()
                                    timestamp = datetime.combine(today, timestamp.time())
                                if timestamp >= cutoff_time:
                                    # Извлекаем тип ошибки
                                    error_type = self._extract_error_type(line)
                                    error_counts[error_type] = error_counts.get(error_type, 0) + 1
                            except ValueError:
                                pass
        except Exception:
            pass
        
        return error_counts
    
    def _extract_error_type(self, log_line: str) -> str:
        """Извлечение типа ошибки из строки лога"""
        # Простая логика для классификации ошибок
        line_lower = log_line.lower()
        
        if 'timeout' in line_lower:
            return 'Timeout'
        elif 'connection' in line_lower:
            return 'Connection Error'
        elif 'blocked' in line_lower or 'captcha' in line_lower:
            return 'Site Blocking'
        elif 'selenium' in line_lower or 'webdriver' in line_lower:
            return 'WebDriver Error'
        elif 'parse' in line_lower or 'parsing' in line_lower:
            return 'Parsing Error'
        else:
            return 'Other Error'
    
    def get_success_rate(self, last_hours: int = 24) -> float:
        """Получение процента успешности за последние часы"""
        if not self.log_file_path.exists():
            return 0.0
        
        import re
        from datetime import datetime, timedelta
        
        success_count = 0
        error_count = 0
        cutoff_time = datetime.now() - timedelta(hours=last_hours)
        
        try:
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    timestamp_match = re.search(r'\[(.*?)\]', line)
                    if timestamp_match:
                        try:
                            # Parse timestamp safely
                            timestamp_str = timestamp_match.group(1)
                            try:
                                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            except ValueError:
                                # Try alternative format
                                timestamp = datetime.strptime(timestamp_str, '%H:%M:%S')
                                # Use today's date
                                today = datetime.now().date()
                                timestamp = datetime.combine(today, timestamp.time())
                            if timestamp >= cutoff_time:
                                if '✓' in line and 'успешно обработан' in line:
                                    success_count += 1
                                elif '✗' in line and 'ошибка:' in line:
                                    error_count += 1
                        except ValueError:
                            pass
        except Exception:
            pass
        
        total = success_count + error_count
        return (success_count / total * 100) if total > 0 else 0.0

# Глобальный экземпляр логгера
_global_logger: Optional[ScraperLogger] = None

def setup_logger(name: str = "ProductScraper", log_dir: str = "logs") -> ScraperLogger:
    """Настройка глобального логгера"""
    global _global_logger
    _global_logger = ScraperLogger(name, log_dir)
    return _global_logger

def get_logger() -> Optional[ScraperLogger]:
    """Получение глобального логгера"""
    return _global_logger

# Удобные функции для быстрого логирования
def log_info(message: str):
    """Быстрое info логирование"""
    if _global_logger:
        _global_logger.info(message)

def log_error(message: str, exc_info: bool = False):
    """Быстрое error логирование"""
    if _global_logger:
        _global_logger.error(message, exc_info)

def log_warning(message: str):
    """Быстрое warning логирование"""
    if _global_logger:
        _global_logger.warning(message)

def log_debug(message: str):
    """Быстрое debug логирование"""
    if _global_logger:
        _global_logger.debug(message)
