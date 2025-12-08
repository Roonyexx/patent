import tkinter as tk
from tkinter import ttk, messagebox

import src.client.config as config
from src.client.client import Client


class ReferencesWindow:
    """Окно для работы со справочниками"""
    
    def __init__(self, parent_frame, api_client: Client):
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
            text="Справочники",
            style="Subtitle.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Вкладки
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка: Сотрудники
        self.employees_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.employees_frame, text="Сотрудники")
        
        # Вкладка: Авторы
        self.authors_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.authors_frame, text="Авторы")
        
        # Вкладка: Статусы
        self.statuses_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.statuses_frame, text="Статусы")
        
        # Вкладка: Типы патентов
        self.types_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.types_frame, text="Типы патентов")
        
        # Вкладка: Правообладатели
        self.holders_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.holders_frame, text="Правообладатели")
        
        # Создаем содержимое вкладок
        self.create_employees_tab()
        self.create_authors_tab()
        self.create_statuses_tab()
        self.create_types_tab()
        self.create_holders_tab()
    
    def create_employees_tab(self):
        """Создать вкладку сотрудников"""
        # Toolbar
        toolbar = ttk.Frame(self.employees_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_employees
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Таблица
        table_frame = ttk.Frame(self.employees_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "full_name", "employment_date", "phone_number", "position_id")
        self.employees_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.employees_tree.yview)
        
        self.employees_tree.heading("#0", text="")
        self.employees_tree.heading("id", text="ID")
        self.employees_tree.heading("full_name", text="ФИО")
        self.employees_tree.heading("employment_date", text="Дата трудоустройства")
        self.employees_tree.heading("phone_number", text="Телефон")
        self.employees_tree.heading("position_id", text="ID Должности")
        
        self.employees_tree.column("#0", width=0, stretch=False)
        self.employees_tree.column("id", width=50, anchor=tk.CENTER)
        self.employees_tree.column("full_name", width=250)
        self.employees_tree.column("employment_date", width=150, anchor=tk.CENTER)
        self.employees_tree.column("phone_number", width=150)
        self.employees_tree.column("position_id", width=100, anchor=tk.CENTER)
        
        self.employees_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_authors_tab(self):
        """Создать вкладку авторов"""
        # Toolbar
        toolbar = ttk.Frame(self.authors_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_authors
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Поиск по ФИО
        ttk.Label(toolbar, text="Поиск по ФИО:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.author_search_var = tk.StringVar()
        self.author_search_var.trace('w', lambda *args: self.filter_authors())
        ttk.Entry(toolbar, textvariable=self.author_search_var, width=30).pack(side=tk.LEFT)
        
        # Таблица
        table_frame = ttk.Frame(self.authors_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "full_name", "passport_id")
        self.authors_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.authors_tree.yview)
        
        self.authors_tree.heading("#0", text="")
        self.authors_tree.heading("id", text="ID")
        self.authors_tree.heading("full_name", text="ФИО")
        self.authors_tree.heading("passport_id", text="ID Паспорта")
        
        self.authors_tree.column("#0", width=0, stretch=False)
        self.authors_tree.column("id", width=100, anchor=tk.CENTER)
        self.authors_tree.column("full_name", width=400)
        self.authors_tree.column("passport_id", width=150, anchor=tk.CENTER)
        
        self.authors_tree.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка для просмотра патентов автора
        btn_frame = ttk.Frame(self.authors_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(
            btn_frame,
            text="📜 Показать патенты автора",
            style="Secondary.TButton",
            command=self.show_author_patents
        ).pack(side=tk.LEFT)
    
    def create_statuses_tab(self):
        """Создать вкладку статусов"""
        # Toolbar
        toolbar = ttk.Frame(self.statuses_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_statuses
        ).pack(side=tk.LEFT)
        
        # Таблица
        table_frame = ttk.Frame(self.statuses_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "name")
        self.statuses_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.statuses_tree.yview)
        
        self.statuses_tree.heading("#0", text="")
        self.statuses_tree.heading("id", text="ID")
        self.statuses_tree.heading("name", text="Название")
        
        self.statuses_tree.column("#0", width=0, stretch=False)
        self.statuses_tree.column("id", width=100, anchor=tk.CENTER)
        self.statuses_tree.column("name", width=500)
        
        self.statuses_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_types_tab(self):
        """Создать вкладку типов патентов"""
        # Toolbar
        toolbar = ttk.Frame(self.types_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_types
        ).pack(side=tk.LEFT)
        
        # Таблица
        table_frame = ttk.Frame(self.types_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "name")
        self.types_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.types_tree.yview)
        
        self.types_tree.heading("#0", text="")
        self.types_tree.heading("id", text="ID")
        self.types_tree.heading("name", text="Название")
        
        self.types_tree.column("#0", width=0, stretch=False)
        self.types_tree.column("id", width=100, anchor=tk.CENTER)
        self.types_tree.column("name", width=500)
        
        self.types_tree.pack(fill=tk.BOTH, expand=True)
    
    def create_holders_tab(self):
        """Создать вкладку правообладателей"""
        # Toolbar
        toolbar = ttk.Frame(self.holders_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            toolbar,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_holders
        ).pack(side=tk.LEFT)
        
        # Таблица
        table_frame = ttk.Frame(self.holders_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "name")
        self.holders_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set
        )
        
        vsb.config(command=self.holders_tree.yview)
        
        self.holders_tree.heading("#0", text="")
        self.holders_tree.heading("id", text="ID")
        self.holders_tree.heading("name", text="Название")
        
        self.holders_tree.column("#0", width=0, stretch=False)
        self.holders_tree.column("id", width=100, anchor=tk.CENTER)
        self.holders_tree.column("name", width=500)
        
        self.holders_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_data(self):
        """Загрузить все данные"""
        self.load_employees()
        self.load_authors()
        self.load_statuses()
        self.load_types()
        self.load_holders()
    
    def load_employees(self):
        """Загрузить сотрудников"""
        try:
            employees = self.api_client.get_employees()
            
            for item in self.employees_tree.get_children():
                self.employees_tree.delete(item)
            
            for emp in employees:
                values = (
                    emp.get('id', ''),
                    emp.get('full_name', ''),
                    emp.get('employment_date', ''),
                    emp.get('phone_number', ''),
                    emp.get('position_id', '')
                )
                self.employees_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сотрудников:\n{str(e)}")
    
    def load_authors(self):
        """Загрузить авторов"""
        try:
            self.authors_data = self.api_client.get_authors()
            
            for item in self.authors_tree.get_children():
                self.authors_tree.delete(item)
            
            for author in self.authors_data:
                values = (
                    author.get('id', ''),
                    author.get('full_name', ''),
                    author.get('passport_id', '-')
                )
                self.authors_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить авторов:\n{str(e)}")
    
    def filter_authors(self):
        """Фильтровать авторов по ФИО"""
        search_text = self.author_search_var.get().lower()
        
        for item in self.authors_tree.get_children():
            self.authors_tree.delete(item)
        
        for author in self.authors_data:
            full_name = (author.get('full_name') or '').lower()
            
            if search_text and search_text not in full_name:
                continue
            
            values = (
                author.get('id', ''),
                author.get('full_name', ''),
                author.get('passport_id', '-')
            )
            self.authors_tree.insert("", tk.END, values=values)
    
    def show_author_patents(self):
        """Показать патенты выбранного автора"""
        selected = self.authors_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автора")
            return
        
        author_id = int(self.authors_tree.item(selected[0])['values'][0])
        author_name = self.authors_tree.item(selected[0])['values'][1]
        
        # Получаем все патенты и фильтруем по автору
        try:
            # Получаем заявки этого автора
            applications = self.api_client.get_applications()
            author_apps = [app for app in applications if app.get('author_id') == author_id]
            
            # Получаем патенты для этих заявок
            all_patents = self.api_client.get_patents()
            author_patents = [p for p in all_patents if p.get('application_id') in [a['id'] for a in author_apps]]
            
            # Создаем окно с результатами
            result_window = tk.Toplevel(self.parent_frame)
            result_window.title(f"Патенты автора: {author_name}")
            result_window.geometry("900x500")
            
            main_frame = ttk.Frame(result_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(
                main_frame,
                text=f"Патенты автора: {author_name}",
                style="Title.TLabel"
            ).pack(pady=(0, 20))
            
            # Таблица
            table_frame = ttk.Frame(main_frame)
            table_frame.pack(fill=tk.BOTH, expand=True)
            
            vsb = ttk.Scrollbar(table_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)
            
            columns = ("id", "title", "issue_date", "type", "status")
            tree = ttk.Treeview(
                table_frame,
                columns=columns,
                show="tree headings",
                yscrollcommand=vsb.set
            )
            
            vsb.config(command=tree.yview)
            
            tree.heading("#0", text="")
            tree.heading("id", text="ID")
            tree.heading("title", text="Название")
            tree.heading("issue_date", text="Дата выдачи")
            tree.heading("type", text="Тип")
            tree.heading("status", text="Статус")
            
            tree.column("#0", width=0, stretch=False)
            tree.column("id", width=50, anchor=tk.CENTER)
            tree.column("title", width=300)
            tree.column("issue_date", width=120, anchor=tk.CENTER)
            tree.column("type", width=150)
            tree.column("status", width=120)
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Заполняем
            for patent in author_patents:
                values = (
                    patent.get('id', ''),
                    patent.get('title', ''),
                    patent.get('issue_date', ''),
                    config.PATENT_TYPE_NAMES.get(patent.get('patent_type_id'), 'Неизвестно'),
                    patent.get('status', {}).get('name', 'Не указан') if patent.get('status') else 'Не указан'
                )
                tree.insert("", tk.END, values=values)
            
            ttk.Label(
                main_frame,
                text=f"Всего патентов: {len(author_patents)}",
                style="Light.TLabel"
            ).pack(pady=(10, 0))
            
            ttk.Button(
                main_frame,
                text="Закрыть",
                style="Secondary.TButton",
                command=result_window.destroy
            ).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить патенты автора:\n{str(e)}")
    
    def load_statuses(self):
        """Загрузить статусы"""
        try:
            statuses = self.api_client.get_statuses()
            
            for item in self.statuses_tree.get_children():
                self.statuses_tree.delete(item)
            
            for status in statuses:
                values = (
                    status.get('id', ''),
                    status.get('name', '')
                )
                self.statuses_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статусы:\n{str(e)}")
    
    def load_types(self):
        """Загрузить типы патентов"""
        try:
            types = self.api_client.get_patent_types()
            
            for item in self.types_tree.get_children():
                self.types_tree.delete(item)
            
            for ptype in types:
                values = (
                    ptype.get('id', ''),
                    ptype.get('name', '')
                )
                self.types_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить типы:\n{str(e)}")
    
    def load_holders(self):
        """Загрузить правообладателей"""
        try:
            holders = self.api_client.get_rights_holders()
            
            for item in self.holders_tree.get_children():
                self.holders_tree.delete(item)
            
            for holder in holders:
                values = (
                    holder.get('id', ''),
                    holder.get('name', '')
                )
                self.holders_tree.insert("", tk.END, values=values)
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить правообладателей:\n{str(e)}")