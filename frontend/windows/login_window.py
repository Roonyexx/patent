# frontend/windows/login_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from styles import Styles


class LoginWindow:
    def __init__(self, api_client, on_success_callback):
        self.api_client = api_client
        self.on_success_callback = on_success_callback

        self.window = tk.Tk()
        self.window.title(f"{Config.APP_TITLE} - Вход")
        self.window.geometry(Config.LOGIN_WINDOW_SIZE)
        self.window.resizable(False, False)

        Styles.configure_styles()
        self.center_window()
        self.create_widgets()

    def center_window(self):
        self.window.update_idletasks()
        w = self.window.winfo_width()
        h = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (w // 2)
        y = (self.window.winfo_screenheight() // 2) - (h // 2)
        self.window.geometry(f"{w}x{h}+{x}+{y}")

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding=50)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=Config.APP_TITLE, style="Title.TLabel").pack(pady=(0, 20))
        ttk.Label(frame, text="Вход в систему", font=(Config.FONT_FAMILY, 14)).pack(pady=(0, 40))

        # Username
        ttk.Label(frame, text="Логин:").pack(anchor="w")
        self.username_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.username_var, width=35).pack(pady=(0, 15))

        # Password
        ttk.Label(frame, text="Пароль:").pack(anchor="w")
        self.password_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.password_var, show="•", width=35).pack(pady=(0, 20))

        ttk.Button(frame, text="Войти", style="Success.TButton",
                   command=self.login).pack(fill="x", pady=(10, 20))

        ttk.Button(frame, text="Создать аккаунт", style="Secondary.TButton",
                   command=self.open_register).pack(fill="x")

        self.window.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Ошибка", "Введите логин и пароль")
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
