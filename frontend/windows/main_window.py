"""
Главное окно приложения
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from api_client import APIClient
from windows.applications_window import ApplicationsWindow
from windows.patents_window import PatentsWindow
from windows.analytics_window import AnalyticsWindow
from windows.references_window import ReferencesWindow


class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        
        self.window = tk.Tk()
        self.window.title(Config.APP_TITLE)
        self.window.geometry(Config.MAIN_WINDOW_SIZE)
        
        # Центрируем окно
        self.center_window()
        
        # Получаем информацию о пользователе
        try:
            self.user = self.api_client.get_current_user()
        except:
            self.user = self.api_client.user_info
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Обработка закрытия окна
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
    
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
        # Верхняя панель
        top_frame = ttk.Frame(self.window, padding="10")
        top_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Заголовок
        title_label = ttk.Label(
            top_frame,
            text=Config.APP_TITLE,
            style="Title.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Информация о пользователе
        user_frame = ttk.Frame(top_frame)
        user_frame.pack(side=tk.RIGHT)
        
        user_type_name = Config.USER_TYPE_NAMES.get(
            self.user.get('user_type', 'author'),
            "Пользователь"
        )
        
        user_info_label = ttk.Label(
            user_frame,
            text=f"{self.user.get('username', 'Пользователь')} ({user_type_name})",
            style="Light.TLabel"
        )
        user_info_label.pack(side=tk.LEFT, padx=(0, 10))
        
        logout_button = ttk.Button(
            user_frame,
            text="Выход",
            style="Secondary.TButton",
            command=self.logout
        )
        logout_button.pack(side=tk.LEFT)
        
        # Разделитель
        separator = ttk.Separator(self.window, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X)
        
        # Основной контейнер
        main_container = ttk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Боковое меню
        sidebar_frame = ttk.Frame(main_container, width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)
        
        # Меню
        menu_title = ttk.Label(
            sidebar_frame,
            text="Меню",
            style="Subtitle.TLabel"
        )
        menu_title.pack(pady=(0, 10))
        
        # Кнопки меню
        self.menu_buttons = []
        
        # Заявки
        btn_applications = ttk.Button(
            sidebar_frame,
            text="📋 Заявки",
            style="Secondary.TButton",
            command=lambda: self.show_content("applications")
        )
        btn_applications.pack(fill=tk.X, pady=(0, 5))
        self.menu_buttons.append(btn_applications)
        
        # Патенты
        btn_patents = ttk.Button(
            sidebar_frame,
            text="📜 Патенты",
            style="Secondary.TButton",
            command=lambda: self.show_content("patents")
        )
        btn_patents.pack(fill=tk.X, pady=(0, 5))
        self.menu_buttons.append(btn_patents)
        
        # Аналитика (только для сотрудников)
        if self.user.get('user_type') == Config.USER_TYPE_EMPLOYEE:
            btn_analytics = ttk.Button(
                sidebar_frame,
                text="📊 Аналитика",
                style="Secondary.TButton",
                command=lambda: self.show_content("analytics")
            )
            btn_analytics.pack(fill=tk.X, pady=(0, 5))
            self.menu_buttons.append(btn_analytics)
        
        # Справочники
        btn_references = ttk.Button(
            sidebar_frame,
            text="📚 Справочники",
            style="Secondary.TButton",
            command=lambda: self.show_content("references")
        )
        btn_references.pack(fill=tk.X, pady=(0, 5))
        self.menu_buttons.append(btn_references)
        
        # Разделитель в меню
        ttk.Separator(sidebar_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # О программе
        btn_about = ttk.Button(
            sidebar_frame,
            text="ℹ️ О программе",
            style="Secondary.TButton",
            command=self.show_about
        )
        btn_about.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Контент
        self.content_frame = ttk.Frame(main_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Показываем заявки по умолчанию
        self.current_content = None
        self.show_content("applications")
    
    def show_content(self, content_type):
        """Показать контент"""
        # Очищаем текущий контент
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Создаем новый контент
        if content_type == "applications":
            self.current_content = ApplicationsWindow(self.content_frame, self.api_client)
        elif content_type == "patents":
            self.current_content = PatentsWindow(self.content_frame, self.api_client)
        elif content_type == "analytics":
            self.current_content = AnalyticsWindow(self.content_frame, self.api_client)
        elif content_type == "references":
            self.current_content = ReferencesWindow(self.content_frame, self.api_client)
    
    def show_about(self):
        """Показать информацию о программе"""
        messagebox.showinfo(
            "О программе",
            f"{Config.APP_TITLE}\n"
            f"Версия {Config.APP_VERSION}\n\n"
            "Система управления патентами\n"
            "для патентного отдела\n\n"
            "© 2025"
        )
    
    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
            try:
                self.api_client.logout()
            except:
                pass
            
            self.window.destroy()
            
            # Открываем окно входа
            from windows.login_window import LoginWindow
            login_window = LoginWindow(self.api_client, lambda: MainWindow(self.api_client).run())
            login_window.run()
    
    def on_closing(self):
        """Обработка закрытия окна"""
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти из программы?"):
            try:
                self.api_client.logout()
            except:
                pass
            self.window.destroy()
    
    def run(self):
        """Запустить окно"""
        self.window.mainloop()