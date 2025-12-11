import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime

from src.client.client import Client


ALL = 'Все'
BY_ID = 'По id'
BY_DATE = 'По дате'

ACTIVE_STATUS = 'Активен'
EXPIRED_STATUS = 'Истёк'


class ApplicationsWindow:
    def __init__(self, parent_frame, user, client: Client):
        self.parent_frame = parent_frame
        self.user = user
        self.client = client

        self.applications = []
        self.statuses = []

        self.filter_var = tk.StringVar(value="Все")
        self.search_var = tk.StringVar()
        self.filter_combobox = None
        self.tree = None

        self.table_items = []

        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        header_frame = tk.Frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header_frame, text="Управление заявками").pack(side=tk.LEFT)

        toolbar_frame = ttk.Frame(self.parent_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Button(toolbar_frame, text="Создать заявку", command=self.create_application).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(toolbar_frame, text="Редактировать", command=self.edit_application).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(toolbar_frame, text="Удалить", command=self.delete_application).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(toolbar_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=(0, 5))

        tk.Label(toolbar_frame, text="Фильтр:").pack(side=tk.LEFT, padx=(20, 5))
        self.filter_combobox = ttk.Combobox(toolbar_frame, textvariable=self.filter_var, state="readonly", width=20)
        self.filter_combobox.pack(side=tk.LEFT, padx=(0, 5))
        self.filter_combobox.bind("<<ComboboxSelected>>", lambda e: self.filter_applications())

        tk.Label(toolbar_frame, text="Поиск:").pack(side=tk.LEFT, padx=(20, 5))

        self.search_var.trace('w', lambda *args: self.filter_applications())
        tk.Entry(toolbar_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT)
        
        table_frame = tk.Frame(self.parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        vertical_scrollbar = tk.Scrollbar(table_frame, orient="vertical")
        vertical_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        horizontal_scrollbar = tk.Scrollbar(table_frame, orient="horizontal")
        horizontal_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        columns = ("id", "submission_date", "status", "documents", "employee", "author")
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
        self.tree.heading("submission_date", text="Дата подачи")
        self.tree.heading("status", text="Статус")
        self.tree.heading("documents", text="Документы")
        self.tree.heading("employee", text="Сотрудник")
        self.tree.heading("author", text="Автор")

        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("submission_date", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=150, anchor=tk.CENTER)
        self.tree.column("documents", width=300)
        self.tree.column("employee", width=120, anchor=tk.CENTER)
        self.tree.column("author", width=120, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_application())
    
    def load_data(self):
        try:
            self.applications = self.client.get_applications()
            self.statuses = self.client.get_statuses()

            statuses_names = [s.get('name') for s in self.statuses if s.get('name') not in [ACTIVE_STATUS, EXPIRED_STATUS]]
            combobox_values = [ALL, BY_ID, BY_DATE] + statuses_names

            self.filter_combobox['values'] = combobox_values

            self.update_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.table_items.clear()

        for application in self.applications:
            values = self.get_values_from_application(application)
            self.table_items.append(values)
            self.tree.insert("", tk.END, values=values, tags=(values[0],))
    
    def filter_applications(self):
        filter_param = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for values in self.table_items:
            if filter_param != ALL:
                if filter_param == BY_ID and search_text:
                    if search_text not in str(values[0]):
                        continue

                elif filter_param == BY_DATE and search_text:
                    if search_text not in values[1]:
                        continue

                else:
                    if filter_param != values[2]:
                        continue
            
            self.tree.insert("", tk.END, values=values, tags=(values[0],))

    def get_values_from_application(self, application):
        employee_full_name = self.client.get_employee_full_name(application.get('employee_id'))
        author_full_name = self.client.get_author_full_name(application.get('author_id'))
        return [
            application.get('id'),
            application.get('submission_date'),
            application.get('status').get('name'),
            application.get('documents'),
            employee_full_name,
            author_full_name
        ]
    
    def create_application(self):
        dialog = ApplicationDialog(self.parent_frame, self.client, self.statuses)
        passport = self.create_passport(dialog.passport_payload)

        if passport == -1:
            return

        author = self.create_author(dialog.author_payload, passport)

        if author == -1:
            return

        if dialog.application_payload:
            try:
                dialog.application_payload['author_id'] = author.get('id')
                self.client.create_application(dialog.application_payload)
                messagebox.showinfo("Успех", "Заявка создана успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать заявку:\n{str(e)}")
    
    def edit_application(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для редактирования")
            return
        
        app_id = int(self.tree.item(selected[0])['values'][0])
        app = next((a for a in self.applications if a['id'] == app_id), None)
        
        if not app:
            return
        
        dialog = ApplicationDialog(self.parent_frame, self.client, self.statuses, app)
        passport = self.create_passport(dialog.passport_payload)

        if passport == -1:
            return

        author = self.create_author(dialog.author_payload, passport)
        print(author)

        if author == -1:
            return

        if dialog.application_payload:
            try:
                dialog.application_payload['author_id'] = author.get('id')
                self.client.update_application(app_id, dialog.application_payload)
                messagebox.showinfo("Успех", "Заявка обновлена успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить заявку:\n{str(e)}")

    def create_passport(self, payload):
        if payload:
            try:
                series = payload.get('series')
                number = payload.get('number')
                is_exist, passport = self.is_passport_exist(series, number)

                if not is_exist:
                    return self.client.create_passport(payload)
                return passport
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить паспорт:\n{str(e)}")
                return -1

    def is_passport_exist(self, series: int, number: int):
        passports = self.client.get_passports()

        for passport in passports:
            if passport.get('series') == series and passport.get('number') == number:
                return True, passport
        return False, {}

    def create_author(self, payload, passport):
        if payload:
            try:
                name = payload.get('name')
                is_exist, author = self.is_author_exist(name, passport.get('id'))

                if not is_exist:
                    payload['passport_id'] = passport.get('id')
                    return self.client.create_author(payload)

                if author == -1:
                    messagebox.showerror("Ошибка", f"Существует автор с таким паспортом, но другим именем")
                    return -1

                return author
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить автора:\n{str(e)}")
                return -1

    def is_author_exist(self, name: str, passport_id: int):
        authors = self.client.get_authors()

        for author in authors:
            if author.get('name') == name and author.get('passport_id') == passport_id:
                return True, author
            elif author.get('name') != name and author.get('passport_id') == passport_id:
                return True, -1
        return False, {}
    
    def view_application(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        app_id = int(self.tree.item(selected[0])['values'][0])
        app = next((a for a in self.applications if a['id'] == app_id), None)
        
        if not app:
            return

        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"Заявка #{app_id}")
        view_window.geometry("600x500")

        main_frame = tk.Frame(view_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text=f"Заявка #{app_id}").pack(pady=(0, 20))
        
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("ID:", app.get('id', '')),
            ("Дата подачи:", app.get('submission_date', '')),
            ("Статус:", app.get('status', {}).get('name', 'Не указан') if app.get('status') else 'Не указан'),
            ("ID Сотрудника:", app.get('employee_id', '-')),
            ("ID Автора:", app.get('author_id', '-')),
            ("Документы:", app.get('documents', '')),
            ("Заключение эксперта:", app.get('expert_conclusion', '')),
        ]
        
        for i, (label, value) in enumerate(fields):
            tk.Label(info_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            tk.Label(info_frame, text=str(value)).grid(row=i, column=1, sticky=tk.W, pady=5)
        
        tk.Button(main_frame, text="Закрыть", command=view_window.destroy).pack(pady=(20, 0))
    
    def delete_application(self):
        selected = self.tree.selection()

        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для удаления")
            return
        
        application_id = int(self.tree.item(selected[0])['values'][0])
        patent_ids = self.get_patent_ids_to_delete(application_id)

        message_box_info = f"Вы уверены, что хотите удалить заявку №{application_id}"

        if len(patent_ids) > 0:
            message_box_info += ", будут удалены патенты с id: {patent_ids}?"
        else:
            message_box_info += "?"
        
        if messagebox.askyesno("Подтверждение", message_box_info):
            try:
                self.client.delete_application(application_id)
                messagebox.showinfo("Успех", "Заявка удалена успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заявку:\n{str(e)}")

    def get_patent_ids_to_delete(self, application_id: int):
        patents = self.client.get_patents()
        ids = []

        for patent in patents:
            if patent.get('application_id') == application_id:
                ids.append(patent.get('id'))
        return ids


DIALOG_SIZE = '400x580'


class ApplicationDialog:
    def __init__(self, parent, client:Client, statuses, application=None):
        self.client = client
        self.statuses = statuses
        self.application = application

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать заявку" if not application else "Редактировать заявку")
        self.dialog.geometry(DIALOG_SIZE)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.full_name_var = tk.StringVar()
        self.passport_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.documents_text = None
        self.conclusion_text = None
        self.calendar = None

        self.passport_payload = None
        self.author_payload = None
        self.application_payload = None
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="ФИО автора:").pack(anchor=tk.W, pady=(0, 5))
        full_name_entry = tk.Entry(frame, textvariable=self.full_name_var)
        full_name_entry.pack(fill=tk.X, pady=(0, 15))

        tk.Label(frame, text="Серия и номер паспорта (через пробел):").pack(anchor=tk.W, pady=(0, 5))
        passport_entry = tk.Entry(frame, textvariable=self.passport_var)
        passport_entry.pack(fill=tk.X, pady=(0, 15))

        tk.Label(frame, text="Дата подачи:").pack(anchor=tk.W, pady=(0, 5))
        self.calendar = DateEntry(frame, selectmode='day', date_pattern='yyyy-mm-dd')
        self.calendar.pack(fill=tk.X, pady=(0, 15))

        tk.Label(frame, text="Документы:").pack(anchor=tk.W, pady=(0, 5))
        documents_var = tk.StringVar(value=self.application.get('documents', '') if self.application else '')
        self.documents_text = tk.Text(frame, height=5)
        self.documents_text.pack(fill=tk.X, pady=(0, 15))
        self.documents_text.insert('1.0', documents_var.get())

        tk.Label(frame, text="Заключение эксперта:").pack(anchor=tk.W, pady=(0, 5))
        conclusion_var = tk.StringVar(value=self.application.get('expert_conclusion', '') if self.application else '')
        self.conclusion_text = tk.Text(frame, height=5)
        self.conclusion_text.pack(fill=tk.X, pady=(0, 15))
        self.conclusion_text.insert('1.0', conclusion_var.get())

        tk.Label(frame, text="Статус:").pack(anchor=tk.W, pady=(0, 5))
        combobox_values = self.get_status_names()
        status_combobox = ttk.Combobox(frame, textvariable=self.status_var, state="readonly", values=combobox_values)
        status_combobox.pack(fill=tk.X, pady=(0, 15))

        if self.application:
            author = self.client.get_author(self.application.get('author_id'))
            full_name_entry.insert(0, author.get('full_name'))

            passport_series = str(author.get('passport').get('series'))

            for _ in range(4 - len(passport_series)):
                passport_series = '0' + passport_series

            passport_number = str(author.get('passport').get('number'))

            for _ in range(6 - len(passport_number)):
                passport_number = '0' + passport_number

            passport_entry.insert(0, f'{passport_series} {passport_number}')

            date = self.application.get('submission_date')
            self.calendar.set_date(date)

            status_combobox.set(self.application.get('status').get('name'))
        else:
            status_combobox.set(combobox_values[0])

        buttons_frame = tk.Frame(frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(buttons_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, expand=True, fill=tk.X,
                                                                           padx=(0, 5))

        tk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, expand=True,
                                                                                  fill=tk.X, padx=(5, 0))

    def get_status_names(self):
        return [s.get('name') for s in self.statuses if s.get('name') not in [ACTIVE_STATUS, EXPIRED_STATUS]]

    def save(self):
        if not self.full_name_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите имя автора")
            return

        if not self.passport_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите серию и номер паспорта")
            return

        is_valid, idents = self.is_passport_valid()

        if not is_valid:
            messagebox.showwarning("Предупреждение", "Неверная серия или номер паспорта")
            return

        if not self.status_var.get().strip():
            messagebox.showwarning("Предупреждение", "Укажите статус")
            return

        status_id = self.get_status_id()

        if status_id == -1:
            messagebox.showwarning("Предупреждение", "Не существует статуса с таким названием")
            return

        self.passport_payload = {'series': int(idents[0]), 'number': int(idents[1])}
        self.author_payload = {'full_name': self.full_name_var.get().strip()}

        if self.documents_text:
            self.application_payload = {'documents': self.documents_text.get('1.0', tk.END).strip()}

        if self.conclusion_text:
            self.application_payload["expert_conclusion"] = self.conclusion_text.get('1.0', tk.END).strip()

        self.application_payload['submission_date'] = self.calendar.get()
        self.application_payload['status_id'] = status_id
        self.dialog.destroy()

    def is_passport_valid(self):
        password_parts = self.passport_var.get().strip().split()

        if len(password_parts) != 2:
            return False, (0, 0)

        series = password_parts[0]
        number = password_parts[1]

        if len(series) != 4 or len(number) != 6 or not series.isdigit() or not number.isdigit():
            return False, (0, 0)
        return True, (series, number)

    def get_status_id(self):
        for status in self.statuses:
            if status.get('name') == self.status_var.get().strip():
                return status.get('id')
        return -1
