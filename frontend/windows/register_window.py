# frontend/windows/register_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from config import Config
from api_client import APIClient


class RegisterWindow:
    def __init__(self, api_client: APIClient, on_success_callback):
        self.api_client = api_client
        self.on_success_callback = on_success_callback

        self.window = tk.Tk()
        self.window.title(f"{Config.APP_TITLE} - Регистрация")
        self.window.geometry("620x900")
        self.window.resizable(False, False)

        # StringVar
        self.email_var = tk.StringVar(master=self.window)
        self.username_var = tk.StringVar(master=self.window)
        self.password_var = tk.StringVar(master=self.window)
        self.confirm_var = tk.StringVar(master=self.window)
        self.full_name_var = tk.StringVar(master=self.window)
        self.position_var = tk.StringVar(master=self.window)
        self.employment_var = tk.StringVar(master=self.window, value=str(date.today()))
        self.phone_var = tk.StringVar(master=self.window)
        self.passport_var = tk.StringVar(master=self.window)
        self.birth_date_var = tk.StringVar(master=self.window)
        self.user_type_var = tk.StringVar(master=self.window, value="author")

        self.center_window()
        self.create_widgets()
        self.show_fields()

    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def create_widgets(self):
        main = ttk.Frame(self.window, padding=35)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Регистрация в системе", style="Title.TLabel").pack(pady=(0, 30))

        ttk.Label(main, text="Кто вы?", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        type_frame = ttk.Frame(main)
        type_frame.pack(fill="x", pady=(0, 20))

        ttk.Radiobutton(type_frame, text="Я — Автор изобретения / рационализаторского предложения",
                        variable=self.user_type_var, value="author", command=self.show_fields).pack(anchor="w", pady=6)
        ttk.Radiobutton(type_frame, text="Я — Сотрудник патентного отдела",
                        variable=self.user_type_var, value="employee", command=self.show_fields).pack(anchor="w", pady=6)

        self.fields_frame = ttk.Frame(main)
        self.fields_frame.pack(fill="both", expand=True, pady=(10, 0))

        self.btn_frame = ttk.Frame(main)
        self.btn_frame.pack(fill="x", pady=30)
        self.create_buttons()

    def show_fields(self):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        if self.user_type_var.get() == "author":
            self.show_author_fields()
        else:
            self.show_employee_fields()

    def show_author_fields(self):
        f = self.fields_frame
        ttk.Label(f, text="Регистрация автора", font=("Segoe UI", 14, "bold"),
                  foreground=Config.SECONDARY_COLOR).pack(anchor="w", pady=(0, 20))
        self.add_field(f, "Email *", self.email_var)
        self.add_field(f, "Логин *", self.username_var)
        self.add_field(f, "Пароль *", self.password_var, show="•")
        self.add_field(f, "Подтвердите пароль *", self.confirm_var, show="•")
        self.add_field(f, "ФИО *", self.full_name_var, pady=(20, 0))
        ttk.Label(f, text="Паспортные данные (необязательно)", foreground=Config.LIGHT_TEXT).pack(anchor="w", pady=(20, 5))
        self.add_field(f, "Серия и номер паспорта (через пробел)", self.passport_var)
        self.add_field(f, "Дата рождения (ГГГГ-ММ-ДД)", self.birth_date_var)

    def show_employee_fields(self):
        f = self.fields_frame
        ttk.Label(f, text="Регистрация сотрудника", font=("Segoe UI", 14, "bold"),
                  foreground=Config.SUCCESS_COLOR).pack(anchor="w", pady=(0, 15))
        self.add_field(f, "Email *", self.email_var)
        self.add_field(f, "Логин *", self.username_var)
        self.add_field(f, "Пароль *", self.password_var, show="•")
        self.add_field(f, "Подтвердите пароль *", self.confirm_var, show="•")
        self.add_field(f, "ФИО *", self.full_name_var, pady=(10, 0))
        ttk.Label(f, text="Должность *").pack(anchor="w", pady=(10, 5))
        ttk.Combobox(f, textvariable=self.position_var, state="readonly",
                     values=["Патентный эксперт", "Начальник отдела", "папочка"]).pack(fill="x", pady=(0, 10))
        self.position_var.set("Патентный эксперт")
        self.add_field(f, "Дата трудоустройства *", self.employment_var, pady=(15, 0))
        self.add_field(f, "Телефон", self.phone_var)

    def add_field(self, parent, label, var, show=None, pady=(5, 10)):
        ttk.Label(parent, text=label).pack(anchor="w", pady=(pady[0], 3))
        ttk.Entry(parent, textvariable=var, width=50, show=show).pack(fill="x", pady=(0, pady[1]))

    def create_buttons(self):
        ttk.Button(self.btn_frame, text="Зарегистрироваться", style="Success.TButton",
                   command=self.submit).pack(side="left", expand=True, fill="x", padx=5)
        ttk.Button(self.btn_frame, text="Назад к входу", style="Secondary.TButton",
                   command=self.back).pack(side="right", expand=True, fill="x", padx=5)

    def validate(self):
        if not self.email_var.get().strip(): return "Введите email"
        if not self.username_var.get().strip(): return "Введите логин"
        if len(self.password_var.get()) < 6: return "Пароль должен быть не менее 6 символов"
        if self.password_var.get() != self.confirm_var.get(): return "Пароли не совпадают"
        if not self.full_name_var.get().strip(): return "Введите ФИО"
        if self.user_type_var.get() == "employee":
            try:
                datetime.strptime(self.employment_var.get().strip(), "%Y-%m-%d")
            except:
                return "Неверный формат даты трудоустройства"
        return None

    def submit(self):
        err = self.validate()
        if err:
            messagebox.showwarning("Ошибка", err)
            return

        payload = {
            "email": self.email_var.get().strip(),
            "username": self.username_var.get().strip(),
            "password": self.password_var.get(),
            "full_name": self.full_name_var.get().strip(),
            "user_type": self.user_type_var.get()
        }

        if self.user_type_var.get() == "employee":
            payload.update({
                "position_name": self.position_var.get(),
                "employment_date": self.employment_var.get().strip(),
                "phone_number": self.phone_var.get().strip() or None
            })
        else:
            if self.passport_var.get().strip():
                parts = self.passport_var.get().strip().split()
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    payload["passport_series"] = int(parts[0])
                    payload["passport_number"] = int(parts[1])
            if self.birth_date_var.get().strip():
                payload["birth_date"] = self.birth_date_var.get().strip()

        try:
            self.api_client.register(payload)
            messagebox.showinfo("Успех", "Регистрация прошла успешно!")
            self.window.destroy()
            self.on_success_callback()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def back(self):
        from windows.login_window import LoginWindow
        self.window.destroy()
        LoginWindow(self.api_client, self.on_success_callback).run()

    def run(self):
        self.window.mainloop()