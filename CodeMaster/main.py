"""
Модернизированный парсер товаров с поддержкой JavaScript и улучшенным UI
Основная точка входа в приложение
"""

import sys
import os
import threading
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск приложения...")
print(f"[{datetime.now().strftime('%H:%M:%S')}] Python path добавлен: {os.path.dirname(os.path.abspath(__file__))}")

# Настройка CustomTkinter
print(f"[{datetime.now().strftime('%H:%M:%S')}] Настройка CustomTkinter...")
ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# Безопасный импорт компонентов
try:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт утилит...")
    from utils.logger import setup_logger
    from utils.config import Config
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Утилиты импортированы успешно")
except ImportError as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка импорта утилит: {e}")
    # Создаем заглушки для отсутствующих модулей
    setup_logger = lambda: None
    class Config:
        def get(self, section, key, default=None):
            return default

try:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт UI компонентов...")  
    from ui.main_window import MainWindow
    print(f"[{datetime.now().strftime('%H:%M:%S')}] UI компоненты импортированы успешно")
except ImportError as e:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка импорта UI: {e}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Используем упрощенный интерфейс...")
    MainWindow = None

class ProductScraperApp:
    """Главный класс приложения"""
    
    def __init__(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Инициализация ProductScraperApp...")
        
        try:
            self.logger = setup_logger()
            self.config = Config()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Конфигурация загружена")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка инициализации конфига/логгера: {e}")
            self.logger = None
            self.config = None
            
        self.main_window = None
        
    def run(self):
        """Запуск приложения"""
        try:
            if self.logger:
                self.logger.info("Запуск приложения Product Scraper")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Создание главного окна...")
            
            # Попытка создания полноценного интерфейса
            if MainWindow:
                try:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Создаю MainWindow...")
                    self.main_window = MainWindow()
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] MainWindow создан успешно")
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка создания MainWindow: {e}")
                    import traceback
                    traceback.print_exc()
                    self.main_window = None
            
            # Если не удалось создать полноценный интерфейс, используем упрощенный
            if not self.main_window:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Создаю упрощенный интерфейс...")
                self.main_window = self._create_simple_fallback()
            
            if not self.main_window:
                raise Exception("Не удалось создать интерфейс приложения")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Настройка обработчика закрытия...")
            # Обработка закрытия приложения
            self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск главного цикла...")
            
            # Запуск главного цикла
            self.main_window.mainloop()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Главный цикл завершен")
            
        except Exception as e:
            error_msg = f"Критическая ошибка при запуске: {e}"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
            
            if self.logger:
                self.logger.error(error_msg)
            
            try:
                messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение:\n{str(e)}")
            except:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Не удалось показать диалог ошибки")
    
    def _create_simple_fallback(self):
        """Создание упрощенного fallback интерфейса"""
        try:
            fallback_window = ctk.CTk()
            fallback_window.title("Product Scraper Pro - Упрощенный режим")
            fallback_window.geometry("800x600")
            
            # Простой интерфейс с информацией
            title_label = ctk.CTkLabel(
                fallback_window, 
                text="Product Scraper Pro", 
                font=ctk.CTkFont(size=24, weight="bold")
            )
            title_label.pack(pady=30)
            
            info_label = ctk.CTkLabel(
                fallback_window,
                text="Приложение запущено в упрощенном режиме\nДля полной функциональности проверьте файлы конфигурации",
                font=ctk.CTkFont(size=12),
                justify="center"
            )
            info_label.pack(pady=20)
            
            close_btn = ctk.CTkButton(
                fallback_window,
                text="Закрыть",
                command=fallback_window.quit,
                width=100
            )
            close_btn.pack(pady=20)
            
            return fallback_window
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка создания fallback интерфейса: {e}")
            return None
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Завершение работы приложения...")
            
            if self.logger:
                self.logger.info("Завершение работы приложения")
            
            # Сохранение конфигурации
            if self.main_window and hasattr(self.main_window, 'save_settings'):
                try:
                    self.main_window.save_settings()
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка сохранения настроек: {e}")
            
            # Завершение всех активных потоков
            if self.main_window and hasattr(self.main_window, 'scraper_thread'):
                if self.main_window.scraper_thread and self.main_window.scraper_thread.is_alive():
                    try:
                        self.main_window.stop_scraping()
                        self.main_window.scraper_thread.join(timeout=5)
                    except Exception as e:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка завершения потоков: {e}")
            
            if self.main_window:
                self.main_window.destroy()
            
        except Exception as e:
            error_msg = f"Ошибка при закрытии приложения: {e}"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
            if self.logger:
                self.logger.error(error_msg)
        finally:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Приложение завершено")
            sys.exit(0)

def main():
    """Главная функция"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск главной функции...")
        app = ProductScraperApp()
        app.run()
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Приложение остановлено пользователем")
        sys.exit(0)
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()