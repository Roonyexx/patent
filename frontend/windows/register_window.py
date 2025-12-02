
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from config import Config
from api_client import APIClient


class RegisterWindow:
    """Окно для регистрации нового пользователя"""
    
    def __init__(self, api_client: APIClient, on_success_callback):
        self.api_client = api_client
        self.on_success_callback = on_success_callback
        
        self.window = tk.Tk()
        self.window.title(f"{Config.APP_TITLE} - Регистрация")
        self.window.geometry("500x700")
        self.window.resizable(False, False)
        
        # Центрируем окно
        self.center_window()
        
        # Создаем интерфейс
        self.create_widgets()
        
    def center_window(self):
        """Центрировать окно на экране"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Создать виджеты окна"""
        # Контейнер с прокруткой
        canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="30")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Заголовок
        title_label = ttk.Label(
            scrollable_frame,
            text="Регистрация",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 20))
        
        # Форма
        form_frame = ttk.Frame(scrollable_frame)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Email
        ttk.Label(form_frame, text="Email:").pack(anchor=tk.W, pady=(0, 5))
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var).pack(fill=tk.X, pady=(0, 15))
        
        # Имя пользователя
        ttk.Label(form_frame, text="Имя пользователя:").pack(anchor=tk.W, pady=(0, 5))
        self.username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.username_var).pack(fill=tk.X, pady=(0, 15))
        
        # Пароль
        ttk.Label(form_frame, text="Пароль:").pack(anchor=tk.W, pady=(0, 5))
        self.password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.password_var, show="•").pack(fill=tk.X, pady=(0, 15))
        
        # Подтверждение пароля
        ttk.Label(form_frame, text="Подтвердите пароль:").pack(anchor=tk.W, pady=(0, 5))
        self.confirm_password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.confirm_password_var, show="•").pack(fill=tk.X, pady=(0, 15))
        
        # Тип пользователя
        ttk.Label(form_frame, text="Тип пользователя:").pack(anchor=tk.W, pady=(0, 5))
        self.user_type_var = tk.StringVar(value="employee")
        
        user_type_frame = ttk.Frame(form_frame)
        user_type_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Radiobutton(
            user_type_frame,
            text="Сотрудник",
            variable=self.user_type_var,
            value="employee",
            command=self.toggle_employee_fields
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Radiobutton(
            user_type_frame,
            text="Автор",
            variable=self.user_type_var,
            value="author",
            command=self.toggle_employee_fields
        ).pack(side=tk.LEFT)
        
        # ФИО
        ttk.Label(form_frame, text="ФИО:").pack(anchor=tk.W, pady=(0, 5))
        self.full_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.full_name_var).pack(fill=tk.X, pady=(0, 15))
        
        # Поля для сотрудника
        self.employee_frame = ttk.LabelFrame(form_frame, text="Данные сотрудника", padding="10")
        self.employee_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Должность
        ttk.Label(self.employee_frame, text="Должность:").pack(anchor=tk.W, pady=(0, 5))
        self.position_var = tk.StringVar()
        self.position_combo = ttk.Combobox(
            self.employee_frame,
            textvariable=self.position_var,
            state="readonly"
        )
        self.position_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Загружаем должности (в реальности нужно получить из API)
        self.position_combo['values'] = ("Патентный эксперт", "Начальник отдела", "папочка")
        self.position_combo.current(0)
        
        # Дата трудоустройства
        ttk.Label(self.employee_frame, text="Дата трудоустройства (ГГГГ-ММ-ДД):").pack(anchor=tk.W, pady=(0, 5))
        self.employment_date_var = tk.StringVar(value=str(date.today()))
        ttk.Entry(self.employee_frame, textvariable=self.employment_date_var).pack(fill=tk.X, pady=(0, 10))
        
        # Телефон
        ttk.Label(self.employee_frame, text="Телефон:").pack(anchor=tk.W, pady=(0, 5))
        self.phone_var = tk.StringVar()
        ttk.Entry(self.employee_frame, textvariable=self.phone_var).pack(fill=tk.X)
        
        # Кнопки
        buttons_frame = ttk.Frame(form_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            buttons_frame,
            text="Зарегистрироваться",
            style="Primary.TButton",
            command=self.register
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="Назад к входу",
            style="Secondary.TButton",
            command=self.back_to_login
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        # Размещаем canvas и scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Прокрутка колесом мыши
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def toggle_employee_fields(self):
        """Показать/скрыть поля для сотрудника"""
        if self.user_type_var.get() == "employee":
            self.employee_frame.pack(fill=tk.X, pady=(0, 15))
        else:
            self.employee_frame.pack_forget()
    
    def validate_fields(self):
        """Валидация полей формы"""
        if not self.email_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите email")
            return False
        
        if not self.username_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите имя пользователя")
            return False
        
        if not self.password_var.get():
            messagebox.showwarning("Предупреждение", "Введите пароль")
            return False
        
        if self.password_var.get() != self.confirm_password_var.get():
            messagebox.showwarning("Предупреждение", "Пароли не совпадают")
            return False
        
        if len(self.password_var.get()) < 6:
            messagebox.showwarning("Предупреждение", "Пароль должен быть минимум 6 символов")
            return False
        
        if not self.full_name_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите ФИО")
            return False
        
        if self.user_type_var.get() == "employee":
            if not self.position_var.get():
                messagebox.showwarning("Предупреждение", "Выберите должность")
                return False
        
        return True
    
    def register(self):
        """Выполнить регистрацию"""
        if not self.validate_fields():
            return
        
        try:
            # Подготовка данных
            user_data = {
                "email": self.email_var.get().strip(),
                "username": self.username_var.get().strip(),
                "password": self.password_var.get(),
                "user_type": self.user_type_var.get(),
                "full_name": self.full_name_var.get().strip()
            }
            
            # Добавляем данные сотрудника
            if self.user_type_var.get() == "employee":
                # Получаем ID должности (1-3 согласно базе)
                positions = {
                    "Патентный эксперт": 1,
                    "Начальник отдела": 2,
                    "папочка": 3
                }
                user_data["position_id"] = positions.get(self.position_var.get(), 1)
                user_data["employment_date"] = self.employment_date_var.get()
                
                if self.phone_var.get().strip():
                    user_data["phone_number"] = self.phone_var.get().strip()
            
            # Выполняем регистрацию через API
            response = self.api_client.register(user_data)
            
            # Показываем сообщение об успехе
            messagebox.showinfo(
                "Успех",
                f"Регистрация прошла успешно!\nДобро пожаловать, {response['username']}!"
            )
            
            # Закрываем окно
            self.window.destroy()
            
            # Вызываем callback
            if self.on_success_callback:
                self.on_success_callback()
                
        except Exception as e:
            messagebox.showerror(
                "Ошибка регистрации",
                f"Не удалось зарегистрироваться:\n{str(e)}"
            )
    
    def back_to_login(self):
        """Вернуться к окну входа"""
        from windows.login_window import LoginWindow
        
        self.window.destroy()
        login_window = LoginWindow(self.api_client, self.on_success_callback)
        login_window.run()
    
    def run(self):
        """Запустить окно"""
        self.window.mainloop()