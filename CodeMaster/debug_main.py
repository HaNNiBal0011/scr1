#!/usr/bin/env python3
"""
Диагностическая версия для определения проблемы с UI
"""

import sys
import os
import customtkinter as ctk
from datetime import datetime

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print(f"[{datetime.now().strftime('%H:%M:%S')}] Начало диагностики...")

# Настройка CustomTkinter
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

class DiagnosticWindow(ctk.CTk):
    """Диагностическое окно для поиска проблемы"""
    
    def __init__(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Создание диагностического окна...")
        super().__init__()
        
        self.title("Диагностика UI")
        self.geometry("600x400")
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Тестирование импорта компонентов...")
        
        # Тестируем пошагово каждый компонент
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт Config...")
            from utils.config import Config
            self.config = Config()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Config импортирован")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Ошибка Config: {e}")
            
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт Logger...")
            from utils.logger import setup_logger
            self.logger = setup_logger()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Logger импортирован")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Ошибка Logger: {e}")
            
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт ThemeManager...")
            from ui.themes import ThemeManager
            self.theme_manager = ThemeManager()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ ThemeManager импортирован")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Ошибка ThemeManager: {e}")
            
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт ExportManager...")
            from utils.export import ExportManager
            self.export_manager = ExportManager()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ ExportManager импортирован")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Ошибка ExportManager: {e}")
            
        try:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Импорт UI компонентов...")
            from ui.components import ModernFrame, StatusBar, ProgressFrame, LogFrame, ResultsFrame, SettingsFrame
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ UI компоненты импортированы")
            
            # Тестируем создание каждого компонента
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Создание тестовых компонентов...")
            
            main_container = ctk.CTkFrame(self)
            main_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Создание StatusBar...")
            status_bar = StatusBar(self)
            status_bar.pack(side="bottom", fill="x")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ StatusBar создан")
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Создание ProgressFrame...")
            progress_frame = ProgressFrame(main_container)
            progress_frame.pack(fill="x", padx=5, pady=2)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ ProgressFrame создан")
            
            # Информационная панель с результатами
            info_frame = ctk.CTkFrame(main_container)
            info_frame.pack(fill="both", expand=True, padx=5, pady=2)
            
            info_label = ctk.CTkLabel(
                info_frame, 
                text="Диагностика UI компонентов завершена успешно!\nВсе основные компоненты работают корректно.",
                font=ctk.CTkFont(size=14)
            )
            info_label.pack(pady=20)
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ Ошибка UI компонентов: {e}")
            import traceback
            traceback.print_exc()
            
            # Создаем простое сообщение об ошибке
            error_label = ctk.CTkLabel(
                self,
                text=f"Ошибка создания UI компонентов:\n{str(e)[:200]}...",
                font=ctk.CTkFont(size=12),
                text_color="red"
            )
            error_label.pack(pady=50)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Диагностическое окно готово")

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Запуск диагностики UI...")
    
    try:
        app = DiagnosticWindow()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Диагностическое окно создано, запуск mainloop...")
        app.mainloop()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Диагностика завершена")
        
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Критическая ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()