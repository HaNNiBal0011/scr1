#!/usr/bin/env python3
"""
Тест GUI приложения CustomTkinter
"""

import customtkinter as ctk
import os
print("Testing GUI libraries...")

try:
    print("Setting up CustomTkinter...")
    ctk.set_appearance_mode("system")
    ctk.set_default_color_theme("blue")
    
    print("Creating test window...")
    root = ctk.CTk()
    root.title("Test Window")
    root.geometry("400x300")
    
    label = ctk.CTkLabel(root, text="Тест GUI приложения")
    label.pack(pady=20)
    
    button = ctk.CTkButton(root, text="Тестовая кнопка")
    button.pack(pady=10)
    
    print("GUI test window created successfully!")
    print("Starting mainloop...")
    
    # Запуск на несколько секунд для тестирования
    root.after(3000, root.quit)
    root.mainloop()
    
    print("GUI test completed successfully!")

except Exception as e:
    print(f"GUI test failed: {e}")
    import traceback
    traceback.print_exc()