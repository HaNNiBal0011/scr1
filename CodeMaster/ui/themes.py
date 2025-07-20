"""
Управление темами приложения
"""

import customtkinter as ctk
from typing import Dict, Optional
import json
import os

class ThemeManager:
    """Менеджер тем приложения"""
    
    def __init__(self):
        self.current_theme = "system"
        self.current_color_theme = "blue"
        self.custom_themes = {}
        
        # Предустановленные цветовые схемы
        self.color_themes = {
            "blue": {
                "primary": "#1f538d",
                "primary_hover": "#14375e",
                "secondary": "#212121",
                "success": "#2e7d32",
                "warning": "#ed6c02",
                "error": "#d32f2f",
                "info": "#0288d1"
            },
            "dark-blue": {
                "primary": "#1565c0",
                "primary_hover": "#0d47a1",
                "secondary": "#263238",
                "success": "#388e3c",
                "warning": "#f57c00",
                "error": "#d32f2f",
                "info": "#0277bd"
            },
            "green": {
                "primary": "#2e7d32",
                "primary_hover": "#1b5e20",
                "secondary": "#212121",
                "success": "#388e3c",
                "warning": "#f57c00",
                "error": "#d32f2f",
                "info": "#00695c"
            },
            "purple": {
                "primary": "#7b1fa2",
                "primary_hover": "#4a148c",
                "secondary": "#212121",
                "success": "#388e3c",
                "warning": "#f57c00",
                "error": "#d32f2f",
                "info": "#5e35b1"
            },
            "orange": {
                "primary": "#f57c00",
                "primary_hover": "#e65100",
                "secondary": "#212121",
                "success": "#388e3c",
                "warning": "#ff9800",
                "error": "#d32f2f",
                "info": "#0288d1"
            }
        }
        
        # Настройки для разных тем
        self.theme_settings = {
            "light": {
                "bg_color": ["#f0f0f0", "#e0e0e0"],
                "text_color": ["#000000", "#1a1a1a"],
                "text_color_disabled": ["#6b6b6b", "#5a5a5a"],
                "button_color": ["#3b8ed0", "#1f538d"],
                "button_hover_color": ["#36719f", "#14375e"],
                "frame_color": ["#ffffff", "#f0f0f0"]
            },
            "dark": {
                "bg_color": ["#212121", "#1a1a1a"],
                "text_color": ["#ffffff", "#e0e0e0"],
                "text_color_disabled": ["#969696", "#7a7a7a"],
                "button_color": ["#1f538d", "#14375e"],
                "button_hover_color": ["#14375e", "#0d2742"],
                "frame_color": ["#2b2b2b", "#212121"]
            }
        }
    
    def set_theme(self, theme: str):
        """Установка темы приложения"""
        if theme in ["system", "light", "dark"]:
            self.current_theme = theme
            ctk.set_appearance_mode(theme)
            return True
        return False
    
    def set_color_theme(self, color_theme: str):
        """Установка цветовой схемы"""
        if color_theme in self.color_themes:
            self.current_color_theme = color_theme
            ctk.set_default_color_theme(color_theme)
            return True
        return False
    
    def get_current_theme(self) -> str:
        """Получение текущей темы"""
        return self.current_theme
    
    def get_current_color_theme(self) -> str:
        """Получение текущей цветовой схемы"""
        return self.current_color_theme
    
    def get_available_themes(self) -> list:
        """Получение списка доступных тем"""
        return ["system", "light", "dark"]
    
    def get_available_color_themes(self) -> list:
        """Получение списка доступных цветовых схем"""
        return list(self.color_themes.keys())
    
    def get_theme_colors(self, theme: Optional[str] = None) -> Dict:
        """Получение цветов темы"""
        if theme is None:
            theme = self.current_theme
        
        if theme == "system":
            # Для системной темы возвращаем нейтральные цвета
            return self.theme_settings.get("light", {})
        
        return self.theme_settings.get(theme, {})
    
    def get_color_theme_colors(self, color_theme: Optional[str] = None) -> Dict:
        """Получение цветов цветовой схемы"""
        if color_theme is None:
            color_theme = self.current_color_theme
        
        return self.color_themes.get(color_theme, self.color_themes["blue"])
    
    def create_custom_theme(self, name: str, colors: Dict) -> bool:
        """Создание пользовательской темы"""
        required_keys = ["primary", "primary_hover", "secondary", "success", "warning", "error", "info"]
        
        if all(key in colors for key in required_keys):
            self.custom_themes[name] = colors
            return True
        return False
    
    def save_custom_themes(self, file_path: str) -> bool:
        """Сохранение пользовательских тем в файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_themes, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False
    
    def load_custom_themes(self, file_path: str) -> bool:
        """Загрузка пользовательских тем из файла"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.custom_themes = json.load(f)
                return True
        except Exception:
            pass
        return False
    
    def apply_theme_to_widget(self, widget, widget_type: str = "frame"):
        """Применение темы к виджету"""
        theme_colors = self.get_theme_colors()
        color_theme_colors = self.get_color_theme_colors()
        
        if not theme_colors:
            return
        
        try:
            if widget_type == "frame":
                if "frame_color" in theme_colors:
                    widget.configure(fg_color=theme_colors["frame_color"])
            
            elif widget_type == "button":
                if "button_color" in theme_colors:
                    widget.configure(fg_color=theme_colors["button_color"])
                if "button_hover_color" in theme_colors:
                    widget.configure(hover_color=theme_colors["button_hover_color"])
            
            elif widget_type == "label":
                if "text_color" in theme_colors:
                    widget.configure(text_color=theme_colors["text_color"])
            
            elif widget_type == "entry":
                if "frame_color" in theme_colors:
                    widget.configure(fg_color=theme_colors["frame_color"])
                if "text_color" in theme_colors:
                    widget.configure(text_color=theme_colors["text_color"])
        
        except Exception:
            # Если виджет не поддерживает эти настройки, игнорируем
            pass
    
    def get_status_color(self, status: str) -> str:
        """Получение цвета для статуса"""
        color_theme_colors = self.get_color_theme_colors()
        
        status_mapping = {
            "success": color_theme_colors.get("success", "#2e7d32"),
            "error": color_theme_colors.get("error", "#d32f2f"),
            "warning": color_theme_colors.get("warning", "#ed6c02"),
            "info": color_theme_colors.get("info", "#0288d1"),
            "primary": color_theme_colors.get("primary", "#1f538d"),
            "secondary": color_theme_colors.get("secondary", "#212121")
        }
        
        return status_mapping.get(status.lower(), color_theme_colors.get("primary", "#1f538d"))
    
    def create_gradient_effect(self, widget, start_color: str, end_color: str):
        """Создание градиентного эффекта (эмуляция)"""
        # CustomTkinter не поддерживает градиенты напрямую,
        # но можно использовать промежуточные цвета
        try:
            widget.configure(fg_color=start_color)
            # Можно добавить анимацию изменения цвета при hover
        except Exception:
            pass
    
    def animate_color_transition(self, widget, start_color: str, end_color: str, duration: int = 300):
        """Анимация перехода цвета"""
        # Простая эмуляция анимации через изменение цвета
        try:
            import threading
            import time
            
            def transition():
                # Простой переход без плавности
                # В реальной реализации можно использовать промежуточные цвета
                time.sleep(duration / 1000)
                widget.configure(fg_color=end_color)
            
            thread = threading.Thread(target=transition, daemon=True)
            thread.start()
            
        except Exception:
            # Если анимация не удалась, просто устанавливаем конечный цвет
            widget.configure(fg_color=end_color)
    
    def get_theme_config(self) -> Dict:
        """Получение полной конфигурации темы"""
        return {
            "theme": self.current_theme,
            "color_theme": self.current_color_theme,
            "theme_colors": self.get_theme_colors(),
            "color_theme_colors": self.get_color_theme_colors(),
            "custom_themes": self.custom_themes
        }
    
    def apply_theme_config(self, config: Dict):
        """Применение конфигурации темы"""
        if "theme" in config:
            self.set_theme(config["theme"])
        
        if "color_theme" in config:
            self.set_color_theme(config["color_theme"])
        
        if "custom_themes" in config:
            self.custom_themes.update(config["custom_themes"])

class ThemeCustomizer:
    """Кастомизатор тем для создания пользовательских тем"""
    
    def __init__(self, theme_manager: ThemeManager):
        self.theme_manager = theme_manager
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """Конвертация HEX в RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb: tuple) -> str:
        """Конвертация RGB в HEX"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def lighten_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Осветление цвета"""
        rgb = self.hex_to_rgb(hex_color)
        new_rgb = tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)
        return self.rgb_to_hex(new_rgb)
    
    def darken_color(self, hex_color: str, factor: float = 0.1) -> str:
        """Затемнение цвета"""
        rgb = self.hex_to_rgb(hex_color)
        new_rgb = tuple(max(0, int(c * (1 - factor))) for c in rgb)
        return self.rgb_to_hex(new_rgb)
    
    def generate_theme_palette(self, primary_color: str) -> Dict:
        """Генерация палитры темы на основе основного цвета"""
        return {
            "primary": primary_color,
            "primary_hover": self.darken_color(primary_color, 0.2),
            "secondary": self.darken_color(primary_color, 0.5),
            "success": "#2e7d32",
            "warning": "#ed6c02",
            "error": "#d32f2f",
            "info": self.lighten_color(primary_color, 0.2)
        }
    
    def create_complementary_theme(self, base_color: str) -> Dict:
        """Создание комплементарной темы"""
        # Простая логика для создания комплементарной цветовой схемы
        rgb = self.hex_to_rgb(base_color)
        
        # Инвертируем цвета для создания комплементарности
        comp_rgb = tuple(255 - c for c in rgb)
        comp_color = self.rgb_to_hex(comp_rgb)
        
        return self.generate_theme_palette(comp_color)
    
    def validate_theme_colors(self, colors: Dict) -> bool:
        """Валидация цветов темы"""
        required_colors = ["primary", "primary_hover", "secondary", "success", "warning", "error", "info"]
        
        # Проверяем наличие всех необходимых цветов
        if not all(color in colors for color in required_colors):
            return False
        
        # Проверяем формат HEX
        for color_value in colors.values():
            if not self._is_valid_hex_color(color_value):
                return False
        
        return True
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """Проверка валидности HEX цвета"""
        if not isinstance(color, str):
            return False
        
        if not color.startswith('#'):
            return False
        
        if len(color) != 7:
            return False
        
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False

class AccessibilityHelper:
    """Помощник для обеспечения доступности интерфейса"""
    
    @staticmethod
    def calculate_contrast_ratio(color1: str, color2: str) -> float:
        """Расчет коэффициента контрастности между двумя цветами"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def get_luminance(rgb):
            def adjust_color(c):
                c = c / 255.0
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            
            r, g, b = [adjust_color(c) for c in rgb]
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        lum1 = get_luminance(rgb1)
        lum2 = get_luminance(rgb2)
        
        lighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    @staticmethod
    def is_accessible_contrast(color1: str, color2: str, level: str = "AA") -> bool:
        """Проверка соответствия контрастности стандартам WCAG"""
        ratio = AccessibilityHelper.calculate_contrast_ratio(color1, color2)
        
        if level == "AAA":
            return ratio >= 7.0
        else:  # AA
            return ratio >= 4.5
    
    @staticmethod
    def suggest_accessible_color(base_color: str, background_color: str) -> str:
        """Предложение доступного цвета на основе фона"""
        customizer = ThemeCustomizer(None)
        
        current_ratio = AccessibilityHelper.calculate_contrast_ratio(base_color, background_color)
        
        if current_ratio >= 4.5:
            return base_color
        
        # Пробуем затемнить или осветлить цвет
        for factor in [0.1, 0.2, 0.3, 0.4, 0.5]:
            darker = customizer.darken_color(base_color, factor)
            if AccessibilityHelper.calculate_contrast_ratio(darker, background_color) >= 4.5:
                return darker
            
            lighter = customizer.lighten_color(base_color, factor)
            if AccessibilityHelper.calculate_contrast_ratio(lighter, background_color) >= 4.5:
                return lighter
        
        # Если не удалось найти подходящий цвет, возвращаем черный или белый
        black_ratio = AccessibilityHelper.calculate_contrast_ratio("#000000", background_color)
        white_ratio = AccessibilityHelper.calculate_contrast_ratio("#ffffff", background_color)
        
        return "#000000" if black_ratio > white_ratio else "#ffffff"
