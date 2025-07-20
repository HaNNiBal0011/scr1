"""
Главное окно приложения с модернизированным UI на CustomTkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
import threading
import time
import json
import csv
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from ui.components import (
    ModernFrame, StatusBar, ProgressFrame, 
    LogFrame, ResultsFrame, SettingsFrame
)
from ui.dialogs import SettingsDialog, AboutDialog, ExportDialog
from ui.themes import ThemeManager
from scraper.site_scrapers import HybridScraper
from scraper.base_scraper import ScrapingMethod, ScrapingStatus
from utils.config import Config
from utils.logger import setup_logger
from utils.export import ExportManager

class MainWindow(ctk.CTk):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        
        # Настройка основного окна
        self.title("Product Scraper Pro - Модернизированный парсер товаров")
        self.geometry("1400x900")
        self.minsize(1200, 700)
        
        # Инициализация компонентов
        self.config = Config()
        self.logger = setup_logger()
        self.theme_manager = ThemeManager()
        self.export_manager = ExportManager()
        
        # Состояние приложения
        self.scraper = None
        self.scraper_thread = None
        self.is_scraping = False
        self.results = []
        
        # Настройка темы
        self._setup_theme()
        
        # Создание интерфейса
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        # Загрузка настроек
        self.load_settings()
        
        self.logger.info("Главное окно инициализировано")
    
    def _setup_theme(self):
        """Настройка темы приложения"""
        theme = self.config.get('appearance', 'theme', 'system')
        ctk.set_appearance_mode(theme)
        
        color_theme = self.config.get('appearance', 'color_theme', 'blue')
        ctk.set_default_color_theme(color_theme)
    
    def _create_widgets(self):
        """Создание виджетов интерфейса"""
        # Главное меню
        self._create_menu()
        
        # Панель инструментов
        self.toolbar = self._create_toolbar()
        
        # Основной контейнер
        self.main_container = ctk.CTkFrame(self)
        
        # Панель настроек скрейпинга
        self.settings_frame = SettingsFrame(self.main_container)
        
        # Панель прогресса
        self.progress_frame = ProgressFrame(self.main_container)
        
        # Панель логов
        self.log_frame = LogFrame(self.main_container)
        
        # Панель результатов
        self.results_frame = ResultsFrame(self.main_container)
        
        # Статус бар
        self.status_bar = StatusBar(self)
    
    def _create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Загрузить список товаров...", command=self.load_products_file)
        file_menu.add_command(label="Сохранить результаты...", command=self.save_results)
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт в CSV...", command=self.export_to_csv)
        file_menu.add_command(label="Экспорт в JSON...", command=self.export_to_json)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.quit)
        
        # Меню "Скрейпинг"
        scraping_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Скрейпинг", menu=scraping_menu)
        scraping_menu.add_command(label="Начать скрейпинг", command=self.start_scraping)
        scraping_menu.add_command(label="Остановить скрейпинг", command=self.stop_scraping)
        scraping_menu.add_separator()
        scraping_menu.add_command(label="Очистить результаты", command=self.clear_results)
        scraping_menu.add_command(label="Очистить логи", command=self.clear_logs)
        
        # Меню "Настройки"
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        settings_menu.add_command(label="Настройки приложения...", command=self.open_settings)
        settings_menu.add_separator()
        
        # Подменю тем
        theme_menu = tk.Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Тема", menu=theme_menu)
        theme_menu.add_command(label="Системная", command=lambda: self.change_theme("system"))
        theme_menu.add_command(label="Светлая", command=lambda: self.change_theme("light"))
        theme_menu.add_command(label="Темная", command=lambda: self.change_theme("dark"))
        
        # Меню "Помощь"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="Горячие клавиши", command=self.show_hotkeys)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def _create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = ctk.CTkFrame(self, height=50)
        
        # Кнопки управления
        self.start_btn = ctk.CTkButton(
            toolbar, text="▶ Начать", 
            command=self.start_scraping,
            width=100, height=35
        )
        self.start_btn.pack(side="left", padx=5, pady=7)
        
        self.stop_btn = ctk.CTkButton(
            toolbar, text="⏹ Остановить", 
            command=self.stop_scraping,
            width=100, height=35,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=5, pady=7)
        
        # Разделитель
        separator = ctk.CTkFrame(toolbar, width=2, height=30)
        separator.pack(side="left", padx=10, pady=10, fill="y")
        
        # Кнопки файлов
        self.load_btn = ctk.CTkButton(
            toolbar, text="📁 Загрузить список", 
            command=self.load_products_file,
            width=140, height=35
        )
        self.load_btn.pack(side="left", padx=5, pady=7)
        
        self.export_btn = ctk.CTkButton(
            toolbar, text="💾 Экспорт", 
            command=self.export_results,
            width=100, height=35
        )
        self.export_btn.pack(side="left", padx=5, pady=7)
        
        # Разделитель
        separator2 = ctk.CTkFrame(toolbar, width=2, height=30)
        separator2.pack(side="left", padx=10, pady=10, fill="y")
        
        # Кнопка настроек
        self.settings_btn = ctk.CTkButton(
            toolbar, text="⚙ Настройки", 
            command=self.open_settings,
            width=100, height=35
        )
        self.settings_btn.pack(side="left", padx=5, pady=7)
        
        # Индикатор метода скрейпинга
        self.method_label = ctk.CTkLabel(
            toolbar, text="Метод: CloudScraper + Selenium", 
            font=ctk.CTkFont(size=12)
        )
        self.method_label.pack(side="right", padx=10, pady=7)
        
        return toolbar
    
    def _setup_layout(self):
        """Настройка расположения виджетов"""
        # Панель инструментов
        self.toolbar.pack(fill="x", padx=5, pady=(5, 0))
        
        # Главный контейнер
        self.main_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Настройка сетки главного контейнера
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)
        
        # Размещение панелей
        self.settings_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.progress_frame.grid(row=1, column=0, sticky="nsew", padx=(5, 2), pady=5)
        
        # Правая панель с вкладками
        self.right_panel = ctk.CTkTabview(self.main_container)
        self.right_panel.grid(row=1, column=1, sticky="nsew", padx=(2, 5), pady=5)
        
        # Вкладки
        self.right_panel.add("Результаты")
        self.right_panel.add("Логи")
        
        # Размещение компонентов в вкладках
        self.results_frame = ResultsFrame(self.right_panel.tab("Результаты"))
        self.results_frame.pack(fill="both", expand=True)
        
        self.log_frame = LogFrame(self.right_panel.tab("Логи"))
        self.log_frame.pack(fill="both", expand=True)
        
        # Статус бар
        self.status_bar.pack(fill="x", side="bottom")
    
    def _bind_events(self):
        """Привязка событий"""
        # Горячие клавиши
        self.bind_all("<Control-o>", lambda e: self.load_products_file())
        self.bind_all("<Control-s>", lambda e: self.save_results())
        self.bind_all("<Control-e>", lambda e: self.export_results())
        self.bind_all("<Control-Return>", lambda e: self.start_scraping())
        self.bind_all("<Escape>", lambda e: self.stop_scraping())
        self.bind_all("<F5>", lambda e: self.clear_results())
        self.bind_all("<Control-comma>", lambda e: self.open_settings())
        
        # События закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def start_scraping(self):
        """Начало скрейпинга"""
        if self.is_scraping:
            self.logger.warning("Скрейпинг уже запущен")
            return
        
        # Получение списка товаров
        products = self.settings_frame.get_products_list()
        if not products:
            messagebox.showwarning("Предупреждение", "Список товаров пуст!")
            return
        
        # Получение настроек
        settings = self.settings_frame.get_settings()
        
        self.logger.info(f"Начало скрейпинга {len(products)} товаров")
        
        # Обновление интерфейса
        self.is_scraping = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_bar.set_status("Скрейпинг запущен...")
        
        # Создание скрейпера
        self.scraper = HybridScraper(
            preferred_method=settings['method'],
            use_selenium_fallback=settings['use_fallback'],
            headless=settings['headless'],
            progress_callback=self.progress_frame.update_progress,
            log_callback=self.log_frame.add_log
        )
        
        # Запуск в отдельном потоке
        self.scraper_thread = threading.Thread(
            target=self._scraping_worker,
            args=(products, settings),
            daemon=True
        )
        self.scraper_thread.start()
    
    def stop_scraping(self):
        """Остановка скрейпинга"""
        if not self.is_scraping:
            return
        
        self.logger.info("Остановка скрейпинга...")
        
        if self.scraper:
            self.scraper.stop()
        
        self.status_bar.set_status("Остановка скрейпинга...")
        
        # Обновление интерфейса будет в _scraping_worker при завершении
    
    def _scraping_worker(self, products: List[Tuple[str, str]], settings: Dict):
        """Рабочая функция скрейпинга"""
        try:
            # Очистка предыдущих результатов
            self.results.clear()
            self.results_frame.clear_results()
            
            # Скрейпинг
            results = self.scraper.scrape_multiple_products(
                products, 
                max_workers=settings.get('max_workers', 3)
            )
            
            # Сохранение результатов
            self.results = results
            
            # Обновление таблицы результатов
            self.after(0, self._update_results_table)
            
            # Статистика
            stats = self.scraper.get_statistics()
            success_count = stats['success_count']
            total_count = len(products)
            
            # Обновление интерфейса
            self.after(0, lambda: self._scraping_finished(success_count, total_count))
            
        except Exception as e:
            self.logger.error(f"Ошибка в процессе скрейпинга: {e}")
            self.after(0, lambda: self._scraping_error(str(e)))
    
    def _scraping_finished(self, success_count: int, total_count: int):
        """Завершение скрейпинга"""
        self.is_scraping = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        # Обновление статус бара
        status_text = f"Скрейпинг завершен. Успешно: {success_count}/{total_count}"
        self.status_bar.set_status(status_text)
        
        # Обновление прогресса
        self.progress_frame.set_complete()
        
        self.logger.info(f"Скрейпинг завершен. Обработано {success_count} из {total_count} товаров")
    
    def _scraping_error(self, error_message: str):
        """Обработка ошибки скрейпинга"""
        self.is_scraping = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        self.status_bar.set_status(f"Ошибка скрейпинга: {error_message}")
        messagebox.showerror("Ошибка", f"Ошибка при скрейпинге:\n{error_message}")
    
    def _update_results_table(self):
        """Обновление таблицы результатов"""
        self.results_frame.update_results(self.results)
    
    def load_products_file(self):
        """Загрузка списка товаров из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл со списком товаров",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                products = []
                
                if file_path.endswith('.csv'):
                    with open(file_path, 'r', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        for row in reader:
                            if len(row) >= 2:
                                products.append((row[0].strip(), row[1].strip()))
                else:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        for line in file:
                            line = line.strip()
                            if line and ',' in line:
                                parts = line.split(',', 1)
                                if len(parts) == 2:
                                    products.append((parts[0].strip(), parts[1].strip()))
                
                if products:
                    self.settings_frame.set_products_list(products)
                    self.status_bar.set_status(f"Загружено {len(products)} товаров")
                    self.logger.info(f"Загружен список из {len(products)} товаров")
                else:
                    messagebox.showwarning("Предупреждение", "Файл не содержит валидных данных")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
                self.logger.error(f"Ошибка загрузки файла: {e}")
    
    def save_results(self):
        """Сохранение результатов"""
        if not self.results:
            messagebox.showinfo("Информация", "Нет результатов для сохранения")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить результаты",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.export_manager.export_to_csv(self.results, file_path)
                else:
                    self.export_manager.export_to_json(self.results, file_path)
                
                self.status_bar.set_status(f"Результаты сохранены: {file_path}")
                self.logger.info(f"Результаты сохранены в {file_path}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                self.logger.error(f"Ошибка сохранения: {e}")
    
    def export_to_csv(self):
        """Экспорт в CSV"""
        if not self.results:
            messagebox.showinfo("Информация", "Нет результатов для экспорта")
            return
        
        dialog = ExportDialog(self, "CSV Export")
        if dialog.result:
            file_path = filedialog.asksaveasfilename(
                title="Экспорт в CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if file_path:
                try:
                    self.export_manager.export_to_csv(self.results, file_path, dialog.result)
                    self.status_bar.set_status(f"Экспорт в CSV завершен: {file_path}")
                    self.logger.info(f"Данные экспортированы в CSV: {file_path}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка экспорта:\n{str(e)}")
    
    def export_to_json(self):
        """Экспорт в JSON"""
        if not self.results:
            messagebox.showinfo("Информация", "Нет результатов для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Экспорт в JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        
        if file_path:
            try:
                self.export_manager.export_to_json(self.results, file_path)
                self.status_bar.set_status(f"Экспорт в JSON завершен: {file_path}")
                self.logger.info(f"Данные экспортированы в JSON: {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка экспорта:\n{str(e)}")
    
    def export_results(self):
        """Общий диалог экспорта"""
        if not self.results:
            messagebox.showinfo("Информация", "Нет результатов для экспорта")
            return
        
        dialog = ExportDialog(self)
        # Диалог обрабатывает экспорт самостоятельно
    
    def clear_results(self):
        """Очистка результатов"""
        if messagebox.askyesno("Подтверждение", "Очистить все результаты?"):
            self.results.clear()
            self.results_frame.clear_results()
            self.status_bar.set_status("Результаты очищены")
            self.logger.info("Результаты очищены")
    
    def clear_logs(self):
        """Очистка логов"""
        if messagebox.askyesno("Подтверждение", "Очистить все логи?"):
            self.log_frame.clear_logs()
            self.status_bar.set_status("Логи очищены")
    
    def open_settings(self):
        """Открытие настроек"""
        dialog = SettingsDialog(self, self.config)
        if dialog.result:
            # Применение новых настроек
            self._apply_settings(dialog.result)
    
    def _apply_settings(self, settings: Dict):
        """Применение настроек"""
        # Сохранение в конфиг
        for section, values in settings.items():
            for key, value in values.items():
                self.config.set(section, key, value)
        
        # Применение темы
        if 'appearance' in settings:
            if 'theme' in settings['appearance']:
                self.change_theme(settings['appearance']['theme'])
        
        self.logger.info("Настройки применены")
    
    def change_theme(self, theme: str):
        """Изменение темы"""
        ctk.set_appearance_mode(theme)
        self.config.set('appearance', 'theme', theme)
        self.status_bar.set_status(f"Тема изменена на: {theme}")
    
    def show_hotkeys(self):
        """Показ горячих клавиш"""
        hotkeys_text = """
Горячие клавиши:

Ctrl+O - Открыть файл со списком товаров
Ctrl+S - Сохранить результаты
Ctrl+E - Экспорт результатов
Ctrl+Enter - Начать скрейпинг
Escape - Остановить скрейпинг
F5 - Очистить результаты
Ctrl+, - Открыть настройки
        """
        
        messagebox.showinfo("Горячие клавиши", hotkeys_text)
    
    def show_about(self):
        """Показ информации о программе"""
        AboutDialog(self)
    
    def load_settings(self):
        """Загрузка настроек"""
        try:
            # Настройка темы
            theme = self.config.get('appearance', 'theme', 'system')
            ctk.set_appearance_mode(theme)
            
            # Загрузка настроек в компоненты
            self.settings_frame.load_settings(self.config)
            
            self.logger.info("Настройки загружены")
            
        except Exception as e:
            self.logger.error(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохранение настроек"""
        try:
            # Сохранение настроек компонентов
            self.settings_frame.save_settings(self.config)
            
            # Сохранение конфигурации
            self.config.save()
            
            self.logger.info("Настройки сохранены")
            
        except Exception as e:
            self.logger.error(f"Ошибка сохранения настроек: {e}")
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if self.is_scraping:
            if messagebox.askyesno("Подтверждение", "Скрейпинг активен. Остановить и выйти?"):
                self.stop_scraping()
                # Ждем завершения потока
                if self.scraper_thread and self.scraper_thread.is_alive():
                    self.scraper_thread.join(timeout=5)
            else:
                return
        
        # Сохранение настроек
        self.save_settings()
        
        # Закрытие приложения
        self.destroy()
