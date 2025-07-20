#!/usr/bin/env python3
"""
Рабочая версия приложения Product Scraper Pro
"""

import sys
import os
import customtkinter as ctk
from datetime import datetime

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск Product Scraper Pro...")

# Настройка CustomTkinter
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class ProductScraperGUI(ctk.CTk):
    """Главное окно приложения Product Scraper Pro"""
    
    def __init__(self):
        super().__init__()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Инициализация GUI...")
        
        # Настройка окна
        self.title("Product Scraper Pro - Модернизированный парсер товаров")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Создание интерфейса
        self.create_interface()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] GUI инициализирован успешно")
        
    def create_interface(self):
        """Создание пользовательского интерфейса"""
        
        # Заголовок
        header_frame = ctk.CTkFrame(self, height=80)
        header_frame.pack(fill="x", padx=20, pady=20)
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame, 
            text="Product Scraper Pro", 
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=25)
        
        subtitle_label = ctk.CTkLabel(
            header_frame, 
            text="Модернизированный парсер товаров с поддержкой JavaScript", 
            font=ctk.CTkFont(size=14)
        )
        subtitle_label.pack()
        
        # Главная панель
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Левая панель - настройки
        left_panel = ctk.CTkFrame(main_frame, width=300)
        left_panel.pack(side="left", fill="y", padx=(20, 10), pady=20)
        left_panel.pack_propagate(False)
        
        # Заголовок настроек
        settings_title = ctk.CTkLabel(
            left_panel, 
            text="Настройки скрейпинга", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        settings_title.pack(pady=20)
        
        # Метод скрейпинга
        method_label = ctk.CTkLabel(left_panel, text="Метод скрейпинга:")
        method_label.pack(pady=(10, 5))
        
        self.method_var = ctk.StringVar(value="CloudScraper")
        method_combo = ctk.CTkComboBox(
            left_panel,
            values=["CloudScraper", "Selenium", "Гибридный"],
            variable=self.method_var,
            width=250
        )
        method_combo.pack(pady=(0, 15))
        
        # Настройки
        self.headless_var = ctk.BooleanVar(value=True)
        headless_check = ctk.CTkCheckBox(
            left_panel,
            text="Headless режим (без GUI браузера)",
            variable=self.headless_var
        )
        headless_check.pack(pady=5, anchor="w", padx=20)
        
        self.fallback_var = ctk.BooleanVar(value=True)
        fallback_check = ctk.CTkCheckBox(
            left_panel,
            text="Использовать Selenium fallback",
            variable=self.fallback_var
        )
        fallback_check.pack(pady=5, anchor="w", padx=20)
        
        # Количество потоков
        threads_label = ctk.CTkLabel(left_panel, text="Количество потоков:")
        threads_label.pack(pady=(20, 5))
        
        self.threads_var = ctk.IntVar(value=3)
        threads_slider = ctk.CTkSlider(
            left_panel, 
            from_=1, to=10, 
            number_of_steps=9,
            variable=self.threads_var,
            width=250
        )
        threads_slider.pack(pady=(0, 10))
        
        self.threads_label = ctk.CTkLabel(left_panel, text="3 потока")
        self.threads_label.pack()
        threads_slider.configure(command=self.update_threads_label)
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(left_panel)
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        start_btn = ctk.CTkButton(
            buttons_frame,
            text="🚀 Запустить скрейпинг",
            command=self.start_scraping,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        start_btn.pack(fill="x", pady=5)
        
        load_btn = ctk.CTkButton(
            buttons_frame,
            text="📁 Загрузить список товаров",
            command=self.load_products
        )
        load_btn.pack(fill="x", pady=5)
        
        export_btn = ctk.CTkButton(
            buttons_frame,
            text="💾 Экспорт результатов",
            command=self.export_results
        )
        export_btn.pack(fill="x", pady=5)
        
        # Правая панель - информация и логи
        right_panel = ctk.CTkFrame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True, padx=(10, 20), pady=20)
        
        # Информационная панель
        info_title = ctk.CTkLabel(
            right_panel, 
            text="Информация о приложении", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        info_title.pack(pady=20)
        
        info_text = """
✓ Поддержка JavaScript-сайтов
✓ Использование CloudScraper для обхода Cloudflare
✓ Selenium WebDriver для сложных случаев
✓ Многопоточная обработка запросов
✓ Автоматический fallback между методами
✓ Экспорт в CSV, JSON, Excel форматы
✓ Подробное логирование процесса
✓ Настраиваемые задержки и таймауты

Готов к работе с украинскими интернет-магазинами:
• Rozetka.com.ua
• Allo.ua  
• Comfy.ua
• Epicentr.ua
        """.strip()
        
        info_label = ctk.CTkLabel(
            right_panel,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        )
        info_label.pack(padx=20, pady=10, fill="both", expand=True)
        
        # Статус бар
        self.status_frame = ctk.CTkFrame(self, height=40)
        self.status_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 20))
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Готов к работе",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=10)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Интерфейс создан успешно")
    
    def update_threads_label(self, value):
        """Обновление метки количества потоков"""
        threads = int(value)
        self.threads_label.configure(text=f"{threads} {'поток' if threads == 1 else 'потока' if threads < 5 else 'потоков'}")
    
    def start_scraping(self):
        """Запуск процесса скрейпинга"""
        method = self.method_var.get()
        threads = self.threads_var.get()
        headless = self.headless_var.get()
        fallback = self.fallback_var.get()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск скрейпинга:")
        print(f"  Метод: {method}")
        print(f"  Потоков: {threads}")
        print(f"  Headless: {headless}")
        print(f"  Fallback: {fallback}")
        
        self.status_label.configure(text=f"Запуск скрейпинга методом {method}...")
        
        # TODO: Здесь будет интеграция с основными скрейпинг модулями
    
    def load_products(self):
        """Загрузка списка товаров"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Загрузка списка товаров")
        self.status_label.configure(text="Загрузка списка товаров...")
        # TODO: Реализация загрузки файла
    
    def export_results(self):
        """Экспорт результатов"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Экспорт результатов")
        self.status_label.configure(text="Экспорт результатов...")
        # TODO: Реализация экспорта

def main():
    """Главная функция"""
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Создание приложения...")
        app = ProductScraperGUI()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск главного цикла...")
        app.mainloop()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Приложение завершено")
        
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Приложение остановлено пользователем")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()