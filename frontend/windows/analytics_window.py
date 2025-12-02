"""
Окно аналитики и отчетов
"""
import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from api_client import APIClient


class AnalyticsWindow:
    """Окно для просмотра аналитики"""
    
    def __init__(self, parent_frame, api_client: APIClient):
        self.parent_frame = parent_frame
        self.api_client = api_client
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Создать виджеты"""
        # Заголовок
        header_frame = ttk.Frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            header_frame,
            text="Аналитика и отчеты",
            style="Subtitle.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Кнопка обновления
        ttk.Button(
            header_frame,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_data
        ).pack(side=tk.RIGHT)
        
        # Вкладки
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка: Общая статистика
        self.general_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.general_frame, text="Общая статистика")
        
        # Вкладка: По авторам
        self.authors_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.authors_frame, text="По авторам")
        
        # Вкладка: По годам
        self.years_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.years_frame, text="По годам")
        
        # Вкладка: По типам
        self.types_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.types_frame, text="По типам")
        
        # Создаем содержимое вкладок
        self.create_general_tab()
        self.create_authors_tab()
        self.create_years_tab()
        self.create_types_tab()
    
    def create_general_tab(self):
        """Создать вкладку общей статистики"""
        # Карточки со статистикой
        cards_frame = ttk.Frame(self.general_frame)
        cards_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Карточка: Всего патентов
        total_card = ttk.LabelFrame(cards_frame, text="Всего патентов", padding="20")
        total_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))
        
        self.total_patents_var = tk.StringVar(value="0")
        ttk.Label(
            total_card,
            textvariable=self.total_patents_var,
            font=(Config.FONT_FAMILY, 32, "bold"),
            foreground=Config.PRIMARY_COLOR
        ).pack()
        
        # Карточка: Всего заявок
        apps_card = ttk.LabelFrame(cards_frame, text="Всего заявок", padding="20")
        apps_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 10))
        
        self.total_applications_var = tk.StringVar(value="0")
        ttk.Label(
            apps_card,
            textvariable=self.total_applications_var,
            font=(Config.FONT_FAMILY, 32, "bold"),
            foreground=Config.SECONDARY_COLOR
        ).pack()
        
        # Карточка: Истекшие патенты
        expired_card = ttk.LabelFrame(cards_frame, text="Истекшие патенты", padding="20")
        expired_card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        self.expired_patents_var = tk.StringVar(value="0")
        ttk.Label(
            expired_card,
            textvariable=self.expired_patents_var,
            font=(Config.FONT_FAMILY, 32, "bold"),
            foreground=Config.DANGER_COLOR
        ).pack()
        
        # Информация
        info_frame = ttk.LabelFrame(self.general_frame, text="Информация", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        self.general_info_text = tk.Text(
            info_frame,
            height=10,
            font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.general_info_text.pack(fill=tk.BOTH, expand=True)
    
    def create_authors_tab(self):
        """Создать вкладку статистики по авторам"""
        # Таблица
        table_frame = ttk.Frame(self.authors_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("author", "patent_count")
        self.authors_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.authors_tree.yview)
        
        self.authors_tree.heading("#0", text="")
        self.authors_tree.heading("author", text="Автор")
        self.authors_tree.heading("patent_count", text="Количество патентов")
        
        self.authors_tree.column("#0", width=0, stretch=False)
        self.authors_tree.column("author", width=400)
        self.authors_tree.column("patent_count", width=200, anchor=tk.CENTER)
        
        self.authors_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_years_tab(self):
        """Создать вкладку статистики по годам"""
        table_frame = ttk.Frame(self.years_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("year", "patent_count")
        self.years_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.years_tree.yview)
        
        self.years_tree.heading("#0", text="")
        self.years_tree.heading("year", text="Год")
        self.years_tree.heading("patent_count", text="Количество патентов")
        
        self.years_tree.column("#0", width=0, stretch=False)
        self.years_tree.column("year", width=400, anchor=tk.CENTER)
        self.years_tree.column("patent_count", width=200, anchor=tk.CENTER)
        
        self.years_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_types_tab(self):
        """Создать вкладку статистики по типам"""
        table_frame = ttk.Frame(self.types_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("type", "patent_count")
        self.types_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.types_tree.yview)
        
        self.types_tree.heading("#0", text="")
        self.types_tree.heading("type", text="Тип патента")
        self.types_tree.heading("patent_count", text="Количество патентов")
        
        self.types_tree.column("#0", width=0, stretch=False)
        self.types_tree.column("type", width=400)
        self.types_tree.column("patent_count", width=200, anchor=tk.CENTER)
        
        self.types_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Загрузить данные"""
        try:
            # Общая статистика
            activity = self.api_client.get_activity_report()
            self.total_patents_var.set(str(activity.get('total_patents', 0)))
            self.total_applications_var.set(str(activity.get('total_applications', 0)))
            self.expired_patents_var.set(str(activity.get('expired_patents', 0)))
            
            # Обновляем текстовую информацию
            self.general_info_text.config(state=tk.NORMAL)
            self.general_info_text.delete('1.0', tk.END)
            
            info_text = f"""
Отчет о патентной активности

Общее количество патентов: {activity.get('total_patents', 0)}
Общее количество заявок: {activity.get('total_applications', 0)}
Истекшие патенты: {activity.get('expired_patents', 0)}

Активные патенты: {activity.get('total_patents', 0) - activity.get('expired_patents', 0)}
            """
            
            self.general_info_text.insert('1.0', info_text)
            self.general_info_text.config(state=tk.DISABLED)
            
            # Статистика по авторам
            self.load_authors_stats()
            
            # Статистика по годам
            self.load_years_stats()
            
            # Статистика по типам
            self.load_types_stats()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить аналитику:\n{str(e)}")
    
    def load_authors_stats(self):
        """Загрузить статистику по авторам"""
        try:
            data = self.api_client.get_statistics_by_author()
            
            # Очищаем таблицу
            for item in self.authors_tree.get_children():
                self.authors_tree.delete(item)
            
            # Заполняем
            for item in data.get('data', []):
                values = (
                    item.get('author', 'Неизвестно'),
                    item.get('patent_count', 0)
                )
                self.authors_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            print(f"Ошибка загрузки статистики по авторам: {e}")
    
    def load_years_stats(self):
        """Загрузить статистику по годам"""
        try:
            data = self.api_client.get_statistics_by_year()
            
            # Очищаем таблицу
            for item in self.years_tree.get_children():
                self.years_tree.delete(item)
            
            # Заполняем и сортируем по году
            items = data.get('data', [])
            items_sorted = sorted(items, key=lambda x: x.get('year') or 0, reverse=True)
            
            for item in items_sorted:
                year = item.get('year')
                year_str = str(int(year)) if year else 'Не указан'
                
                values = (
                    year_str,
                    item.get('patent_count', 0)
                )
                self.years_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            print(f"Ошибка загрузки статистики по годам: {e}")
    
    def load_types_stats(self):
        """Загрузить статистику по типам"""
        try:
            data = self.api_client.get_statistics_by_type()
            
            # Очищаем таблицу
            for item in self.types_tree.get_children():
                self.types_tree.delete(item)
            
            # Заполняем
            for item in data.get('data', []):
                type_id = item.get('type_id')
                type_name = Config.PATENT_TYPE_NAMES.get(type_id, f'Тип {type_id}')
                
                values = (
                    type_name,
                    item.get('patent_count', 0)
                )
                self.types_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            print(f"Ошибка загрузки статистики по типам: {e}")