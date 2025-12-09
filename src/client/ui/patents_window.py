import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date

import src.client.config as config
from src.client.client import Client
from src.client.ui.export_patent_window import ExportPatentWindow


ALL = 'Все'
BY_AUTHOR_FULL_NAME = 'По ФИО автора'
BY_EMPLOYEE_FULL_NAME = 'По ФИО сотрудника'
BY_TITLE = 'По названию'

ACTIVE_STATUS = 'Активен'
EXPIRED_STATUS = 'Истёк'

def is_patent_expired(expiration_date: str):
    if expiration_date:
        try:
            formatted_expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d').date()

            if formatted_expiration_date < date.today():
                return True
        except Exception as e:
            print(str(e))

    return False


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

        self.patent_table_items = []
        self.status_names = []
        self.filter_params = [ALL, BY_AUTHOR_FULL_NAME, BY_EMPLOYEE_FULL_NAME, BY_TITLE]

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
        
        columns = ("id", "title", "issue_date", "expiration_date", "type", "status", "employee", "author", "holder")
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
        self.tree.heading("employee", text="Сотрудник")
        self.tree.heading("author", text="Автор")
        self.tree.heading("holder", text="Правообладатель")
        
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("title", width=250)
        self.tree.column("issue_date", width=120, anchor=tk.CENTER)
        self.tree.column("expiration_date", width=120, anchor=tk.CENTER)
        self.tree.column("type", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("employee", width=100, anchor=tk.CENTER)
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

            self.status_names = [s['name'] for s in self.statuses]
            self.filter_params += self.status_names
            self.filter_combobox['values'] = self.filter_params

            self.update_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.patent_table_items.clear()
        
        for patent in self.patents:
            is_expired = is_patent_expired(patent.get('expiration_date'))

            if is_expired:
                expired_status_id = self.client.get_status_id_by_name(EXPIRED_STATUS)
                self.update_patent_status(patent, expired_status_id)

            values = self.get_values_from_patent(patent)
            self.patent_table_items.append(values)
            item_id = self.tree.insert("", tk.END, values=values, tags=(values[0],))

            if is_expired:
                self.tree.item(item_id, tags=('expired',))
        
        self.tree.tag_configure('expired', background='#ffcccc')

    def update_patent_status(self, patent, status_id: int):
        patent['status_id'] = status_id
        print(patent)
        self.client.update_patent(patent.get('id'), patent)
    
    def filter_patents(self):
        filter_param = self.filter_var.get().strip()
        search_text = self.search_var.get().lower()

        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        for values in self.patent_table_items:
            if filter_param != ALL:
                if filter_param == BY_AUTHOR_FULL_NAME and search_text:
                    author_full_name = values[7].lower()

                    if search_text not in author_full_name:
                        continue

                elif filter_param == BY_EMPLOYEE_FULL_NAME and search_text:
                    employee_full_name = values[6].lower()

                    if search_text not in employee_full_name:
                        continue

                elif filter_param == BY_TITLE and search_text:
                    title = values[1].lower()

                    if search_text not in title:
                        continue

                else:
                    status = values[5]

                    if filter_param != status:
                        continue

            item_id = self.tree.insert("", tk.END, values=values, tags=(values[0],))

            if is_patent_expired(values[3]):
                self.tree.item(item_id, tags=('expired',))
        
        self.tree.tag_configure('expired', background='#ffcccc')

    def get_values_from_patent(self, patent):
        patent_type_name = self.client.get_patent_type_name(patent.get('patent_type_id'))
        patent_status = self.client.get_status(patent.get('status_id')).get('name')
        application = self.client.get_application(patent.get('application_id'))
        employee_full_name = self.client.get_employee_full_name(application.get('employee_id'))
        author_full_name = self.client.get_author_full_name(application.get('author_id'))
        rights_holder_name = self.client.get_rights_holder(patent.get('rights_holder_id')).get('name')
        return [
            patent.get('id'),
            patent.get('title'),
            patent.get('issue_date'),
            patent.get('expiration_date'),
            patent_type_name,
            patent_status,
            employee_full_name,
            author_full_name,
            rights_holder_name
        ]
    
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
                
                self.tree.insert("", tk.END, values=values, tags=('expired',))
            
            self.tree.tag_configure('expired', background='#ffcccc')
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить истекшие патенты:\n{str(e)}")
    
    def create_patent(self):
        dialog = PatentDialog(self.parent_frame, self.client, self.patent_types, self.statuses, self.applications, self.patents)
        rights_holder = self.create_rights_holder(dialog.rights_holder_payload)

        if rights_holder == -1:
            return

        if dialog.patent_payload:
            try:
                dialog.patent_payload['rights_holder_id'] = rights_holder.get('id')
                dialog.patent_payload['issue_date'] = str(datetime.today().date())
                self.client.create_patent(dialog.patent_payload)
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
        rights_holder = self.create_rights_holder(dialog.rights_holder_payload)

        if rights_holder == -1:
            return

        if dialog.patent_payload:
            try:
                dialog.patent_payload['rights_holder_id'] = rights_holder.get('id')
                self.client.update_patent(patent_id, dialog.patent_payload)
                messagebox.showinfo("Успех", "Патент обновлен успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить патент:\n{str(e)}")

    def create_rights_holder(self, payload):
        if payload:
            try:
                name = payload.get('name')
                is_exist, right_holder = self.is_rights_holder_exist(name)

                if not is_exist:
                    return self.client.create_rights_holder(payload)
                return right_holder
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить правообладателя:\n{str(e)}")
                return -1

    def is_rights_holder_exist(self, name: str):
        holders = self.client.get_rights_holders()

        for holder in holders:
            if holder.get('name') == name:
                return True, holder
        return False, {}
    
    def view_patent(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0])['values']
        
        window = tk.Toplevel(self.parent_frame)
        window.title("Информация о патенте")
        window.geometry("400x480")
        
        main_frame = tk.Frame(window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text=f"Патент №{values[0]}").pack(pady=(0, 20))
        
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = {
            "id": values[0],
            "Название": values[1],
            "Дата выдачи": values[2],
            "Дата истечения": values[3],
            "Тип": values[4],
            "Статус": values[5],
            "Сотрудник": values[6],
            "Автор": values[7],
            "Правообладатель": values[8],
        }

        row = 0

        for label, value in fields.items():
            tk.Label(info_frame, text=label, font=('Segoe UI', 10, 'bold')).grid(
                row=row, column=0, sticky=tk.W, pady=5, padx=(0, 10)
            )

            value_label = ttk.Label(info_frame, text=str(value), wraplength=400)
            value_label.grid(row=row, column=1, sticky=tk.W, pady=5)
            row += 1

        tk.Button(main_frame, text="Экспорт", command=lambda: self.show_export_window(window, fields)).pack(fill='x',
                                                                                                            pady=(20, 0))
        tk.Button(main_frame, text="Закрыть", command=window.destroy).pack(fill='x', pady=(20, 0))
    
    def delete_patent(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите патент для удаления")
            return
        
        patent_id = int(self.tree.item(selected[0])['values'][0])
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить патент №{patent_id}?"):
            try:
                self.client.delete_patent(patent_id)
                messagebox.showinfo("Успех", "Патент удален успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить патент:\n{str(e)}")

    def show_export_window(self, parent, values):
        ExportPatentWindow(parent, values).show()


APPLICATION_NAME_SEPARATOR = '-'
DIALOG_SIZE = '400x500'


class PatentDialog:
    def __init__(self, parent, client: Client, patent_types, statuses, applications, patents, patent=None):
        self.client = client
        self.patent_types = patent_types
        self.statuses = statuses
        self.applications = applications
        self.patents = patents
        self.patent = patent
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать патент" if not patent else "Редактировать патент")
        self.dialog.geometry(DIALOG_SIZE)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.application_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.description_text = None
        self.rights_holder_entry = None
        self.title_entry = None

        self.rights_holder_payload = None
        self.patent_payload = None
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        frame = tk.Frame(self.dialog)
        frame.pack(fill=tk.X, pady=10, padx=10)
        
        tk.Label(frame, text="Название:").pack(anchor=tk.W, pady=(0, 5))
        tk.StringVar(value=self.patent.get('title', '') if self.patent else '')
        self.title_entry = tk.Entry(frame)
        self.title_entry.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(frame, text="Описание:").pack(anchor=tk.W, pady=(0, 5))
        self.description_text = tk.Text(frame, height=5, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL))
        self.description_text.pack(fill=tk.X, pady=(0, 15))

        if self.patent and self.patent.get('description'):
            self.description_text.insert('1.0', self.patent['description'])
        
        tk.Label(frame, text="Тип патента:").pack(anchor=tk.W, pady=(0, 5))
        type_combobox = ttk.Combobox(frame, textvariable=self.type_var, state="readonly")
        type_combobox['values'] = [pt['name'] for pt in self.patent_types]
        type_combobox.pack(fill=tk.X, pady=(0, 15))
        
        if self.patent and self.patent.get('patent_type_id'):
            type_name = self.get_patent_type_name(self.patent.get('patent_type_id'))
            type_combobox.set(type_name)
        elif self.patent_types:
            type_combobox.current(0)

        tk.Label(frame, text="Статус:").pack(anchor=tk.W, pady=(0, 5))
        status_combobox = ttk.Combobox(frame, textvariable=self.status_var, state="readonly")
        status_combobox['values'] = [ACTIVE_STATUS, EXPIRED_STATUS]
        status_combobox.pack(fill=tk.X, pady=(0, 15))

        if self.patent and self.patent.get('status_id'):
            status_name = self.get_status_name(self.patent.get('patent_type_id'))
            status_combobox.set(status_name)
        elif self.patent_types:
            status_combobox.current(0)

        tk.Label(frame, text="Заявка:").pack(anchor=tk.W, pady=(0, 5))
        app_combo = ttk.Combobox(frame, textvariable=self.application_var, state="readonly")
        app_combo['values'] = [f"Заявка{APPLICATION_NAME_SEPARATOR}{application.get('id')}"
                               for application in self.applications]
        app_combo.pack(fill=tk.X, pady=(0, 15))
        
        if self.patent and self.patent.get('application_id'):
            app_combo.set(f"Заявка{APPLICATION_NAME_SEPARATOR}{self.patent.get('application_id')}")
        elif self.applications:
            app_combo.current(0)

        tk.Label(frame, text="Правообладатель:").pack(anchor=tk.W, pady=(0, 5))
        self.rights_holder_entry = tk.Entry(frame)
        self.rights_holder_entry.pack(fill=tk.X, pady=(0, 15))

        buttons_frame = tk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(buttons_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, expand=True,
                                                                           fill=tk.X, padx=(0, 5))
        tk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, expand=True,
                                                                                  fill=tk.X, padx=(5, 0))

    def get_patent_type_name(self, patent_type_id: int):
        for patent_type in self.patent_types:
            if patent_type.get('id') == patent_type_id:
                return patent_type.get('name')
        return '-'

    def get_status_name(self, status_id: int):
        for status in self.statuses:
            if status.get('id') == status_id:
                return status.get('name')
        return '-'
    
    def save(self):
        if not self.rights_holder_entry.get().strip():
            messagebox.showwarning("Предупреждение", "Введите правообладателя")
            return

        if not self.title_entry.get().strip():
            messagebox.showwarning("Предупреждение", "Введите название патента")
            return

        if not self.is_title_valid():
            messagebox.showwarning("Предупреждение", "Патент с таким названием уже существует")
            return
        
        if not self.application_var.get():
            messagebox.showwarning("Предупреждение", "Выберите заявку")
            return

        self.rights_holder_payload = {'name': self.rights_holder_entry.get().strip()}

        patent_type_id = self.client.get_patent_type_id_by_name(self.type_var.get().strip())
        application_id = int(self.application_var.get().strip().split(APPLICATION_NAME_SEPARATOR)[1])
        status_id = self.client.get_status_id_by_name(self.status_var.get().strip())
        
        self.patent_payload = {
            "title": self.title_entry.get().strip(),
            "description": self.description_text.get('1.0', tk.END).strip(),
            "patent_type_id": patent_type_id,
            "application_id": application_id,
            "status_id": status_id
        }
        self.dialog.destroy()

    def is_title_valid(self):
        for patent in self.patents:
            if patent.get('title') == self.title_entry.get().strip():
                return False
        return True
