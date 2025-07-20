"""
Управление конфигурацией приложения
"""

import configparser
import os
import json
from typing import Any, Dict, Optional, Union
from pathlib import Path

class Config:
    """Класс для управления конфигурацией приложения"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser(interpolation=None)
        
        # Настройки по умолчанию
        self.defaults = {
            'general': {
                'app_name': 'Product Scraper Pro',
                'version': '2.0.0',
                'author': 'Scraper Team',
                'last_updated': '',
                'debug_mode': 'false'
            },
            'appearance': {
                'theme': 'system',
                'color_theme': 'blue',
                'ui_scale': '1.0',
                'window_width': '1400',
                'window_height': '900',
                'window_maximized': 'false'
            },
            'scraping': {
                'method': 'cloudscraper',
                'use_fallback': 'true',
                'headless': 'true',
                'max_workers': '3',
                'delay_min': '1.0',
                'delay_max': '3.0',
                'page_timeout': '30',
                'element_timeout': '10',
                'max_retries': '3',
                'disable_images': 'true',
                'disable_javascript': 'false'
            },
            'network': {
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'use_proxy': 'false',
                'proxy_host': '',
                'proxy_port': '',
                'proxy_username': '',
                'proxy_password': '',
                'request_timeout': '30',
                'max_connections': '10'
            },
            'logging': {
                'log_level': 'INFO',
                'log_to_file': 'true',
                'log_to_console': 'true',
                'max_log_size': '10',
                'log_backup_count': '5',
                'log_directory': 'logs'
            },
            'export': {
                'default_format': 'CSV',
                'include_headers': 'true',
                'date_format': '%Y-%m-%d %H:%M:%S',
                'encoding': 'utf-8',
                'export_directory': 'exports'
            },
            'sites': {
                'rozetka_enabled': 'true',
                'allo_enabled': 'true',
                'comfy_enabled': 'true',
                'epicentr_enabled': 'true'
            },
            'advanced': {
                'selenium_pool_size': '2',
                'cloudscraper_pool_size': '5',
                'cache_enabled': 'false',
                'cache_ttl': '3600',
                'auto_save_results': 'true',
                'backup_enabled': 'true'
            }
        }
        
        self.load()
    
    def load(self):
        """Загрузка конфигурации из файла"""
        # Загружаем настройки по умолчанию
        self._load_defaults()
        
        # Если файл существует, загружаем из него
        if self.config_file.exists():
            try:
                self.config.read(self.config_file, encoding='utf-8')
                self._migrate_config()
            except Exception as e:
                print(f"Ошибка загрузки конфигурации: {e}")
                print("Используются настройки по умолчанию")
        
        # Создаем необходимые директории
        self._create_directories()
    
    def _load_defaults(self):
        """Загрузка настроек по умолчанию"""
        for section, options in self.defaults.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            for option, value in options.items():
                if not self.config.has_option(section, option):
                    self.config.set(section, option, value)
    
    def _migrate_config(self):
        """Миграция конфигурации при обновлении"""
        # Проверяем версию конфигурации и мигрируем при необходимости
        current_version = self.get('general', 'version', '1.0.0')
        
        if current_version < '2.0.0':
            # Миграция с версии 1.x
            self._migrate_from_v1()
            self.set('general', 'version', '2.0.0')
    
    def _migrate_from_v1(self):
        """Миграция с версии 1.x"""
        # Добавляем новые секции и опции, которых не было в v1
        pass
    
    def _create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            self.get('logging', 'log_directory'),
            self.get('export', 'export_directory')
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def save(self):
        """Сохранение конфигурации в файл"""
        try:
            # Обновляем дату последнего изменения
            from datetime import datetime
            self.set('general', 'last_updated', datetime.now().isoformat())
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False
    
    def get(self, section: str, option: str, fallback: Any = None) -> str:
        """Получение значения опции"""
        try:
            return self.config.get(section, option, fallback=str(fallback) if fallback is not None else None)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return str(fallback) if fallback is not None else ""
    
    def getint(self, section: str, option: str, fallback: int = 0) -> int:
        """Получение целочисленного значения"""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getfloat(self, section: str, option: str, fallback: float = 0.0) -> float:
        """Получение вещественного значения"""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getboolean(self, section: str, option: str, fallback: bool = False) -> bool:
        """Получение булевого значения"""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return fallback
    
    def getlist(self, section: str, option: str, fallback: list = None, separator: str = ',') -> list:
        """Получение списка значений"""
        if fallback is None:
            fallback = []
        
        try:
            value = self.config.get(section, option)
            if not value:
                return fallback
            return [item.strip() for item in value.split(separator) if item.strip()]
        except (configparser.NoSectionError, configparser.NoOptionError):
            return fallback
    
    def getdict(self, section: str, option: str, fallback: dict = None) -> dict:
        """Получение словаря из JSON строки"""
        if fallback is None:
            fallback = {}
        
        try:
            value = self.config.get(section, option)
            if not value:
                return fallback
            return json.loads(value)
        except (configparser.NoSectionError, configparser.NoOptionError, json.JSONDecodeError):
            return fallback
    
    def set(self, section: str, option: str, value: Any):
        """Установка значения опции"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        # Конвертируем значение в строку
        if isinstance(value, (list, dict)):
            value = json.dumps(value, ensure_ascii=False)
        else:
            value = str(value)
        
        self.config.set(section, option, value)
    
    def remove_option(self, section: str, option: str) -> bool:
        """Удаление опции"""
        try:
            return self.config.remove_option(section, option)
        except configparser.NoSectionError:
            return False
    
    def remove_section(self, section: str) -> bool:
        """Удаление секции"""
        return self.config.remove_section(section)
    
    def has_section(self, section: str) -> bool:
        """Проверка существования секции"""
        return self.config.has_section(section)
    
    def has_option(self, section: str, option: str) -> bool:
        """Проверка существования опции"""
        return self.config.has_option(section, option)
    
    def get_section(self, section: str) -> Dict[str, str]:
        """Получение всех опций секции"""
        try:
            return dict(self.config.items(section))
        except configparser.NoSectionError:
            return {}
    
    def get_sections(self) -> list:
        """Получение списка всех секций"""
        return self.config.sections()
    
    def update_section(self, section: str, options: Dict[str, Any]):
        """Обновление секции новыми опциями"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        for option, value in options.items():
            self.set(section, option, value)
    
    def reset_to_defaults(self, section: Optional[str] = None):
        """Сброс к настройкам по умолчанию"""
        if section:
            # Сброс конкретной секции
            if section in self.defaults:
                if self.config.has_section(section):
                    self.config.remove_section(section)
                self.config.add_section(section)
                for option, value in self.defaults[section].items():
                    self.config.set(section, option, value)
        else:
            # Сброс всей конфигурации
            self.config.clear()
            self._load_defaults()
    
    def export_config(self, file_path: str, format_type: str = 'ini') -> bool:
        """Экспорт конфигурации в файл"""
        try:
            file_path = Path(file_path)
            
            if format_type.lower() == 'json':
                # Экспорт в JSON
                config_dict = {}
                for section in self.config.sections():
                    config_dict[section] = dict(self.config.items(section))
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            else:
                # Экспорт в INI
                with open(file_path, 'w', encoding='utf-8') as f:
                    self.config.write(f)
            
            return True
        
        except Exception as e:
            print(f"Ошибка экспорта конфигурации: {e}")
            return False
    
    def import_config(self, file_path: str, format_type: str = 'ini') -> bool:
        """Импорт конфигурации из файла"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return False
            
            if format_type.lower() == 'json':
                # Импорт из JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                
                for section, options in config_dict.items():
                    if not self.config.has_section(section):
                        self.config.add_section(section)
                    for option, value in options.items():
                        self.config.set(section, option, str(value))
            
            else:
                # Импорт из INI
                self.config.read(file_path, encoding='utf-8')
            
            return True
        
        except Exception as e:
            print(f"Ошибка импорта конфигурации: {e}")
            return False
    
    def validate_config(self) -> Dict[str, list]:
        """Валидация конфигурации"""
        errors = {}
        
        # Проверка числовых значений
        numeric_checks = [
            ('scraping', 'max_workers', 1, 20),
            ('scraping', 'page_timeout', 5, 300),
            ('scraping', 'element_timeout', 1, 60),
            ('scraping', 'max_retries', 1, 10),
            ('network', 'request_timeout', 5, 300),
            ('network', 'max_connections', 1, 50),
            ('logging', 'max_log_size', 1, 100),
            ('logging', 'log_backup_count', 1, 20)
        ]
        
        for section, option, min_val, max_val in numeric_checks:
            value = self.getint(section, option)
            if not (min_val <= value <= max_val):
                if section not in errors:
                    errors[section] = []
                errors[section].append(f"{option} должен быть между {min_val} и {max_val}")
        
        # Проверка float значений
        float_checks = [
            ('scraping', 'delay_min', 0.1, 10.0),
            ('scraping', 'delay_max', 0.1, 10.0),
            ('appearance', 'ui_scale', 0.5, 2.0)
        ]
        
        for section, option, min_val, max_val in float_checks:
            value = self.getfloat(section, option)
            if not (min_val <= value <= max_val):
                if section not in errors:
                    errors[section] = []
                errors[section].append(f"{option} должен быть между {min_val} и {max_val}")
        
        # Проверка delay_min <= delay_max
        delay_min = self.getfloat('scraping', 'delay_min')
        delay_max = self.getfloat('scraping', 'delay_max')
        if delay_min > delay_max:
            if 'scraping' not in errors:
                errors['scraping'] = []
            errors['scraping'].append("delay_min не может быть больше delay_max")
        
        # Проверка существования директорий
        directories = [
            ('logging', 'log_directory'),
            ('export', 'export_directory')
        ]
        
        for section, option in directories:
            directory = self.get(section, option)
            if directory and not Path(directory).exists():
                try:
                    Path(directory).mkdir(parents=True, exist_ok=True)
                except Exception:
                    if section not in errors:
                        errors[section] = []
                    errors[section].append(f"Не удается создать директорию: {directory}")
        
        return errors
    
    def get_site_config(self, site: str) -> Dict[str, Any]:
        """Получение конфигурации для конкретного сайта"""
        site_configs = {
            'rozetka': {
                'enabled': self.getboolean('sites', 'rozetka_enabled'),
                'base_url': 'https://rozetka.com.ua',
                'selectors': {
                    'title': "h1[data-testid='product-title']",
                    'price': "[data-testid='price'] .price__value",
                    'old_price': ".price__old",
                    'availability': ".status-label"
                }
            },
            'allo': {
                'enabled': self.getboolean('sites', 'allo_enabled'),
                'base_url': 'https://allo.ua',
                'selectors': {
                    'title': "h1.p-view__title",
                    'price': ".p-view__price .sum",
                    'availability': ".p-view__status"
                }
            },
            'comfy': {
                'enabled': self.getboolean('sites', 'comfy_enabled'),
                'base_url': 'https://comfy.ua',
                'selectors': {
                    'title': ".product-title",
                    'price': ".price-current"
                }
            },
            'epicentr': {
                'enabled': self.getboolean('sites', 'epicentr_enabled'),
                'base_url': 'https://epicentrk.ua',
                'selectors': {
                    'title': "h1",
                    'price': "[class*='price']"
                }
            }
        }
        
        return site_configs.get(site.lower(), {})
    
    def __str__(self) -> str:
        """Строковое представление конфигурации"""
        sections = []
        for section in self.config.sections():
            options = []
            for option, value in self.config.items(section):
                options.append(f"  {option} = {value}")
            sections.append(f"[{section}]\n" + "\n".join(options))
        
        return "\n\n".join(sections)
