"""
Компоненты пользовательского интерфейса
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import customtkinter as ctk
from typing import List, Dict, Tuple, Optional, Callable
from datetime import datetime
import threading

from scraper.base_scraper import ScrapingMethod, ScrapingResult, ScrapingStatus

class ModernFrame(ctk.CTkFrame):
    """Модернизированная рамка с дополнительными возможностями"""
    
    def __init__(self, parent, title: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.title = title
        
        if title:
            self.title_label = ctk.CTkLabel(
                self, text=title, 
                font=ctk.CTkFont(size=16, weight="bold")
            )
            self.title_label.pack(pady=(10, 5))

class StatusBar(ctk.CTkFrame):
    """Строка состояния"""
    
    def __init__(self, parent):
        super().__init__(parent, height=30)
        
        # Основной статус
        self.status_label = ctk.CTkLabel(
            self, text="Готов к работе", 
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        
        # Время
        self.time_label = ctk.CTkLabel(
            self, text="", 
            font=ctk.CTkFont(size=11)
        )
        self.time_label.pack(side="right", padx=10, pady=5)
        
        # Обновление времени
        self._update_time()
    
    def set_status(self, text: str):
        """Установка текста статуса"""
        self.status_label.configure(text=text)
    
    def _update_time(self):
        """Обновление времени"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.configure(text=current_time)
        self.after(1000, self._update_time)

class ProgressFrame(ModernFrame):
    """Панель прогресса с детальной информацией"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Прогресс выполнения")
        
        # Основной прогресс-бар
        self.main_progress = ctk.CTkProgressBar(self, width=300)
        self.main_progress.pack(pady=10, padx=20, fill="x")
        self.main_progress.set(0)
        
        # Метка прогресса
        self.progress_label = ctk.CTkLabel(
            self, text="0%", 
            font=ctk.CTkFont(size=12)
        )
        self.progress_label.pack(pady=5)
        
        # Детальная информация
        self.detail_frame = ctk.CTkFrame(self)
        self.detail_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Счетчики
        self.counters_frame = ctk.CTkFrame(self.detail_frame)
        self.counters_frame.pack(fill="x", padx=10, pady=10)
        
        # Успешно обработано
        self.success_label = ctk.CTkLabel(
            self.counters_frame, text="Успешно: 0", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="green"
        )
        self.success_label.pack(side="left", padx=10)
        
        # Ошибки
        self.error_label = ctk.CTkLabel(
            self.counters_frame, text="Ошибки: 0", 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="red"
        )
        self.error_label.pack(side="left", padx=10)
        
        # Общий счетчик
        self.total_label = ctk.CTkLabel(
            self.counters_frame, text="Всего: 0", 
            font=ctk.CTkFont(size=11)
        )
        self.total_label.pack(side="right", padx=10)
        
        # Текущее действие
        self.current_action = ctk.CTkLabel(
            self.detail_frame, text="Готов к работе", 
            font=ctk.CTkFont(size=10)
        )
        self.current_action.pack(pady=5)
        
        # Индикаторы методов
        self.methods_frame = ctk.CTkFrame(self.detail_frame)
        self.methods_frame.pack(fill="x", padx=10, pady=5)
        
        self.cloudscraper_indicator = ctk.CTkLabel(
            self.methods_frame, text="CloudScraper: 0", 
            font=ctk.CTkFont(size=10)
        )
        self.cloudscraper_indicator.pack(side="left", padx=5)
        
        self.selenium_indicator = ctk.CTkLabel(
            self.methods_frame, text="Selenium: 0", 
            font=ctk.CTkFont(size=10)
        )
        self.selenium_indicator.pack(side="left", padx=5)
        
        # Статистика
        self.success_count = 0
        self.error_count = 0
        self.total_count = 0
        self.cloudscraper_count = 0
        self.selenium_count = 0
    
    def update_progress(self, progress: float, message: str = ""):
        """Обновление прогресса"""
        # Обновление прогресс-бара
        progress_normalized = max(0, min(1, progress / 100))
        self.main_progress.set(progress_normalized)
        
        # Обновление метки
        self.progress_label.configure(text=f"{progress:.1f}%")
        
        # Обновление текущего действия
        if message:
            self.current_action.configure(text=message)
    
    def update_counters(self, success: int = None, errors: int = None, 
                       total: int = None, cloudscraper: int = None, selenium: int = None):
        """Обновление счетчиков"""
        if success is not None:
            self.success_count = success
            self.success_label.configure(text=f"Успешно: {success}")
        
        if errors is not None:
            self.error_count = errors
            self.error_label.configure(text=f"Ошибки: {errors}")
        
        if total is not None:
            self.total_count = total
            self.total_label.configure(text=f"Всего: {total}")
        
        if cloudscraper is not None:
            self.cloudscraper_count = cloudscraper
            self.cloudscraper_indicator.configure(text=f"CloudScraper: {cloudscraper}")
        
        if selenium is not None:
            self.selenium_count = selenium
            self.selenium_indicator.configure(text=f"Selenium: {selenium}")
    
    def set_complete(self):
        """Установка состояния завершения"""
        self.main_progress.set(1.0)
        self.progress_label.configure(text="100%")
        self.current_action.configure(text="Скрейпинг завершен")
    
    def reset(self):
        """Сброс прогресса"""
        self.main_progress.set(0)
        self.progress_label.configure(text="0%")
        self.current_action.configure(text="Готов к работе")
        self.success_count = 0
        self.error_count = 0
        self.total_count = 0
        self.cloudscraper_count = 0
        self.selenium_count = 0
        self.update_counters(0, 0, 0, 0, 0)

class LogFrame(ModernFrame):
    """Панель логов с фильтрацией"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Логи выполнения")
        
        # Панель управления логами
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по уровню
        self.level_var = ctk.StringVar(value="Все")
        self.level_combo = ctk.CTkComboBox(
            self.controls_frame,
            values=["Все", "INFO", "WARNING", "ERROR", "DEBUG"],
            variable=self.level_var,
            command=self._filter_logs,
            width=100
        )
        self.level_combo.pack(side="left", padx=5)
        
        # Автопрокрутка
        self.autoscroll_var = ctk.BooleanVar(value=True)
        self.autoscroll_check = ctk.CTkCheckBox(
            self.controls_frame,
            text="Автопрокрутка",
            variable=self.autoscroll_var
        )
        self.autoscroll_check.pack(side="left", padx=10)
        
        # Кнопка очистки
        self.clear_btn = ctk.CTkButton(
            self.controls_frame,
            text="Очистить",
            command=self.clear_logs,
            width=80, height=25
        )
        self.clear_btn.pack(side="right", padx=5)
        
        # Текстовое поле логов
        self.log_text = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, height=15,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Цвета для разных уровней логов
        self.log_text.tag_config("INFO", foreground="black")
        self.log_text.tag_config("WARNING", foreground="orange")
        self.log_text.tag_config("ERROR", foreground="red")
        self.log_text.tag_config("DEBUG", foreground="gray")
        
        # Список всех логов для фильтрации
        self.all_logs = []
        
        # Блокировка для потокобезопасности
        self.log_lock = threading.Lock()
    
    def add_log(self, message: str, level: str = "INFO"):
        """Добавление лога"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "message": message
        }
        
        with self.log_lock:
            self.all_logs.append(log_entry)
        
        # Обновление в основном потоке
        self.after(0, lambda: self._update_log_display(log_entry))
    
    def _update_log_display(self, log_entry: Dict):
        """Обновление отображения логов"""
        # Проверка фильтра
        if not self._should_show_log(log_entry):
            return
        
        # Форматирование сообщения
        formatted_message = f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}\n"
        
        # Добавление в текстовое поле
        self.log_text.insert(tk.END, formatted_message, log_entry['level'])
        
        # Автопрокрутка
        if self.autoscroll_var.get():
            self.log_text.see(tk.END)
        
        # Ограничение количества строк
        self._limit_log_lines()
    
    def _should_show_log(self, log_entry: Dict) -> bool:
        """Проверка, должен ли лог отображаться"""
        filter_level = self.level_var.get()
        if filter_level == "Все":
            return True
        return log_entry['level'] == filter_level
    
    def _filter_logs(self, selected_level: str):
        """Фильтрация логов по уровню"""
        self.log_text.delete(1.0, tk.END)
        
        with self.log_lock:
            for log_entry in self.all_logs:
                if self._should_show_log(log_entry):
                    formatted_message = f"[{log_entry['timestamp']}] {log_entry['level']}: {log_entry['message']}\n"
                    self.log_text.insert(tk.END, formatted_message, log_entry['level'])
        
        if self.autoscroll_var.get():
            self.log_text.see(tk.END)
    
    def _limit_log_lines(self, max_lines: int = 1000):
        """Ограничение количества строк в логах"""
        lines = self.log_text.get(1.0, tk.END).split('\n')
        if len(lines) > max_lines:
            # Удаление старых строк
            lines_to_remove = len(lines) - max_lines
            for _ in range(lines_to_remove):
                self.log_text.delete(1.0, "2.0")
    
    def clear_logs(self):
        """Очистка логов"""
        with self.log_lock:
            self.all_logs.clear()
        self.log_text.delete(1.0, tk.END)

class ResultsFrame(ModernFrame):
    """Панель результатов с таблицей"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Результаты скрейпинга")
        
        # Панель управления
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по статусу
        self.status_var = ctk.StringVar(value="Все")
        self.status_combo = ctk.CTkComboBox(
            self.controls_frame,
            values=["Все", "Успешно", "Ошибка"],
            variable=self.status_var,
            command=self._filter_results,
            width=100
        )
        self.status_combo.pack(side="left", padx=5)
        
        # Информация о результатах
        self.info_label = ctk.CTkLabel(
            self.controls_frame,
            text="Результаты: 0",
            font=ctk.CTkFont(size=11)
        )
        self.info_label.pack(side="left", padx=10)
        
        # Кнопка экспорта
        self.export_btn = ctk.CTkButton(
            self.controls_frame,
            text="Экспорт",
            width=80, height=25
        )
        self.export_btn.pack(side="right", padx=5)
        
        # Таблица результатов
        self._create_results_table()
        
        # Данные
        self.results_data = []
    
    def _create_results_table(self):
        """Создание таблицы результатов"""
        # Контейнер для таблицы
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Стиль таблицы
        style = ttk.Style()
        style.theme_use("clam")
        
        # Столбцы таблицы
        columns = ("ID", "Сайт", "Название", "Цена", "Статус", "Метод", "Время")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Настройка столбцов
        self.tree.heading("ID", text="ID товара")
        self.tree.heading("Сайт", text="Сайт")
        self.tree.heading("Название", text="Название товара")
        self.tree.heading("Цена", text="Цена")
        self.tree.heading("Статус", text="Статус")
        self.tree.heading("Метод", text="Метод")
        self.tree.heading("Время", text="Время (сек)")
        
        # Ширина столбцов
        self.tree.column("ID", width=80, minwidth=60)
        self.tree.column("Сайт", width=80, minwidth=60)
        self.tree.column("Название", width=300, minwidth=200)
        self.tree.column("Цена", width=100, minwidth=80)
        self.tree.column("Статус", width=100, minwidth=80)
        self.tree.column("Метод", width=120, minwidth=100)
        self.tree.column("Время", width=80, minwidth=60)
        
        # Скроллбары
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Размещение
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Контекстное меню
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Создание контекстного меню"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Копировать URL", command=self._copy_url)
        self.context_menu.add_command(label="Копировать название", command=self._copy_name)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Показать детали", command=self._show_details)
        
        # Привязка к правой кнопке мыши
        self.tree.bind("<Button-3>", self._show_context_menu)
    
    def _show_context_menu(self, event):
        """Показ контекстного меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _copy_url(self):
        """Копирование URL"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            # Получение данных из результатов
            # Реализация копирования в буфер обмена
            pass
    
    def _copy_name(self):
        """Копирование названия"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if len(values) > 2:
                # Копирование названия в буфер обмена
                self.clipboard_clear()
                self.clipboard_append(values[2])
    
    def _show_details(self):
        """Показ детальной информации"""
        selection = self.tree.selection()
        if selection:
            # Показать диалог с подробной информацией
            pass
    
    def update_results(self, results: List[ScrapingResult]):
        """Обновление таблицы результатов"""
        self.results_data = results
        self._refresh_table()
        
        # Обновление информации
        total_count = len(results)
        success_count = sum(1 for r in results if r.status == ScrapingStatus.SUCCESS)
        self.info_label.configure(text=f"Результаты: {total_count} (успешно: {success_count})")
    
    def _refresh_table(self):
        """Обновление отображения таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтрация результатов
        filtered_results = self._get_filtered_results()
        
        # Добавление данных
        for result in filtered_results:
            if result.product:
                product = result.product
                values = (
                    product.id,
                    product.site,
                    product.name[:50] + "..." if len(product.name) > 50 else product.name,
                    f"{product.price:.2f} ₴" if product.price else "N/A",
                    "Успешно" if result.status == ScrapingStatus.SUCCESS else "Ошибка",
                    result.method_used.value if result.method_used else "N/A",
                    f"{result.response_time:.2f}"
                )
                
                item = self.tree.insert("", "end", values=values)
                
                # Цвет строки в зависимости от статуса
                if result.status == ScrapingStatus.SUCCESS:
                    self.tree.set(item, "Статус", "✓ Успешно")
                else:
                    self.tree.set(item, "Статус", "✗ Ошибка")
    
    def _get_filtered_results(self) -> List[ScrapingResult]:
        """Получение отфильтрованных результатов"""
        filter_status = self.status_var.get()
        
        if filter_status == "Все":
            return self.results_data
        elif filter_status == "Успешно":
            return [r for r in self.results_data if r.status == ScrapingStatus.SUCCESS]
        elif filter_status == "Ошибка":
            return [r for r in self.results_data if r.status != ScrapingStatus.SUCCESS]
        
        return self.results_data
    
    def _filter_results(self, selected_status: str):
        """Фильтрация результатов"""
        self._refresh_table()
    
    def clear_results(self):
        """Очистка результатов"""
        self.results_data.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.info_label.configure(text="Результаты: 0")

class SettingsFrame(ModernFrame):
    """Панель настроек скрейпинга"""
    
    def __init__(self, parent):
        super().__init__(parent, title="Настройки скрейпинга")
        
        # Основной контейнер с двумя колонками
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Левая колонка - настройки
        self.left_frame = ctk.CTkFrame(self.content_frame)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Правая колонка - список товаров
        self.right_frame = ctk.CTkFrame(self.content_frame)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self._create_settings_widgets()
        self._create_products_widgets()
    
    def _create_settings_widgets(self):
        """Создание виджетов настроек"""
        # Заголовок
        title_label = ctk.CTkLabel(
            self.left_frame, text="Параметры скрейпинга",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Метод скрейпинга
        method_frame = ctk.CTkFrame(self.left_frame)
        method_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(method_frame, text="Метод скрейпинга:").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.method_var = ctk.StringVar(value="cloudscraper")
        self.method_combo = ctk.CTkComboBox(
            method_frame,
            values=["cloudscraper", "selenium", "hybrid"],
            variable=self.method_var,
            command=self._on_method_change
        )
        self.method_combo.pack(padx=10, pady=(0, 10), fill="x")
        
        # Настройки fallback
        self.fallback_var = ctk.BooleanVar(value=True)
        self.fallback_check = ctk.CTkCheckBox(
            self.left_frame,
            text="Использовать Selenium fallback",
            variable=self.fallback_var
        )
        self.fallback_check.pack(padx=10, pady=5, anchor="w")
        
        # Headless режим
        self.headless_var = ctk.BooleanVar(value=True)
        self.headless_check = ctk.CTkCheckBox(
            self.left_frame,
            text="Headless режим (без GUI браузера)",
            variable=self.headless_var
        )
        self.headless_check.pack(padx=10, pady=5, anchor="w")
        
        # Количество потоков
        threads_frame = ctk.CTkFrame(self.left_frame)
        threads_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(threads_frame, text="Максимум потоков:").pack(anchor="w", padx=10, pady=(10, 5))
        
        self.threads_var = ctk.IntVar(value=3)
        self.threads_spinbox = ctk.CTkSlider(
            threads_frame,
            from_=1, to=10,
            number_of_steps=9,
            variable=self.threads_var
        )
        self.threads_spinbox.pack(padx=10, pady=(0, 5), fill="x")
        
        self.threads_label = ctk.CTkLabel(threads_frame, text="3")
        self.threads_label.pack(padx=10, pady=(0, 10))
        
        # Привязка обновления метки
        self.threads_spinbox.configure(command=self._update_threads_label)
        
        # Задержки
        delay_frame = ctk.CTkFrame(self.left_frame)
        delay_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(delay_frame, text="Задержка между запросами (сек):").pack(anchor="w", padx=10, pady=(10, 5))
        
        delay_inner_frame = ctk.CTkFrame(delay_frame)
        delay_inner_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(delay_inner_frame, text="От:").pack(side="left", padx=(10, 5))
        self.delay_min_var = ctk.DoubleVar(value=1.0)
        self.delay_min_entry = ctk.CTkEntry(delay_inner_frame, textvariable=self.delay_min_var, width=60)
        self.delay_min_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(delay_inner_frame, text="До:").pack(side="left", padx=(10, 5))
        self.delay_max_var = ctk.DoubleVar(value=3.0)
        self.delay_max_entry = ctk.CTkEntry(delay_inner_frame, textvariable=self.delay_max_var, width=60)
        self.delay_max_entry.pack(side="left", padx=5)
    
    def _create_products_widgets(self):
        """Создание виджетов списка товаров"""
        # Заголовок
        title_label = ctk.CTkLabel(
            self.right_frame, text="Список товаров",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=10)
        
        # Панель управления
        controls_frame = ctk.CTkFrame(self.right_frame)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Кнопки
        self.add_btn = ctk.CTkButton(
            controls_frame, text="Добавить",
            command=self._add_product,
            width=80, height=25
        )
        self.add_btn.pack(side="left", padx=5, pady=5)
        
        self.remove_btn = ctk.CTkButton(
            controls_frame, text="Удалить",
            command=self._remove_product,
            width=80, height=25
        )
        self.remove_btn.pack(side="left", padx=5, pady=5)
        
        self.clear_btn = ctk.CTkButton(
            controls_frame, text="Очистить",
            command=self._clear_products,
            width=80, height=25
        )
        self.clear_btn.pack(side="left", padx=5, pady=5)
        
        # Счетчик товаров
        self.count_label = ctk.CTkLabel(
            controls_frame, text="Товаров: 0",
            font=ctk.CTkFont(size=11)
        )
        self.count_label.pack(side="right", padx=10, pady=5)
        
        # Текстовое поле для списка товаров
        self.products_text = scrolledtext.ScrolledText(
            self.right_frame, height=10,
            font=("Consolas", 10)
        )
        self.products_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Подсказка
        hint_label = ctk.CTkLabel(
            self.right_frame, 
            text="Формат: ID_товара,сайт (например: 123456,rozetka)",
            font=ctk.CTkFont(size=9)
        )
        hint_label.pack(padx=10, pady=(0, 10))
        
        # Привязка обновления счетчика
        self.products_text.bind('<KeyRelease>', self._update_products_count)
    
    def _on_method_change(self, value):
        """Обработка изменения метода скрейпинга"""
        if value == "selenium":
            self.fallback_check.configure(state="disabled")
        else:
            self.fallback_check.configure(state="normal")
    
    def _update_threads_label(self, value):
        """Обновление метки количества потоков"""
        self.threads_label.configure(text=str(int(value)))
    
    def _add_product(self):
        """Добавление товара"""
        # Простой диалог для добавления товара
        dialog = ctk.CTkInputDialog(
            text="Введите ID товара и сайт через запятую:",
            title="Добавить товар"
        )
        result = dialog.get_input()
        
        if result and ',' in result:
            self.products_text.insert(tk.END, result + '\n')
            self._update_products_count()
    
    def _remove_product(self):
        """Удаление выбранного товара"""
        try:
            # Получение текущей позиции курсора
            current_line = self.products_text.index(tk.INSERT).split('.')[0]
            line_start = f"{current_line}.0"
            line_end = f"{current_line}.end+1c"
            self.products_text.delete(line_start, line_end)
            self._update_products_count()
        except:
            pass
    
    def _clear_products(self):
        """Очистка списка товаров"""
        self.products_text.delete(1.0, tk.END)
        self._update_products_count()
    
    def _update_products_count(self, event=None):
        """Обновление счетчика товаров"""
        content = self.products_text.get(1.0, tk.END).strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        valid_lines = [line for line in lines if ',' in line]
        
        self.count_label.configure(text=f"Товаров: {len(valid_lines)}")
    
    def get_settings(self) -> Dict:
        """Получение текущих настроек"""
        method_map = {
            "cloudscraper": ScrapingMethod.CLOUDSCRAPER,
            "selenium": ScrapingMethod.SELENIUM,
            "hybrid": ScrapingMethod.HYBRID
        }
        
        return {
            "method": method_map.get(self.method_var.get(), ScrapingMethod.CLOUDSCRAPER),
            "use_fallback": self.fallback_var.get(),
            "headless": self.headless_var.get(),
            "max_workers": int(self.threads_var.get()),
            "delay_min": self.delay_min_var.get(),
            "delay_max": self.delay_max_var.get()
        }
    
    def get_products_list(self) -> List[Tuple[str, str]]:
        """Получение списка товаров"""
        content = self.products_text.get(1.0, tk.END).strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        products = []
        for line in lines:
            if ',' in line:
                parts = line.split(',', 1)
                if len(parts) == 2:
                    product_id = parts[0].strip()
                    site = parts[1].strip()
                    if product_id and site:
                        products.append((product_id, site))
        
        return products
    
    def set_products_list(self, products: List[Tuple[str, str]]):
        """Установка списка товаров"""
        self.products_text.delete(1.0, tk.END)
        
        for product_id, site in products:
            self.products_text.insert(tk.END, f"{product_id},{site}\n")
        
        self._update_products_count()
    
    def load_settings(self, config):
        """Загрузка настроек из конфигурации"""
        try:
            # Метод скрейпинга
            method = config.get('scraping', 'method', 'cloudscraper')
            self.method_var.set(method)
            
            # Fallback
            use_fallback = config.getboolean('scraping', 'use_fallback', True)
            self.fallback_var.set(use_fallback)
            
            # Headless
            headless = config.getboolean('scraping', 'headless', True)
            self.headless_var.set(headless)
            
            # Потоки
            max_workers = config.getint('scraping', 'max_workers', 3)
            self.threads_var.set(max_workers)
            self._update_threads_label(max_workers)
            
            # Задержки
            delay_min = config.getfloat('scraping', 'delay_min', 1.0)
            delay_max = config.getfloat('scraping', 'delay_max', 3.0)
            self.delay_min_var.set(delay_min)
            self.delay_max_var.set(delay_max)
            
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self, config):
        """Сохранение настроек в конфигурацию"""
        try:
            # Секция scraping
            if not config.has_section('scraping'):
                config.add_section('scraping')
            
            config.set('scraping', 'method', self.method_var.get())
            config.set('scraping', 'use_fallback', str(self.fallback_var.get()))
            config.set('scraping', 'headless', str(self.headless_var.get()))
            config.set('scraping', 'max_workers', str(int(self.threads_var.get())))
            config.set('scraping', 'delay_min', str(self.delay_min_var.get()))
            config.set('scraping', 'delay_max', str(self.delay_max_var.get()))
            
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
