import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import src.client.ui.ui_extensions as ext
from src.client.client import Client


WINDOW_SIZE = '600x400'
MIN_PASSWORD_LENGTH = 5


def validate_datetime(date: str) -> bool:
    try:
        datetime.strptime(date.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


class RegisterWindow:
    def __init__(self, client: Client):
        self.client = client

        self.positions = self.client.get_positions()

        self.window = tk.Tk()
        self.window.title('Регистрация в системе')
        self.window.geometry(WINDOW_SIZE)
        self.window.resizable(False, False)

        self.email_var = tk.StringVar(master=self.window)
        self.login_var = tk.StringVar(master=self.window)
        self.password_var = tk.StringVar(master=self.window)
        self.full_name_var = tk.StringVar(master=self.window)
        self.position_var = tk.StringVar(master=self.window)
        self.employment_var = tk.StringVar(master=self.window, value=str(date.today()))
        self.phone_var = tk.StringVar(master=self.window)
        self.passport_var = tk.StringVar(master=self.window)
        self.birth_date_var = tk.StringVar(master=self.window)

        self.create_widgets()
        ext.center_window(self.window)

    def create_widgets(self):
        frame = tk.Frame(self.window)
        frame.pack(fill='both', expand=True)

        for i in range(11):
            frame.rowconfigure(index=i, weight=1)

        for j in range(2):
            frame.columnconfigure(index=j, weight=1)

        tk.Label(frame, text='Регистрация', font=('Segoe UI', 14)).grid(row=0, column=0, columnspan=2)

        ext.add_entry_field(frame, 'Email:', self.email_var, 1, 0, 1, 1)
        ext.add_entry_field(frame, 'Логин*:', self.login_var, 2, 0, 2, 1)
        ext.add_entry_field(frame, 'Пароль*:', self.password_var, 3, 0, 3, 1)
        ext.add_entry_field(frame, 'ФИО*:', self.full_name_var, 4, 0, 4, 1)

        tk.Label(frame, text='Должность:').grid(row=5, column=0)
        combobox_values = [x['name'] for x in self.positions]
        ttk.Combobox(frame, textvariable=self.position_var, state="readonly", values=combobox_values).grid(row=5, column=1)
        self.position_var.set(self.positions[0]['name'])

        ext.add_entry_field(frame, 'Дата трудоустройства:', self.employment_var, 6, 0, 6, 1)
        ext.add_entry_field(frame, 'Телефон:', self.phone_var, 7, 0, 7, 1)
        ext.add_entry_field(frame, 'Серия и номер паспорта (через пробел):', self.passport_var, 8, 0, 8, 1)
        ext.add_entry_field(frame, 'Дата рождения (ГГГГ-ММ-ДД)', self.birth_date_var, 9, 0, 9, 1)

        tk.Button(frame, text='Зарегистрироваться', command=self.register).grid(row=10, column=0)
        tk.Button(frame, text='Назад', command=self.open_login_window).grid(row=10, column=1)

    def validate(self):
        if not self.email_var.get().strip():
            return 'Введите email'

        if not self.login_var.get().strip():
            return 'Введите логин'

        if len(self.password_var.get()) < MIN_PASSWORD_LENGTH:
            return f'Пароль должен быть не менее {MIN_PASSWORD_LENGTH} символов'

        if not self.full_name_var.get().strip():
            return 'Введите полное имя пользователя'

        # if not validate_datetime(self.employment_var.get().strip()):
        #     return 'Дата не соответствует формату yyyy-mm-dd'

    def register(self):
        err = self.validate()

        if err:
            messagebox.showwarning('Ошибка', err)
            return

        payload = {
            "email": self.email_var.get().strip(),
            "username": self.login_var.get().strip(),
            "password": self.password_var.get(),
            "full_name": self.full_name_var.get().strip(),
            "user_type": 'employee'
        }

        payload.update({
            "position_id": self.get_position_id(),
            "employment_date": self.employment_var.get().strip(),
            "phone_number": self.phone_var.get().strip() or None
        })

        password_parts = self.passport_var.get().strip().split()

        if len(password_parts) == 2 and password_parts[0].isdigit() and password_parts[1].isdigit():
            payload["passport_series"] = int(password_parts[0])
            payload["passport_number"] = int(password_parts[1])

        payload["birth_date"] = self.birth_date_var.get().strip()

        try:
            self.client.register(payload)
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.open_main_window()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def get_position_id(self) -> int:
        for position in self.positions:
            if position['name'] == self.position_var.get().strip():
                return position['id']

        return self.positions[0]['id']

    def open_login_window(self):
        self.window.destroy()

        from src.client.ui.login_window import LoginWindow
        LoginWindow(self.client).show()

    def open_main_window(self):
        self.window.destroy()

        from src.client.ui.main_window import MainWindow
        MainWindow(self.client).show()

    def show(self):
        self.window.mainloop()