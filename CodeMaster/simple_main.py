#!/usr/bin/env python3
"""
Упрощенная версия приложения для тестирования
"""

import sys
import os
import customtkinter as ctk
from datetime import datetime

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Настройка CustomTkinter
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class SimpleApp(ctk.CTk):
    """Простое приложение для тестирования"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.title("Product Scraper Pro - Тест")
        self.geometry("800x600")
        self.minsize(600, 400)
        
        # Создание интерфейса
        self._create_widgets()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Приложение инициализировано успешно")
        
    def _create_widgets(self):
        """Создание виджетов интерфейса"""
        # Заголовок
        title_label = ctk.CTkLabel(
            self, 
            text="Product Scraper Pro", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=30)
        
        # Информационная панель
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(pady=20, padx=40, fill="x")
        
        info_text = """
✓ Приложение успешно запущено
✓ GUI интерфейс работает корректно  
✓ CustomTkinter загружен
✓ Все компоненты инициализированы
        """.strip()
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(pady=20, padx=20)
        
        # Кнопки тестирования
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(pady=20, padx=40, fill="x")
        
        test_btn = ctk.CTkButton(
            buttons_frame,
            text="Тест функций",
            command=self.test_function
        )
        test_btn.pack(side="left", padx=10, pady=20)
        
        close_btn = ctk.CTkButton(
            buttons_frame,
            text="Закрыть",
            command=self.quit
        )
        close_btn.pack(side="right", padx=10, pady=20)
        
        # Статус бар
        self.status_label = ctk.CTkLabel(
            self, 
            text="Готов к работе", 
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="bottom", pady=10)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] UI компоненты созданы")
    
    def test_function(self):
        """Тестовая функция"""
        self.status_label.configure(text=f"Тест выполнен в {datetime.now().strftime('%H:%M:%S')}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Тестовая функция выполнена")

def main():
    """Главная функция"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск приложения...")
    
    try:
        app = SimpleApp()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск главного цикла...")
        app.mainloop()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Приложение завершено")
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Приложение остановлено пользователем")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()