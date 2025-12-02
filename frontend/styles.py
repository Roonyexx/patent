# frontend/styles.py
import tkinter as tk
from tkinter import ttk
from config import Config


class Styles:
    """Класс для настройки стилей приложения"""

    @staticmethod
    def configure_styles():
        """Настроить стили ttk"""
        style = ttk.Style()
        
        # Основная тема (можно заменить на 'clam', 'alt', 'default', 'classic')
        style.theme_use('clam')

        # Цветовая схема
        primary = Config.PRIMARY_COLOR
        secondary = Config.SECONDARY_COLOR
        success = Config.SUCCESS_COLOR
        danger = Config.DANGER_COLOR
        warning = Config.WARNING_COLOR
        light_bg = Config.LIGHT_BG
        dark_text = Config.DARK_TEXT
        light_text = Config.LIGHT_TEXT

        # Настройки фона и текста
        style.configure(".", 
                        background=light_bg,
                        foreground=dark_text,
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))

        style.configure("TButton",
                        padding=10,
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"))

        style.configure("TLabel",
                        background=light_bg,
                        foreground=dark_text,
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))

        style.configure("Treeview",
                        background="white",
                        foreground=dark_text,
                        rowheight=25,
                        fieldbackground="white")

        style.configure("Treeview.Heading",
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
                        foreground=primary)

        style.map("Treeview",
                  background=[('selected', secondary)])

        # Заголовки
        style.configure("Title.TLabel",
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_TITLE, "bold"),
                        foreground=primary)

        style.configure("Subtitle.TLabel",
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_LARGE, "bold"),
                        foreground=dark_text)

        style.configure("Light.TLabel",
                        foreground=light_text,
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_SMALL))

        # Кнопки
        style.configure("Primary.TButton",
                        background=primary,
                        foreground="white")

        style.map("Primary.TButton",
                  background=[('active', secondary)])

        style.configure("Success.TButton",
                        background=success,
                        foreground="white")

        style.map("Success.TButton",
                  background=[('active', "#2ecc71")])

        style.configure("Danger.TButton",
                        background=danger,
                        foreground="white")

        style.map("Danger.TButton",
                  background=[('active', "#e74c3c")])

        style.configure("Secondary.TButton",
                        background=secondary,
                        foreground="white")

        style.map("Secondary.TButton",
                  background=[('active', "#2980b9")])

        # Для карточек в аналитике
        style.configure("Card.TLabelframe",
                        background="white",
                        relief="solid",
                        borderwidth=1)

        style.configure("Card.TLabelframe.Label",
                        font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, "bold"),
                        foreground=primary)