import tkinter as tk
from tkinter import messagebox

import src.client.config as config
import src.client.ui.ui_extensions as ext
from src.client.client import Client


WINDOW_SIZE = '400x200'


class LoginWindow:
    def __init__(self, client: Client):
        self.client = client

        self.window = tk.Tk()
        self.window.title('Вход в систему')
        self.window.geometry(WINDOW_SIZE)
        self.window.resizable(False, False)

        self.login_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self.create_widgets()
        ext.center_window(self.window)

    def create_widgets(self):
        frame = tk.Frame(self.window)
        frame.pack(fill='both', expand=True)

        for i in range(5):
            frame.rowconfigure(index=i, weight=1)

        for j in range(2):
            frame.columnconfigure(index=j, weight=1)

        tk.Label(frame, text='Вход', font=(config.FONT_FAMILY, 14)).grid(row=0, column=0, columnspan=2)

        ext.add_entry_field(frame, 'Логин:', self.login_var, 1, 0, 1, 1)
        ext.add_entry_field(frame, 'Пароль:', self.password_var, 2, 0, 2, 1)

        tk.Button(frame, text='Войти', command=self.login).grid(row=3, column=0, columnspan=2,
                                                                sticky='ew', padx=(100, 100))
        tk.Button(frame, text='Зарегистрироваться', command=self.open_register_window).grid(row=4, column=0, columnspan=2,
                                                                                         sticky='ew', padx=(100, 100))

    def login(self):
        login = self.login_var.get().strip()
        password = self.password_var.get().strip()

        if not login or not password:
            messagebox.showwarning('Ошибка', 'Поля логина и пароля не могут быть пустыми')
            return

        try:
            self.client.login(login, password)
            self.open_main_window()
        except Exception as e:
            messagebox.showerror('Ошибка входа', str(e))

    def open_main_window(self):
        self.window.destroy()

        from src.client.ui.main_window import MainWindow
        MainWindow(self.client).show()

    def open_register_window(self):
        self.window.destroy()

        from src.client.ui.register_window import RegisterWindow
        RegisterWindow(self.client).show()

    def show(self):
        self.window.mainloop()
