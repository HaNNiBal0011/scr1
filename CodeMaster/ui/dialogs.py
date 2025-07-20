"""
Диалоговые окна для настроек, экспорта и информации
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from typing import Dict, Optional, List
import json
import csv
from datetime import datetime

class SettingsDialog(ctk.CTkToplevel):
    """Диалог настроек приложения"""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.result = None
        
        # Настройка окна
        self.title("Настройки приложения")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Модальность
        self.transient(parent)
        self.grab_set()
        
        # Центрирование относительно родительского окна
        self._center_window()
        
        # Создание интерфейса
        self._create_widgets()
        self._load_current_settings()
        
        # Фокус на диалоге
        self.focus()
    
    def _center_window(self):
        """Центрирование окна"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width - 600) // 2
        y = parent_y + (parent_height - 500) // 2
        
        self.geometry(f"600x500+{x}+{y}")
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной контейнер
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Вкладки
        self.tabview = ctk.CTkTabview(main_frame)
        self.tabview.pack(fill="both", expand=True)
        
        # Вкладка "Внешний вид"
        self.tabview.add("Внешний вид")
        self._create_appearance_tab()
        
        # Вкладка "Скрейпинг"
        self.tabview.add("Скрейпинг")
        self._create_scraping_tab()
        
        # Вкладка "Сеть"
        self.tabview.add("Сеть")
        self._create_network_tab()
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.cancel_btn = ctk.CTkButton(
            buttons_frame, text="Отмена",
            command=self._on_cancel,
            width=100
        )
        self.cancel_btn.pack(side="right", padx=(5, 0))
        
        self.ok_btn = ctk.CTkButton(
            buttons_frame, text="OK",
            command=self._on_ok,
            width=100
        )
        self.ok_btn.pack(side="right")
        
        self.apply_btn = ctk.CTkButton(
            buttons_frame, text="Применить",
            command=self._on_apply,
            width=100
        )
        self.apply_btn.pack(side="right", padx=(0, 5))
    
    def _create_appearance_tab(self):
        """Создание вкладки внешнего вида"""
        tab = self.tabview.tab("Внешний вид")
        
        # Тема
        theme_frame = ctk.CTkFrame(tab)
        theme_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(theme_frame, text="Тема приложения:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.theme_var = ctk.StringVar()
        self.theme_combo = ctk.CTkComboBox(
            theme_frame,
            values=["system", "light", "dark"],
            variable=self.theme_var
        )
        self.theme_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Цветовая схема
        color_frame = ctk.CTkFrame(tab)
        color_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(color_frame, text="Цветовая схема:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.color_var = ctk.StringVar()
        self.color_combo = ctk.CTkComboBox(
            color_frame,
            values=["blue", "dark-blue", "green"],
            variable=self.color_var
        )
        self.color_combo.pack(fill="x", padx=10, pady=(0, 10))
        
        # Масштабирование UI
        scale_frame = ctk.CTkFrame(tab)
        scale_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(scale_frame, text="Масштабирование интерфейса:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.scale_var = ctk.DoubleVar()
        self.scale_slider = ctk.CTkSlider(
            scale_frame,
            from_=0.8, to=1.4,
            variable=self.scale_var,
            number_of_steps=6
        )
        self.scale_slider.pack(fill="x", padx=10, pady=5)
        
        self.scale_label = ctk.CTkLabel(scale_frame, text="100%")
        self.scale_label.pack(padx=10, pady=(0, 10))
        
        # Привязка обновления метки
        self.scale_slider.configure(command=self._update_scale_label)
    
    def _create_scraping_tab(self):
        """Создание вкладки скрейпинга"""
        tab = self.tabview.tab("Скрейпинг")
        
        # Таймауты
        timeout_frame = ctk.CTkFrame(tab)
        timeout_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(timeout_frame, text="Таймауты (секунды):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Таймаут страницы
        page_timeout_frame = ctk.CTkFrame(timeout_frame)
        page_timeout_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(page_timeout_frame, text="Загрузка страницы:").pack(side="left", padx=10)
        self.page_timeout_var = ctk.IntVar()
        self.page_timeout_entry = ctk.CTkEntry(page_timeout_frame, textvariable=self.page_timeout_var, width=80)
        self.page_timeout_entry.pack(side="right", padx=10)
        
        # Таймаут элемента
        element_timeout_frame = ctk.CTkFrame(timeout_frame)
        element_timeout_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(element_timeout_frame, text="Ожидание элемента:").pack(side="left", padx=10)
        self.element_timeout_var = ctk.IntVar()
        self.element_timeout_entry = ctk.CTkEntry(element_timeout_frame, textvariable=self.element_timeout_var, width=80)
        self.element_timeout_entry.pack(side="right", padx=10)
        
        # Повторы
        retry_frame = ctk.CTkFrame(tab)
        retry_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(retry_frame, text="Количество повторов:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.retry_var = ctk.IntVar()
        self.retry_slider = ctk.CTkSlider(
            retry_frame,
            from_=1, to=10,
            variable=self.retry_var,
            number_of_steps=9
        )
        self.retry_slider.pack(fill="x", padx=10, pady=5)
        
        self.retry_label = ctk.CTkLabel(retry_frame, text="3")
        self.retry_label.pack(padx=10, pady=(0, 10))
        
        self.retry_slider.configure(command=self._update_retry_label)
        
        # Опции Chrome
        chrome_frame = ctk.CTkFrame(tab)
        chrome_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(chrome_frame, text="Настройки Chrome:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.disable_images_var = ctk.BooleanVar()
        self.disable_images_check = ctk.CTkCheckBox(
            chrome_frame,
            text="Отключить загрузку изображений",
            variable=self.disable_images_var
        )
        self.disable_images_check.pack(anchor="w", padx=10, pady=5)
        
        self.disable_javascript_var = ctk.BooleanVar()
        self.disable_javascript_check = ctk.CTkCheckBox(
            chrome_frame,
            text="Отключить JavaScript (не рекомендуется)",
            variable=self.disable_javascript_var
        )
        self.disable_javascript_check.pack(anchor="w", padx=10, pady=(5, 10))
    
    def _create_network_tab(self):
        """Создание вкладки сети"""
        tab = self.tabview.tab("Сеть")
        
        # User Agent
        ua_frame = ctk.CTkFrame(tab)
        ua_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ua_frame, text="User Agent:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.user_agent_var = ctk.StringVar()
        self.user_agent_entry = ctk.CTkEntry(ua_frame, textvariable=self.user_agent_var)
        self.user_agent_entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # Прокси
        proxy_frame = ctk.CTkFrame(tab)
        proxy_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(proxy_frame, text="Прокси настройки:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.use_proxy_var = ctk.BooleanVar()
        self.use_proxy_check = ctk.CTkCheckBox(
            proxy_frame,
            text="Использовать прокси",
            variable=self.use_proxy_var,
            command=self._toggle_proxy
        )
        self.use_proxy_check.pack(anchor="w", padx=10, pady=5)
        
        # Поля прокси
        self.proxy_frame = ctk.CTkFrame(proxy_frame)
        self.proxy_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        proxy_host_frame = ctk.CTkFrame(self.proxy_frame)
        proxy_host_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(proxy_host_frame, text="Хост:").pack(side="left", padx=10)
        self.proxy_host_var = ctk.StringVar()
        self.proxy_host_entry = ctk.CTkEntry(proxy_host_frame, textvariable=self.proxy_host_var)
        self.proxy_host_entry.pack(side="right", padx=10, fill="x", expand=True)
        
        proxy_port_frame = ctk.CTkFrame(self.proxy_frame)
        proxy_port_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkLabel(proxy_port_frame, text="Порт:").pack(side="left", padx=10)
        self.proxy_port_var = ctk.StringVar()
        self.proxy_port_entry = ctk.CTkEntry(proxy_port_frame, textvariable=self.proxy_port_var, width=80)
        self.proxy_port_entry.pack(side="right", padx=10)
        
        # Изначально прокси отключен
        self._toggle_proxy()
    
    def _update_scale_label(self, value):
        """Обновление метки масштабирования"""
        scale_percent = int(value * 100)
        self.scale_label.configure(text=f"{scale_percent}%")
    
    def _update_retry_label(self, value):
        """Обновление метки повторов"""
        self.retry_label.configure(text=str(int(value)))
    
    def _toggle_proxy(self):
        """Переключение доступности настроек прокси"""
        if self.use_proxy_var.get():
            for widget in self.proxy_frame.winfo_children():
                for child in widget.winfo_children():
                    if hasattr(child, 'configure'):
                        child.configure(state="normal")
        else:
            for widget in self.proxy_frame.winfo_children():
                for child in widget.winfo_children():
                    if hasattr(child, 'configure') and not isinstance(child, ctk.CTkLabel):
                        child.configure(state="disabled")
    
    def _load_current_settings(self):
        """Загрузка текущих настроек"""
        # Внешний вид
        self.theme_var.set(self.config.get('appearance', 'theme', 'system'))
        self.color_var.set(self.config.get('appearance', 'color_theme', 'blue'))
        scale = self.config.getfloat('appearance', 'ui_scale', 1.0)
        self.scale_var.set(scale)
        self._update_scale_label(scale)
        
        # Скрейпинг
        self.page_timeout_var.set(self.config.getint('scraping', 'page_timeout', 30))
        self.element_timeout_var.set(self.config.getint('scraping', 'element_timeout', 10))
        retry_count = self.config.getint('scraping', 'max_retries', 3)
        self.retry_var.set(retry_count)
        self._update_retry_label(retry_count)
        
        self.disable_images_var.set(self.config.getboolean('scraping', 'disable_images', True))
        self.disable_javascript_var.set(self.config.getboolean('scraping', 'disable_javascript', False))
        
        # Сеть
        default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.user_agent_var.set(self.config.get('network', 'user_agent', default_ua))
        
        self.use_proxy_var.set(self.config.getboolean('network', 'use_proxy', False))
        self.proxy_host_var.set(self.config.get('network', 'proxy_host', ''))
        self.proxy_port_var.set(self.config.get('network', 'proxy_port', ''))
        
        self._toggle_proxy()
    
    def _get_settings(self) -> Dict:
        """Получение настроек из формы"""
        return {
            'appearance': {
                'theme': self.theme_var.get(),
                'color_theme': self.color_var.get(),
                'ui_scale': self.scale_var.get()
            },
            'scraping': {
                'page_timeout': self.page_timeout_var.get(),
                'element_timeout': self.element_timeout_var.get(),
                'max_retries': int(self.retry_var.get()),
                'disable_images': self.disable_images_var.get(),
                'disable_javascript': self.disable_javascript_var.get()
            },
            'network': {
                'user_agent': self.user_agent_var.get(),
                'use_proxy': self.use_proxy_var.get(),
                'proxy_host': self.proxy_host_var.get(),
                'proxy_port': self.proxy_port_var.get()
            }
        }
    
    def _on_ok(self):
        """Обработка нажатия OK"""
        self.result = self._get_settings()
        self.destroy()
    
    def _on_apply(self):
        """Обработка нажатия Применить"""
        self.result = self._get_settings()
        # Не закрываем диалог, применяем настройки
        
    def _on_cancel(self):
        """Обработка нажатия Отмена"""
        self.result = None
        self.destroy()

class ExportDialog(ctk.CTkToplevel):
    """Диалог экспорта результатов"""
    
    def __init__(self, parent, export_type="General"):
        super().__init__(parent)
        self.result = None
        self.export_type = export_type
        
        # Настройка окна
        self.title(f"Экспорт результатов - {export_type}")
        self.geometry("500x400")
        self.resizable(False, False)
        
        # Модальность
        self.transient(parent)
        self.grab_set()
        
        # Центрирование
        self._center_window()
        
        # Создание интерфейса
        self._create_widgets()
        
        # Фокус
        self.focus()
    
    def _center_window(self):
        """Центрирование окна"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 400) // 2
        
        self.geometry(f"500x400+{x}+{y}")
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной контейнер
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Выберите параметры экспорта",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Формат файла
        format_frame = ctk.CTkFrame(main_frame)
        format_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(format_frame, text="Формат файла:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.format_var = ctk.StringVar(value="CSV")
        
        csv_radio = ctk.CTkRadioButton(format_frame, text="CSV (Excel)", variable=self.format_var, value="CSV")
        csv_radio.pack(anchor="w", padx=10, pady=2)
        
        json_radio = ctk.CTkRadioButton(format_frame, text="JSON", variable=self.format_var, value="JSON")
        json_radio.pack(anchor="w", padx=10, pady=2)
        
        xlsx_radio = ctk.CTkRadioButton(format_frame, text="Excel (XLSX)", variable=self.format_var, value="XLSX")
        xlsx_radio.pack(anchor="w", padx=10, pady=(2, 10))
        
        # Поля для экспорта
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(fields_frame, text="Поля для экспорта:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Чекбоксы полей
        self.fields = {
            'id': ctk.BooleanVar(value=True),
            'site': ctk.BooleanVar(value=True),
            'name': ctk.BooleanVar(value=True),
            'price': ctk.BooleanVar(value=True),
            'old_price': ctk.BooleanVar(value=False),
            'availability': ctk.BooleanVar(value=True),
            'url': ctk.BooleanVar(value=False),
            'image_url': ctk.BooleanVar(value=False),
            'description': ctk.BooleanVar(value=False),
            'method_used': ctk.BooleanVar(value=True),
            'response_time': ctk.BooleanVar(value=False),
            'status': ctk.BooleanVar(value=True)
        }
        
        field_names = {
            'id': 'ID товара',
            'site': 'Сайт',
            'name': 'Название',
            'price': 'Цена',
            'old_price': 'Старая цена',
            'availability': 'Наличие',
            'url': 'URL товара',
            'image_url': 'URL изображения',
            'description': 'Описание',
            'method_used': 'Метод скрейпинга',
            'response_time': 'Время ответа',
            'status': 'Статус'
        }
        
        # Две колонки чекбоксов
        checkboxes_frame = ctk.CTkFrame(fields_frame)
        checkboxes_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        left_frame = ctk.CTkFrame(checkboxes_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(5, 2.5))
        
        right_frame = ctk.CTkFrame(checkboxes_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(2.5, 5))
        
        # Размещение чекбоксов
        field_items = list(self.fields.items())
        mid_point = len(field_items) // 2
        
        for i, (field, var) in enumerate(field_items):
            parent_frame = left_frame if i < mid_point else right_frame
            
            checkbox = ctk.CTkCheckBox(
                parent_frame,
                text=field_names[field],
                variable=var
            )
            checkbox.pack(anchor="w", padx=10, pady=2)
        
        # Дополнительные опции
        options_frame = ctk.CTkFrame(fields_frame)
        options_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.include_headers_var = ctk.BooleanVar(value=True)
        headers_check = ctk.CTkCheckBox(
            options_frame,
            text="Включить заголовки столбцов",
            variable=self.include_headers_var
        )
        headers_check.pack(anchor="w", padx=10, pady=5)
        
        self.success_only_var = ctk.BooleanVar(value=False)
        success_check = ctk.CTkCheckBox(
            options_frame,
            text="Только успешные результаты",
            variable=self.success_only_var
        )
        success_check.pack(anchor="w", padx=10, pady=5)
        
        # Кнопки
        buttons_frame = ctk.CTkFrame(self)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.cancel_btn = ctk.CTkButton(
            buttons_frame, text="Отмена",
            command=self._on_cancel,
            width=100
        )
        self.cancel_btn.pack(side="right", padx=(5, 0))
        
        self.export_btn = ctk.CTkButton(
            buttons_frame, text="Экспорт",
            command=self._on_export,
            width=100
        )
        self.export_btn.pack(side="right")
    
    def _on_export(self):
        """Обработка нажатия Экспорт"""
        # Проверка выбранных полей
        selected_fields = [field for field, var in self.fields.items() if var.get()]
        
        if not selected_fields:
            messagebox.showwarning("Предупреждение", "Выберите хотя бы одно поле для экспорта!")
            return
        
        # Выбор файла
        format_type = self.format_var.get()
        
        if format_type == "CSV":
            file_path = filedialog.asksaveasfilename(
                title="Сохранить CSV файл",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        elif format_type == "JSON":
            file_path = filedialog.asksaveasfilename(
                title="Сохранить JSON файл",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
        else:  # XLSX
            file_path = filedialog.asksaveasfilename(
                title="Сохранить Excel файл",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
        
        if file_path:
            self.result = {
                'file_path': file_path,
                'format': format_type,
                'fields': selected_fields,
                'include_headers': self.include_headers_var.get(),
                'success_only': self.success_only_var.get()
            }
            self.destroy()
    
    def _on_cancel(self):
        """Обработка нажатия Отмена"""
        self.result = None
        self.destroy()

class AboutDialog(ctk.CTkToplevel):
    """Диалог "О программе" """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Настройка окна
        self.title("О программе")
        self.geometry("500x600")
        self.resizable(False, False)
        
        # Модальность
        self.transient(parent)
        self.grab_set()
        
        # Центрирование
        self._center_window()
        
        # Создание интерфейса
        self._create_widgets()
        
        # Фокус
        self.focus()
    
    def _center_window(self):
        """Центрирование окна"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 600) // 2
        
        self.geometry(f"500x600+{x}+{y}")
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной контейнер
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Логотип (текстовый)
        logo_frame = ctk.CTkFrame(main_frame)
        logo_frame.pack(fill="x", padx=10, pady=10)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="🛒 Product Scraper Pro",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        logo_label.pack(pady=20)
        
        # Версия
        version_label = ctk.CTkLabel(
            main_frame,
            text="Версия 2.0.0",
            font=ctk.CTkFont(size=14)
        )
        version_label.pack(pady=5)
        
        # Описание
        description_frame = ctk.CTkFrame(main_frame)
        description_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        description_text = """
Модернизированный парсер товаров с поддержкой JavaScript и улучшенным пользовательским интерфейсом.

Основные возможности:
• Гибридный парсинг: CloudScraper + Selenium
• Поддержка современных сайтов с защитой
• Обход JavaScript и динамического контента
• Многопоточная обработка товаров
• Экспорт в CSV, JSON и Excel
• Настраиваемые темы интерфейса
• Детальное логирование процесса

Поддерживаемые сайты:
• Rozetka.com.ua
• Allo.ua
• Comfy.ua
• Epicentr.ua

Технологии:
• Python 3.8+
• CustomTkinter (современный UI)
• Selenium WebDriver
• CloudScraper
• BeautifulSoup4
• Undetected ChromeDriver
        """
        
        description_label = ctk.CTkLabel(
            description_frame,
            text=description_text,
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        description_label.pack(padx=15, pady=15, fill="both", expand=True)
        
        # Информация о разработчике
        dev_frame = ctk.CTkFrame(main_frame)
        dev_frame.pack(fill="x", padx=10, pady=10)
        
        dev_label = ctk.CTkLabel(
            dev_frame,
            text="Разработано с использованием современных технологий веб-скрейпинга\n© 2024",
            font=ctk.CTkFont(size=10)
        )
        dev_label.pack(pady=10)
        
        # Кнопка закрытия
        close_btn = ctk.CTkButton(
            main_frame,
            text="Закрыть",
            command=self.destroy,
            width=100
        )
        close_btn.pack(pady=(10, 0))

class ProgressDialog(ctk.CTkToplevel):
    """Диалог прогресса для длительных операций"""
    
    def __init__(self, parent, title="Выполнение операции"):
        super().__init__(parent)
        
        # Настройка окна
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        # Модальность
        self.transient(parent)
        self.grab_set()
        
        # Центрирование
        self._center_window()
        
        # Состояние
        self.cancelled = False
        
        # Создание интерфейса
        self._create_widgets()
        
        # Фокус
        self.focus()
    
    def _center_window(self):
        """Центрирование окна"""
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()
        
        x = parent_x + (parent_width - 400) // 2
        y = parent_y + (parent_height - 200) // 2
        
        self.geometry(f"400x200+{x}+{y}")
    
    def _create_widgets(self):
        """Создание виджетов"""
        # Основной контейнер
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Сообщение
        self.message_label = ctk.CTkLabel(
            main_frame,
            text="Инициализация...",
            font=ctk.CTkFont(size=12)
        )
        self.message_label.pack(pady=(20, 10))
        
        # Прогресс-бар
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=300)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)
        
        # Процент
        self.percent_label = ctk.CTkLabel(
            main_frame,
            text="0%",
            font=ctk.CTkFont(size=11)
        )
        self.percent_label.pack(pady=5)
        
        # Кнопка отмены
        self.cancel_btn = ctk.CTkButton(
            main_frame,
            text="Отмена",
            command=self._on_cancel,
            width=100
        )
        self.cancel_btn.pack(pady=(20, 0))
    
    def update_progress(self, progress: float, message: str = ""):
        """Обновление прогресса"""
        # Нормализация прогресса
        progress = max(0, min(100, progress))
        
        # Обновление прогресс-бара
        self.progress_bar.set(progress / 100)
        
        # Обновление процента
        self.percent_label.configure(text=f"{progress:.1f}%")
        
        # Обновление сообщения
        if message:
            self.message_label.configure(text=message)
        
        # Обновление интерфейса
        self.update()
    
    def _on_cancel(self):
        """Обработка отмены"""
        self.cancelled = True
        self.cancel_btn.configure(text="Отменяется...", state="disabled")
    
    def is_cancelled(self) -> bool:
        """Проверка отмены"""
        return self.cancelled
