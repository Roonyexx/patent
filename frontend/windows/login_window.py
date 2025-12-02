# frontend/windows/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from styles import Styles


class LoginWindow:
    """Окно входа в систему"""

    def __init__(self, api_client, on_success_callback):
        self.api_client = api_client
        self.on_success_callback = on_success_callback

        self.window = tk.Tk()
        self.window.title(f"{Config.APP_TITLE} - Вход")
        self.window.geometry(Config.LOGIN_WINDOW_SIZE)
        self.window.resizable(False, False)

        # Центрируем окно
        self.center_window()

        # Применяем стили (один раз для всего приложения)
        Styles.configure_styles()

        self.create_widgets()

    def center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        main_frame = ttk.Frame(self.window, padding="50")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        ttk.Label(
            main_frame,
            text=Config.APP_TITLE,
            style="Title.TLabel"
        ).pack(pady=(0, 20))

        ttk.Label(
            main_frame,
            text="Вход в систему",
            font=(Config.FONT_FAMILY, 14),
            foreground=Config.LIGHT_TEXT
        ).pack(pady=(0, 40))

        # Логин
        ttk.Label(main_frame, text="Логин:").pack(anchor="w", pady=(0, 5))
        self.username_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.username_var, width=35, font=(Config.FONT_FAMILY, 11)).pack(pady=(0, 15))

        # Пароль
        ttk.Label(main_frame, text="Пароль:").pack(anchor="w", pady=(0, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.password_var, show="•", width=35, font=(Config.FONT_FAMILY, 11)).pack(pady=(0, 25))

        # Кнопка Войти
        ttk.Button(
            main_frame,
            text="Войти",
            style="Success.TButton",
            command=self.login
        ).pack(fill=tk.X, pady=(10, 10))

        # Кнопка Регистрация
        ttk.Button(
            main_frame,
            text="Регистрация нового пользователя",
            style="Secondary.TButton",
            command=self.open_register
        ).pack(fill=tk.X, pady=(0, 30))

        # Подвал
        ttk.Label(
            main_frame,
            text=f"Версия {Config.APP_VERSION} © 2025",
            foreground=Config.LIGHT_TEXT,
            font=(Config.FONT_FAMILY, 8)
        ).pack(side=tk.BOTTOM, pady=20)

        # Enter = войти
        self.window.bind("<Return>", lambda e: self.login())
        self.username_var.set("")
        self.username_var.trace_add("write", lambda *args: self.username_var.set(self.username_var.get().strip()))

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showerror("Ошибка", "Введите логин и пароль")
            return

        try:
            self.api_client.login(username, password)
            self.window.destroy()
            self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Ошибка входа", str(e))

    def open_register(self):
        from windows.register_window import RegisterWindow
        self.window.destroy()
        RegisterWindow(self.api_client, self.on_success_callback).run()

    def run(self):
        self.window.mainloop()