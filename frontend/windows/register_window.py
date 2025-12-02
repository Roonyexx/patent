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
        self.window.geometry("520x780")
        self.window.resizable(False, False)
        self.center_window()
        self.create_widgets()

    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")

    def create_widgets(self):
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas, padding="30")
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        ttk.Label(scrollable, text="Регистрация", style="Title.TLabel").pack(pady=(0, 20))

        # Email
        ttk.Label(scrollable, text="Email *").pack(anchor="w", pady=(10, 5))
        self.email_var = tk.StringVar()
        ttk.Entry(scrollable, textvariable=self.email_var, width=40).pack(fill="x", pady=(0, 10))

        # Логин
        ttk.Label(scrollable, text="Логин *").pack(anchor="w", pady=(10, 5))
        self.username_var = tk.StringVar()
        ttk.Entry(scrollable, textvariable=self.username_var, width=40).pack(fill="x", pady=(0, 10))

        # Пароль
        ttk.Label(scrollable, text="Пароль *").pack(anchor="w", pady=(10, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(scrollable, textvariable=self.password_var, show="•", width=40).pack(fill="x", pady=(0, 10))

        # Подтверждение пароля
        ttk.Label(scrollable, text="Подтвердите пароль *").pack(anchor="w", pady=(10, 5))
        self.confirm_var = tk.StringVar()
        ttk.Entry(scrollable, textvariable=self.confirm_var, show="•", width=40).pack(fill="x", pady=(0, 20))

        # Тип пользователя
        ttk.Label(scrollable, text="Тип пользователя *").pack(anchor="w", pady=(10, 5))
        self.user_type_var = tk.StringVar(value="author")
        frame_type = ttk.Frame(scrollable)
        frame_type.pack(fill="x", pady=(0, 20))
        ttk.Radiobutton(frame_type, text="Автор", variable=self.user_type_var, value="author",
                        command=self.toggle_fields).pack(side="left", padx=(0, 30))
        ttk.Radiobutton(frame_type, text="Сотрудник патентного отдела", variable=self.user_type_var, value="employee",
                        command=self.toggle_fields).pack(side="left")

        # ФИО
        ttk.Label(scrollable, text="ФИО *").pack(anchor="w", pady=(10, 5))
        self.full_name_var = tk.StringVar()
        ttk.Entry(scrollable, textvariable=self.full_name_var, width=40).pack(fill="x", pady=(0, 20))

        # === Блок сотрудника ===
        self.employee_block = ttk.LabelFrame(scrollable, text="Данные сотрудника", padding=15)

        ttk.Label(self.employee_block, text="Должность *").pack(anchor="w", pady=(5, 5))
        self.position_var = tk.StringVar()
        ttk.Combobox(self.employee_block, textvariable=self.position_var, state="readonly",
                     values=["Патентный эксперт", "Начальник отдела", "Технический специалист"]).pack(fill="x", pady=(0, 10))
        self.position_var.set("Патентный эксперт")

        ttk.Label(self.employee_block, text="Дата трудоустройства (ГГГГ-ММ-ДД)").pack(anchor="w", pady=(10, 5))
        self.employment_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(self.employee_block, textvariable=self.employment_var).pack(fill="x", pady=(0, 10))

        ttk.Label(self.employee_block, text="Телефон").pack(anchor="w", pady=(10, 5))
        self.phone_var = tk.StringVar()
        ttk.Entry(self.employee_block, textvariable=self.phone_var).pack(fill="x", pady=(0, 10))

        # Кнопки
        btn_frame = ttk.Frame(scrollable)
        btn_frame.pack(fill="x", pady=30)
        ttk.Button(btn_frame, text="Зарегистрироваться", style="Success.TButton", command=self.register).pack(side="left", expand=True, fill="x", padx=(0, 5))
        ttk.Button(btn_frame, text="Назад к входу", style="Secondary.TButton", command=self.back).pack(side="right", expand=True, fill="x", padx=(5, 0))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.toggle_fields()  # скрыть блок сотрудника при старте

    def toggle_fields(self):
        if self.user_type_var.get() == "employee":
            self.employee_block.pack(fill="x", pady=20)
        else:
            self.employee_block.pack_forget()

    def validate(self):
        e = self.email_var.get().strip()
        u = self.username_var.get().strip()
        p = self.password_var.get()
        c = self.confirm_var.get()
        f = self.full_name_var.get().strip()

        if not e: messagebox.showwarning("Ошибка", "Введите email"); return False
        if not u: messagebox.showwarning("Ошибка", "Введите логин"); return False
        if not p: messagebox.showwarning("Ошибка", "Введите пароль"); return False
        if p != c: messagebox.showwarning("Ошибка", "Пароли не совпадают"); return False
        if len(p) < 6: messagebox.showwarning("Ошибка", "Пароль должен быть не менее 6 символов"); return False
        if not f: messagebox.showwarning("Ошибка", "Введите ФИО"); return False

        if self.user_type_var.get() == "employee":
            if not self.position_var.get():
                messagebox.showwarning("Ошибка", "Выберите должность"); return False
            try:
                datetime.strptime(self.employment_var.get().strip(), "%Y-%m-%d")
            except:
                messagebox.showwarning("Ошибка", "Неверный формат даты (ГГГГ-ММ-ДД)"); return False

        return True

    def register(self):
        if not self.validate(): return

        data = {
            "email": self.email_var.get().strip(),
            "username": self.username_var.get().strip(),
            "password": self.password_var.get(),
            "user_type": self.user_type_var.get(),
            "full_name": self.full_name_var.get().strip()
        }

        if self.user_type_var.get() == "employee":
            pos_map = {"Патентный эксперт": 1, "Начальник отдела": 2, "Технический специалист": 3}
            data["position_id"] = pos_map.get(self.position_var.get(), 1)
            data["employment_date"] = self.employment_var.get().strip()
            if self.phone_var.get().strip():
                data["phone_number"] = self.phone_var.get().strip()

        try:
            self.api_client.register(data)
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