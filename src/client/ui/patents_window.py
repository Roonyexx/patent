import tkinter as tk
from tkinter import ttk, messagebox

from datetime import datetime, date
import src.client.config as config
from src.client.client import Client


class PatentsWindow:
    def __init__(self, parent_frame, client: Client):
        self.parent_frame = parent_frame
        self.client = client

        self.filter_var = tk.StringVar(value="Все")
        self.search_var = tk.StringVar()
        self.filter_combobox = None
        self.tree = None

        self.patents = []
        self.patent_types = []
        self.statuses = []
        self.applications = []

        self.filter_params = ['Все', 'По ФИО автора', 'По ФИО сотрудника', 'По названию']

        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        header_frame = tk.Frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text="Управление патентами",).pack(side=tk.LEFT)

        toolbar_frame = tk.Frame(self.parent_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(toolbar_frame, text="Создать патент", command=self.create_patent).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(toolbar_frame, text="Редактировать", command=self.edit_patent).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(toolbar_frame, text="Удалить", command=self.delete_patent).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(toolbar_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=(0, 5))

        tk.Label(toolbar_frame, text="Фильтр:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_combobox = ttk.Combobox(toolbar_frame, textvariable=self.filter_var, state="readonly", width=20)
        self.filter_combobox.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_patents())

        tk.Label(toolbar_frame, text="Поиск:").pack(side=tk.LEFT, padx=(20, 5))

        self.search_var.trace('w', lambda *args: self.filter_patents())
        tk.Entry(toolbar_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        
        table_frame = tk.Frame(self.parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        vertical_scrollbar = tk.Scrollbar(table_frame, orient="vertical")
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        horizontal_scrollbar = tk.Scrollbar(table_frame, orient="horizontal")
        horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("id", "title", "issue_date", "expiration_date", "type", "status", "author", "holder")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set
        )
        
        vertical_scrollbar.config(command=self.tree.yview)
        horizontal_scrollbar.config(command=self.tree.xview)
        
        self.tree.heading("#0", text="")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("issue_date", text="Дата выдачи")
        self.tree.heading("expiration_date", text="Дата истечения")
        self.tree.heading("type", text="Тип")
        self.tree.heading("status", text="Статус")
        self.tree.heading("author", text="Автор")
        self.tree.heading("holder", text="Правообладатель")
        
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("title", width=250)
        self.tree.column("issue_date", width=120, anchor=tk.CENTER)
        self.tree.column("expiration_date", width=120, anchor=tk.CENTER)
        self.tree.column("type", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("author", width=100, anchor=tk.CENTER)
        self.tree.column("holder", width=100, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_patent())
    
    def load_data(self):
        try:
            self.patents = self.client.get_patents()
            self.patent_types = self.client.get_patent_types()
            self.statuses = self.client.get_statuses()
            self.applications = self.client.get_applications()

            self.filter_params += [s['name'] for s in self.statuses]
            self.filter_combobox['values'] = self.filter_params

            self.update_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for patent in self.patents:
            is_expired = False
            if patent.get('expiration_date'):
                try:
                    exp_date = datetime.strptime(patent['expiration_date'], '%Y-%m-%d').date()

                    if exp_date < date.today():
                        is_expired = True
                except Exception as e:
                    messagebox.showwarning('Предупреждение', str(e))
            
            values = (
                patent.get('id', ''),
                patent.get('title', ''),
                patent.get('issue_date', ''),
                patent.get('expiration_date', ''),
                config.PATENT_TYPE_NAMES.get(patent.get('patent_type_id'), 'Неизвестно'),
                patent.get('status', {}).get('name', 'Не указан') if patent.get('status') else 'Не указан',
                'author',
                patent.get('rights_holder_id', '-')
            )
            
            item = self.tree.insert("", tk.END, values=values, tags=(patent.get('id'),))
            
            if is_expired:
                self.tree.item(item, tags=('expired',))
        
        self.tree.tag_configure('expired', background='#ffcccc')

    def get_author_name(self, app_id):
        author_id = 0

        for app in self.applications:
            if app.get('id') == app_id:
                author_id = app.get('author_id')

        authors = self.client.get_authors()
    
    def filter_patents(self):
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for patent in self.patents:
            if search_text:
                title = (patent.get('title') or '').lower()
                if search_text not in title:
                    continue
            
            is_expired = False
            if patent.get('expiration_date'):
                try:
                    exp_date = datetime.strptime(patent['expiration_date'], '%Y-%m-%d').date()
                    if exp_date < date.today():
                        is_expired = True
                except:
                    pass
            
            values = (
                patent.get('id', ''),
                patent.get('title', ''),
                patent.get('issue_date', ''),
                patent.get('expiration_date', ''),
                config.PATENT_TYPE_NAMES.get(patent.get('patent_type_id'), 'Неизвестно'),
                patent.get('status', {}).get('name', 'Не указан') if patent.get('status') else 'Не указан',
                patent.get('rights_holder_id', '-')
            )
            
            item = self.tree.insert("", tk.END, values=values, tags=(patent.get('id'),))
            
            if is_expired:
                self.tree.item(item, tags=('expired',))
        
        self.tree.tag_configure('expired', background='#ffcccc')
    
    def show_expired(self):
        try:
            expired = self.client.get_expired_patents()
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for patent in expired:
                values = (
                    patent.get('id', ''),
                    patent.get('title', ''),
                    patent.get('issue_date', ''),
                    patent.get('expiration_date', ''),
                    config.PATENT_TYPE_NAMES.get(patent.get('patent_type_id'), 'Неизвестно'),
                    patent.get('status', {}).get('name', 'Не указан') if patent.get('status') else 'Не указан',
                    patent.get('rights_holder_id', '-')
                )
                
                item = self.tree.insert("", tk.END, values=values, tags=('expired',))
            
            self.tree.tag_configure('expired', background='#ffcccc')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить истекшие патенты:\n{str(e)}")
    
    def create_patent(self):
        dialog = PatentDialog(self.parent_frame, self.client, self.patent_types, self.statuses, self.applications)
        if dialog.result:
            try:
                self.client.create_patent(dialog.result)
                messagebox.showinfo("Успех", "Патент создан успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать патент:\n{str(e)}")
    
    def edit_patent(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите патент для редактирования")
            return
        
        patent_id = int(self.tree.item(selected[0])['values'][0])
        patent = next((p for p in self.patents if p['id'] == patent_id), None)
        
        if not patent:
            return
        
        dialog = PatentDialog(self.parent_frame, self.client, self.patent_types, self.statuses, self.applications, patent)
        if dialog.result:
            try:
                self.client.update_patent(patent_id, dialog.result)
                messagebox.showinfo("Успех", "Патент обновлен успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить патент:\n{str(e)}")
    
    def view_patent(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        patent_id = int(self.tree.item(selected[0])['values'][0])
        patent = next((p for p in self.patents if p['id'] == patent_id), None)
        
        if not patent:
            return
        
        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"Патент #{patent_id}")
        view_window.geometry("700x600")
        
        main_frame = ttk.Frame(view_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=f"Патент #{patent_id}", style="Title.TLabel").pack(pady=(0, 20))
        
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("ID:", patent.get('id', '')),
            ("Название:", patent.get('title', '')),
            ("Дата выдачи:", patent.get('issue_date', '')),
            ("Дата истечения:", patent.get('expiration_date', '')),
            ("Тип:", config.PATENT_TYPE_NAMES.get(patent.get('patent_type_id'), 'Неизвестно')),
            ("Статус:", patent.get('status', {}).get('name', 'Не указан') if patent.get('status') else 'Не указан'),
            ("ID Правообладателя:", patent.get('rights_holder_id', '-')),
            ("ID Заявки:", patent.get('application_id', '-')),
            ("Описание:", patent.get('description', '')),
        ]
        
        for i, (label, value) in enumerate(fields):
            ttk.Label(info_frame, text=label, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10)
            )
            
            value_label = ttk.Label(info_frame, text=str(value), wraplength=400)
            value_label.grid(row=i, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(
            main_frame,
            text="Закрыть",
            style="Secondary.TButton",
            command=view_window.destroy
        ).pack(pady=(20, 0))
    
    def delete_patent(self):
        """Удалить патент"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите патент для удаления")
            return
        
        patent_id = int(self.tree.item(selected[0])['values'][0])
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить патент #{patent_id}?"):
            try:
                self.client.delete_patent(patent_id)
                messagebox.showinfo("Успех", "Патент удален успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить патент:\n{str(e)}")


class PatentDialog:
    def __init__(self, parent, api_client: Client, patent_types, statuses, applications, patent=None):
        self.description_text = None
        self.type_var = tk.StringVar()
        self.application_var = tk.StringVar()
        self.holder_entry = None
        self.title_entry = None
        self.result = None
        self.api_client = api_client
        self.patent_types = patent_types
        self.statuses = statuses
        self.applications = applications
        self.patent = patent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать патент" if not patent else "Редактировать патент")
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding="20")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        ttk.Label(scrollable_frame, text="Название:").pack(anchor=tk.W, pady=(0, 5))
        tk.StringVar(value=self.patent.get('title', '') if self.patent else '')
        self.title_entry = ttk.Entry(scrollable_frame)
        self.title_entry.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(scrollable_frame, text="Описание:").pack(anchor=tk.W, pady=(0, 5))
        self.description_text = tk.Text(scrollable_frame, height=5, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL))
        self.description_text.pack(fill=tk.X, pady=(0, 15))

        if self.patent and self.patent.get('description'):
            self.description_text.insert('1.0', self.patent['description'])
        
        ttk.Label(scrollable_frame, text="Тип патента:").pack(anchor=tk.W, pady=(0, 5))
        type_combo = ttk.Combobox(scrollable_frame, textvariable=self.type_var, state="readonly")
        type_combo['values'] = [pt['name'] for pt in self.patent_types]
        type_combo.pack(fill=tk.X, pady=(0, 15))
        
        if self.patent and self.patent.get('patent_type_id'):
            type_name = config.PATENT_TYPE_NAMES.get(self.patent['patent_type_id'], '')
            type_combo.set(type_name)
        elif self.patent_types:
            type_combo.current(0)

        ttk.Label(scrollable_frame, text="Заявка:").pack(anchor=tk.W, pady=(0, 5))
        app_combo = ttk.Combobox(scrollable_frame, textvariable=self.application_var, state="readonly")
        app_combo['values'] = [f"Заявка #{app['id']}" for app in self.applications]
        app_combo.pack(fill=tk.X, pady=(0, 15))
        
        if self.patent and self.patent.get('application_id'):
            app_combo.set(f"Заявка #{self.patent['application_id']}")
        elif self.applications:
            app_combo.current(0)

        ttk.Label(scrollable_frame, text="ID Правообладателя:").pack(anchor=tk.W, pady=(0, 5))
        self.holder_entry = ttk.Entry(scrollable_frame)
        self.holder_entry.pack(fill=tk.X, pady=(0, 15))

        buttons_frame = ttk.Frame(scrollable_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            buttons_frame,
            text="Сохранить",
            style="Success.TButton",
            command=self.save
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="Отмена",
            style="Secondary.TButton",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def save(self):
        if not self.title_entry.get().strip():
            messagebox.showwarning("Предупреждение", "Введите название патента")
            return
        
        if not self.application_var.get():
            messagebox.showwarning("Предупреждение", "Выберите заявку")
            return
        
        type_name = self.type_var.get()
        type_id = next((k for k, v in config.PATENT_TYPE_NAMES.items() if v == type_name), 1)
        
        app_text = self.application_var.get()
        app_id = int(app_text.split('#')[1])
        
        data = {
            "title": self.title_entry.get().strip(),
            "description": self.description_text.get('1.0', tk.END).strip(),
            "patent_type_id": type_id,
            "application_id": app_id,
            "rights_holder_id": int(self.holder_entry.get() or 0)
        }
        
        self.result = data
        self.dialog.destroy()
