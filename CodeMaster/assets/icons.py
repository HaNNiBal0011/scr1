"""
Иконки и графические ресурсы для приложения
Использует SVG иконки для масштабируемости и современного дизайна
"""

import base64
from typing import Dict, Optional
import tkinter as tk
from tkinter import PhotoImage
import io

class IconManager:
    """Менеджер иконок приложения"""
    
    def __init__(self):
        self.icons_cache = {}
        self.svg_icons = self._get_svg_icons()
    
    def get_icon(self, name: str, size: int = 24) -> Optional[PhotoImage]:
        """Получение иконки по имени и размеру"""
        cache_key = f"{name}_{size}"
        
        if cache_key in self.icons_cache:
            return self.icons_cache[cache_key]
        
        if name in self.svg_icons:
            try:
                # Для SVG иконок используем текстовые символы Unicode
                # В реальном приложении здесь была бы конвертация SVG в PhotoImage
                icon = self._create_text_icon(self.svg_icons[name]['symbol'], size)
                self.icons_cache[cache_key] = icon
                return icon
            except Exception as e:
                print(f"Ошибка создания иконки {name}: {e}")
                return None
        
        return None
    
    def _create_text_icon(self, symbol: str, size: int) -> PhotoImage:
        """Создание текстовой иконки из Unicode символа"""
        # Создаем простую текстовую иконку
        # В реальном приложении можно использовать PIL для создания изображений
        return None  # Заглушка для совместимости
    
    def _get_svg_icons(self) -> Dict:
        """Получение SVG иконок"""
        return {
            # Основные иконки приложения
            'play': {
                'symbol': '▶',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>'''
            },
            'stop': {
                'symbol': '⏹',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 6h12v12H6z"/>
                </svg>'''
            },
            'pause': {
                'symbol': '⏸',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                </svg>'''
            },
            'folder': {
                'symbol': '📁',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M10 4H4c-1.11 0-2 .89-2 2v12c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V8c0-1.11-.89-2-2-2h-8l-2-2z"/>
                </svg>'''
            },
            'save': {
                'symbol': '💾',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/>
                </svg>'''
            },
            'settings': {
                'symbol': '⚙',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19.14,12.94c0.04-0.3,0.06-0.61,0.06-0.94c0-0.32-0.02-0.64-0.07-0.94l2.03-1.58c0.18-0.14,0.23-0.41,0.12-0.61 l-1.92-3.32c-0.12-0.22-0.37-0.29-0.59-0.22l-2.39,0.96c-0.5-0.38-1.03-0.7-1.62-0.94L14.4,2.81c-0.04-0.24-0.24-0.41-0.48-0.41 h-3.84c-0.24,0-0.43,0.17-0.47,0.41L9.25,5.35C8.66,5.59,8.12,5.92,7.63,6.29L5.24,5.33c-0.22-0.08-0.47,0-0.59,0.22L2.74,8.87 C2.62,9.08,2.66,9.34,2.86,9.48l2.03,1.58C4.84,11.36,4.8,11.69,4.8,12s0.02,0.64,0.07,0.94l-2.03,1.58 c-0.18,0.14-0.23,0.41-0.12,0.61l1.92,3.32c0.12,0.22,0.37,0.29,0.59,0.22l2.39-0.96c0.5,0.38,1.03,0.7,1.62,0.94l0.36,2.54 c0.05,0.24,0.24,0.41,0.48,0.41h3.84c0.24,0,0.44-0.17,0.47-0.41l0.36-2.54c0.59-0.24,1.13-0.56,1.62-0.94l2.39,0.96 c0.22,0.08,0.47,0,0.59-0.22l1.92-3.32c0.12-0.22,0.07-0.47-0.12-0.61L19.14,12.94z M12,15.6c-1.98,0-3.6-1.62-3.6-3.6 s1.62-3.6,3.6-3.6s3.6,1.62,3.6,3.6S13.98,15.6,12,15.6z"/>
                </svg>'''
            },
            'export': {
                'symbol': '📤',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
                </svg>'''
            },
            'import': {
                'symbol': '📥',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
                </svg>'''
            },
            'refresh': {
                'symbol': '🔄',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
                </svg>'''
            },
            'clear': {
                'symbol': '🗑',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                </svg>'''
            },
            'add': {
                'symbol': '➕',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>'''
            },
            'remove': {
                'symbol': '➖',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 13H5v-2h14v2z"/>
                </svg>'''
            },
            'edit': {
                'symbol': '✏',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                </svg>'''
            },
            'search': {
                'symbol': '🔍',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                </svg>'''
            },
            'info': {
                'symbol': 'ℹ',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                </svg>'''
            },
            'warning': {
                'symbol': '⚠',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                </svg>'''
            },
            'error': {
                'symbol': '❌',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.47 2 2 6.47 2 12s4.47 10 10 10 10-4.47 10-10S17.53 2 12 2zm5 13.59L15.59 17 12 13.41 8.41 17 7 15.59 10.59 12 7 8.41 8.41 7 12 10.59 15.59 7 17 8.41 13.41 12 17 15.59z"/>
                </svg>'''
            },
            'success': {
                'symbol': '✅',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>'''
            },
            'close': {
                'symbol': '✖',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>'''
            },
            'minimize': {
                'symbol': '🗕',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 19h12v2H6z"/>
                </svg>'''
            },
            'maximize': {
                'symbol': '🗖',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M4 4h16v16H4V4zm2 2v12h12V6H6z"/>
                </svg>'''
            },
            
            # Иконки сайтов
            'rozetka': {
                'symbol': '🟢',
                'svg': '''<svg viewBox="0 0 24 24" fill="#00A046">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            'allo': {
                'symbol': '🔵',
                'svg': '''<svg viewBox="0 0 24 24" fill="#0066CC">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            'comfy': {
                'symbol': '🟠',
                'svg': '''<svg viewBox="0 0 24 24" fill="#FF6600">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            'epicentr': {
                'symbol': '🟡',
                'svg': '''<svg viewBox="0 0 24 24" fill="#FFD700">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            
            # Иконки статуса
            'loading': {
                'symbol': '⏳',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M6 2v6h.01L6 8.01 10 12l-4 4 .01.01H6V22h12v-5.99h-.01L18 16l-4-4 4-3.99-.01-.01H18V2H6z"/>
                </svg>'''
            },
            'online': {
                'symbol': '🟢',
                'svg': '''<svg viewBox="0 0 24 24" fill="#4CAF50">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            'offline': {
                'symbol': '🔴',
                'svg': '''<svg viewBox="0 0 24 24" fill="#F44336">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            'unknown': {
                'symbol': '⚫',
                'svg': '''<svg viewBox="0 0 24 24" fill="#757575">
                    <circle cx="12" cy="12" r="10"/>
                </svg>'''
            },
            
            # Иконки методов скрейпинга
            'cloudscraper': {
                'symbol': '☁',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96z"/>
                </svg>'''
            },
            'selenium': {
                'symbol': '🌐',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zm6.93 6h-2.95c-.32-1.25-.78-2.45-1.38-3.56 1.84.63 3.37 1.91 4.33 3.56zM12 4.04c.83 1.2 1.48 2.53 1.91 3.96h-3.82c.43-1.43 1.08-2.76 1.91-3.96zM4.26 14C4.1 13.36 4 12.69 4 12s.1-1.36.26-2h3.38c-.08.66-.14 1.32-.14 2 0 .68.06 1.34.14 2H4.26zm.82 2h2.95c.32 1.25.78 2.45 1.38 3.56-1.84-.63-3.37-1.9-4.33-3.56zm2.95-8H5.08c.96-1.66 2.49-2.93 4.33-3.56C8.81 5.55 8.35 6.75 8.03 8zM12 19.96c-.83-1.2-1.48-2.53-1.91-3.96h3.82c-.43 1.43-1.08 2.76-1.91 3.96zM14.34 14H9.66c-.09-.66-.16-1.32-.16-2 0-.68.07-1.35.16-2h4.68c.09.65.16 1.32.16 2 0 .68-.07 1.34-.16 2zm.25 5.56c.6-1.11 1.06-2.31 1.38-3.56h2.95c-.96 1.65-2.49 2.93-4.33 3.56zM16.36 14c.08-.66.14-1.32.14-2 0-.68-.06-1.34-.14-2h3.38c.16.64.26 1.31.26 2s-.1 1.36-.26 2h-3.38z"/>
                </svg>'''
            },
            
            # Иконки экспорта
            'csv': {
                'symbol': '📄',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M18,20H6V4H13V9H18V20Z"/>
                </svg>'''
            },
            'json': {
                'symbol': '📋',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M5,3C3.89,3 3,3.89 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5C21,3.89 20.1,3 19,3H5M5,5H19V19H5V5M7,7V9H9V7H7M11,7V9H17V7H11M7,11V13H9V11H7M11,11V13H17V11H11M7,15V17H9V15H7M11,15V17H17V15H11Z"/>
                </svg>'''
            },
            'excel': {
                'symbol': '📊',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M21.17 3.25Q21.5 3.25 21.76 3.5 22 3.74 22 4.08V19.92Q22 20.26 21.76 20.5 21.5 20.75 21.17 20.75H7.83Q7.5 20.75 7.24 20.5 7 20.26 7 19.92V17H2.83Q2.5 17 2.24 16.76 2 16.5 2 16.17V7.83Q2 7.5 2.24 7.24 2.5 7 2.83 7H7V4.08Q7 3.74 7.24 3.5 7.5 3.25 7.83 3.25H21.17M7 13.06L8.18 15.28H9.97L8 12.06L9.93 8.89H8.22L7.13 10.9L7.09 10.96L7.06 11.03Q6.8 10.5 6.5 9.96 6.25 9.43 6 8.89H4.22L6.13 12.03L4.16 15.28H5.97L7 13.06M20 13.06V15.28H18.56V16.44H20V18.39H9V15.28H12.22L11.56 14.22L12.22 13.17H14.5L15.17 14.22L14.5 15.28H17V13.06H20M20 8.89H9V12.03H17V10.9H14.5L15.17 9.85L14.5 8.89H12.22L11.56 9.94L12.22 11H9V8.89H20Z"/>
                </svg>'''
            },
            
            # Дополнительные утилитарные иконки
            'copy': {
                'symbol': '📋',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                </svg>'''
            },
            'paste': {
                'symbol': '📄',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M19 2h-4.18C14.4.84 13.3 0 12 0c-1.3 0-2.4.84-2.82 2H5c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-7 0c.55 0 1 .45 1 1s-.45 1-1 1-1-.45-1-1 .45-1 1-1zm7 18H5V4h2v3h10V4h2v16z"/>
                </svg>'''
            },
            'link': {
                'symbol': '🔗',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"/>
                </svg>'''
            },
            'help': {
                'symbol': '❓',
                'svg': '''<svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
                </svg>'''
            }
        }
    
    def get_status_icon(self, status: str) -> str:
        """Получение иконки по статусу"""
        status_icons = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠',
            'info': 'ℹ',
            'loading': '⏳',
            'online': '🟢',
            'offline': '🔴',
            'unknown': '⚫'
        }
        return status_icons.get(status.lower(), '❓')
    
    def get_site_icon(self, site: str) -> str:
        """Получение иконки сайта"""
        site_icons = {
            'rozetka': '🟢',
            'allo': '🔵', 
            'comfy': '🟠',
            'epicentr': '🟡'
        }
        return site_icons.get(site.lower(), '🌐')
    
    def get_method_icon(self, method: str) -> str:
        """Получение иконки метода скрейпинга"""
        method_icons = {
            'cloudscraper': '☁',
            'selenium': '🌐',
            'hybrid': '🔄'
        }
        return method_icons.get(method.lower(), '⚙')
    
    def get_file_type_icon(self, file_type: str) -> str:
        """Получение иконки типа файла"""
        file_icons = {
            'csv': '📄',
            'json': '📋',
            'excel': '📊',
            'xlsx': '📊',
            'html': '🌐',
            'txt': '📄',
            'log': '📝'
        }
        return file_icons.get(file_type.lower(), '📄')
    
    def create_colored_icon(self, base_icon: str, color: str) -> str:
        """Создание цветной версии иконки (эмуляция)"""
        # В текстовых иконках цвет не применяется напрямую
        # Возвращаем базовую иконку
        return base_icon
    
    def get_unicode_symbols(self) -> Dict[str, str]:
        """Получение Unicode символов для иконок"""
        return {name: data['symbol'] for name, data in self.svg_icons.items()}
    
    def get_svg_content(self, name: str) -> Optional[str]:
        """Получение SVG содержимого иконки"""
        if name in self.svg_icons:
            return self.svg_icons[name]['svg']
        return None

# Глобальный экземпляр менеджера иконок
icon_manager = IconManager()

# Удобные функции для быстрого доступа к иконкам
def get_icon(name: str, size: int = 24) -> Optional[PhotoImage]:
    """Быстрое получение иконки"""
    return icon_manager.get_icon(name, size)

def get_status_icon(status: str) -> str:
    """Быстрое получение иконки статуса"""
    return icon_manager.get_status_icon(status)

def get_site_icon(site: str) -> str:
    """Быстрое получение иконки сайта"""
    return icon_manager.get_site_icon(site)

def get_method_icon(method: str) -> str:
    """Быстрое получение иконки метода"""
    return icon_manager.get_method_icon(method)

def get_file_type_icon(file_type: str) -> str:
    """Быстрое получение иконки типа файла"""
    return icon_manager.get_file_type_icon(file_type)

# Константы для часто используемых иконок
class Icons:
    """Константы иконок"""
    
    # Основные действия
    PLAY = '▶'
    STOP = '⏹'
    PAUSE = '⏸'
    REFRESH = '🔄'
    
    # Файловые операции
    FOLDER = '📁'
    SAVE = '💾'
    EXPORT = '📤'
    IMPORT = '📥'
    
    # Интерфейс
    SETTINGS = '⚙'
    CLOSE = '✖'
    MINIMIZE = '🗕'
    MAXIMIZE = '🗖'
    
    # Редактирование
    ADD = '➕'
    REMOVE = '➖'
    EDIT = '✏'
    CLEAR = '🗑'
    COPY = '📋'
    
    # Статусы
    SUCCESS = '✅'
    ERROR = '❌'
    WARNING = '⚠'
    INFO = 'ℹ'
    LOADING = '⏳'
    
    # Сайты
    ROZETKA = '🟢'
    ALLO = '🔵'
    COMFY = '🟠'
    EPICENTR = '🟡'
    
    # Методы
    CLOUDSCRAPER = '☁'
    SELENIUM = '🌐'
    HYBRID = '🔄'
    
    # Файлы
    CSV = '📄'
    JSON = '📋'
    EXCEL = '📊'
    HTML = '🌐'
    
    # Дополнительные
    SEARCH = '🔍'
    HELP = '❓'
    LINK = '🔗'
    ONLINE = '🟢'
    OFFLINE = '🔴'

