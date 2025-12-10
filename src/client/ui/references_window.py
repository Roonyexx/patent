import tkinter as tk
from tkinter import ttk, messagebox

import src.client.config as config
from src.client.client import Client


class ReferencesWindow:

    def __init__(self, parent_frame, api_client: Client):
        self.parent_frame = parent_frame
        self.api_client = api_client

        self.employees = []
        self.authors = []

        self.positions = []
        self.passports = []

        self.emp_full_name_var = tk.StringVar()
        self.emp_passport_var = tk.StringVar()
        self.emp_position_var = tk.StringVar()

        self.author_search_var = tk.StringVar()
        self.author_passport_var = tk.StringVar()

        self.create_widgets()
        self.load_positions()
        self.load_passports()
        self.load_data()

    def create_widgets(self):
        """Создать виджеты"""
        header_frame = ttk.Frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="",
            style="Subtitle.TLabel"
        )
        title_label.pack(side=tk.LEFT)

        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.employees_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.employees_frame, text="Сотрудники")

        self.authors_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.authors_frame, text="Авторы")

        self.create_employees_tab()
        self.create_authors_tab()

    def load_positions(self):
        try:
            self.positions = self.api_client.get_positions()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить должности:\n{str(e)}")

    def load_passports(self):
        try:
            self.passports = self.api_client.get_passports()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить паспорта:\n{str(e)}")

    def get_position_name(self, position_id):
        """Получить название должности по ID"""
        for p in self.positions:
            if p['id'] == position_id:
                return p['name']
        return str(position_id)

    def get_passport_string(self, passport_id):
        """Получить строку паспорта (серия номер) по ID"""
        for p in self.passports:
            if p['id'] == passport_id:
                return f"{p['series']} {p['number']}"
        return str(passport_id)

    def create_employees_tab(self):
        """Создать вкладку сотрудников"""
        toolbar_frame = ttk.Frame(self.employees_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar_frame, text="Редактировать", command=self.edit_employee).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Удалить", command=self.delete_employee).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Обновить", command=self.load_employees).pack(side=tk.LEFT, padx=(0, 5))

        filter_frame = ttk.Frame(self.employees_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filter_frame, text="ФИО:").pack(side=tk.LEFT, padx=(0, 5))
        self.emp_full_name_var.trace('w', lambda *args: self.filter_employees())
        ttk.Entry(filter_frame, textvariable=self.emp_full_name_var, width=20).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(filter_frame, text="Паспорт (серия номер):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(filter_frame, textvariable=self.emp_passport_var, width=15).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(filter_frame, text="Должность:").pack(side=tk.LEFT, padx=(0, 5))
        positions_names = [p['name'] for p in self.positions] if self.positions else []
        ttk.Combobox(filter_frame, textvariable=self.emp_position_var, values=positions_names, width=20).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(filter_frame, text="Применить фильтры", command=self.filter_employees).pack(side=tk.LEFT)

        table_frame = ttk.Frame(self.employees_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("id", "full_name", "employment_date", "phone_number", "position", "passport")
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
        self.employees_tree.heading("position", text="Должность")
        self.employees_tree.heading("passport", text="Паспорт")

        self.employees_tree.column("#0", width=0, stretch=False)
        self.employees_tree.column("id", width=50, anchor=tk.CENTER)
        self.employees_tree.column("full_name", width=200)
        self.employees_tree.column("employment_date", width=120, anchor=tk.CENTER)
        self.employees_tree.column("phone_number", width=120)
        self.employees_tree.column("position", width=150)
        self.employees_tree.column("passport", width=120)

        self.employees_tree.pack(fill=tk.BOTH, expand=True)
        self.employees_tree.bind("<Double-1>", lambda e: self.view_employee())

    def load_employees(self):
        try:
            self.employees = self.api_client.get_employees()
            self.update_employees_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить сотрудников:\n{str(e)}")

    def update_employees_table(self):
        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)

        for emp in self.employees:
            values = (
                emp.get('id', ''),
                emp.get('full_name', ''),
                emp.get('employment_date', ''),
                emp.get('phone_number', ''),
                self.get_position_name(emp.get('position_id')),
                self.get_passport_string(emp.get('passport_id'))
            )
            self.employees_tree.insert("", tk.END, values=values)

    def filter_employees(self):
        search_full_name = self.emp_full_name_var.get().lower()
        search_passport = self.emp_passport_var.get().strip()
        search_position_name = self.emp_position_var.get()

        search_position_id = next((p['id'] for p in self.positions if p['name'] == search_position_name), None) if search_position_name else None

        filtered = []
        for emp in self.employees:
            if search_full_name and search_full_name not in (emp.get('full_name') or '').lower():
                continue

            if search_passport:
                passport_str = self.get_passport_string(emp.get('passport_id'))
                if search_passport not in passport_str:
                    continue

            if search_position_id and search_position_id != emp.get('position_id'):
                continue

            filtered.append(emp)

        for item in self.employees_tree.get_children():
            self.employees_tree.delete(item)

        for emp in filtered:
            values = (
                emp.get('id', ''),
                emp.get('full_name', ''),
                emp.get('employment_date', ''),
                emp.get('phone_number', ''),
                self.get_position_name(emp.get('position_id')),
                self.get_passport_string(emp.get('passport_id'))
            )
            self.employees_tree.insert("", tk.END, values=values)

    def edit_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для редактирования")
            return

        emp_id = int(self.employees_tree.item(selected[0])['values'][0])
        emp = next((e for e in self.employees if e['id'] == emp_id), None)

        if not emp:
            return

        dialog = EmployeeDialog(self.parent_frame, self.positions, self.passports, emp)
        if dialog.employee_payload:
            try:
                self.api_client.update_employee(emp_id, dialog.employee_payload)
                messagebox.showinfo("Успех", "Сотрудник обновлен успешно!")
                self.load_employees()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить сотрудника:\n{str(e)}")

    def delete_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите сотрудника для удаления")
            return

        emp_id = int(self.employees_tree.item(selected[0])['values'][0])

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить сотрудника #{emp_id}?"):
            try:
                self.api_client.delete_employee(emp_id)
                messagebox.showinfo("Успех", "Сотрудник удален успешно!")
                self.load_employees()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить сотрудника:\n{str(e)}")

    def view_employee(self):
        selected = self.employees_tree.selection()
        if not selected:
            return

        emp_id = int(self.employees_tree.item(selected[0])['values'][0])
        emp = next((e for e in self.employees if e['id'] == emp_id), None)

        if not emp:
            return

        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"Сотрудник #{emp_id}")
        view_window.geometry("600x400")

        main_frame = tk.Frame(view_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text=f"Сотрудник #{emp_id}").pack(pady=(0, 20))

        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", emp.get('id', '')),
            ("ФИО:", emp.get('full_name', '')),
            ("Дата трудоустройства:", emp.get('employment_date', '')),
            ("Телефон:", emp.get('phone_number', '')),
            ("Должность:", self.get_position_name(emp.get('position_id'))),
            ("Паспорт:", self.get_passport_string(emp.get('passport_id'))),
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(info_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            tk.Label(info_frame, text=str(value)).grid(row=i, column=1, sticky=tk.W, pady=5)

        tk.Button(main_frame, text="Закрыть", command=view_window.destroy).pack(pady=(20, 0))

    def create_authors_tab(self):
        """Создать вкладку авторов"""
        toolbar_frame = ttk.Frame(self.authors_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar_frame, text="Создать автора", command=self.create_author).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Редактировать", command=self.edit_author).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Удалить", command=self.delete_author).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Обновить", command=self.load_authors).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(toolbar_frame, text="Поиск по ФИО:").pack(side=tk.LEFT, padx=(20, 5))
        self.author_search_var.trace('w', lambda *args: self.filter_authors())
        ttk.Entry(toolbar_frame, textvariable=self.author_search_var, width=20).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(toolbar_frame, text="Паспорт (серия номер):").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Entry(toolbar_frame, textvariable=self.author_passport_var, width=15).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(toolbar_frame, text="Применить фильтры", command=self.filter_authors).pack(side=tk.LEFT)

        table_frame = ttk.Frame(self.authors_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("id", "full_name", "passport")
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
        self.authors_tree.heading("passport", text="Паспорт")

        self.authors_tree.column("#0", width=0, stretch=False)
        self.authors_tree.column("id", width=100, anchor=tk.CENTER)
        self.authors_tree.column("full_name", width=400)
        self.authors_tree.column("passport", width=150, anchor=tk.CENTER)

        self.authors_tree.pack(fill=tk.BOTH, expand=True)
        self.authors_tree.bind("<Double-1>", lambda e: self.view_author())

        btn_frame = ttk.Frame(self.authors_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Показать патенты автора", command=self.show_author_patents).pack(side=tk.LEFT)

    def load_authors(self):
        try:
            self.authors = self.api_client.get_authors()
            self.update_authors_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить авторов:\n{str(e)}")

    def update_authors_table(self):
        for item in self.authors_tree.get_children():
            self.authors_tree.delete(item)

        for author in self.authors:
            values = (
                author.get('id', ''),
                author.get('full_name', ''),
                self.get_passport_string(author.get('passport_id')) if author.get('passport_id') else '-'
            )
            self.authors_tree.insert("", tk.END, values=values)

    def filter_authors(self):
        search_text = self.author_search_var.get().lower()
        search_passport = self.author_passport_var.get().strip()

        filtered = []
        for author in self.authors:
            if search_text and search_text not in (author.get('full_name') or '').lower():
                continue

            if search_passport:
                passport_str = self.get_passport_string(author.get('passport_id'))
                if search_passport not in passport_str:
                    continue

            filtered.append(author)

        for item in self.authors_tree.get_children():
            self.authors_tree.delete(item)

        for author in filtered:
            values = (
                author.get('id', ''),
                author.get('full_name', ''),
                self.get_passport_string(author.get('passport_id')) if author.get('passport_id') else '-'
            )
            self.authors_tree.insert("", tk.END, values=values)

    def create_author(self):
        dialog = AuthorDialog(self.parent_frame, self.passports)
        if dialog.author_payload:
            try:
                self.api_client.create_author(dialog.author_payload)
                messagebox.showinfo("Успех", "Автор создан успешно!")
                self.load_authors()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать автора:\n{str(e)}")

    def edit_author(self):
        selected = self.authors_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автора для редактирования")
            return

        author_id = int(self.authors_tree.item(selected[0])['values'][0])
        author = next((a for a in self.authors if a['id'] == author_id), None)

        if not author:
            return

        dialog = AuthorDialog(self.parent_frame, self.passports, author)
        if dialog.author_payload:
            try:
                self.api_client.update_author(author_id, dialog.author_payload)
                messagebox.showinfo("Успех", "Автор обновлен успешно!")
                self.load_authors()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить автора:\n{str(e)}")

    def delete_author(self):
        selected = self.authors_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автора для удаления")
            return

        author_id = int(self.authors_tree.item(selected[0])['values'][0])

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить автора #{author_id}?"):
            try:
                self.api_client.delete_author(author_id)
                messagebox.showinfo("Успех", "Автор удален успешно!")
                self.load_authors()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить автора:\n{str(e)}")

    def view_author(self):
        selected = self.authors_tree.selection()
        if not selected:
            return

        author_id = int(self.authors_tree.item(selected[0])['values'][0])
        author = next((a for a in self.authors if a['id'] == author_id), None)

        if not author:
            return

        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"Автор #{author_id}")
        view_window.geometry("600x300")

        main_frame = tk.Frame(view_window)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text=f"Автор #{author_id}").pack(pady=(0, 20))

        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)

        fields = [
            ("ID:", author.get('id', '')),
            ("ФИО:", author.get('full_name', '')),
            ("Паспорт:", self.get_passport_string(author.get('passport_id')) if author.get('passport_id') else '-'),
        ]

        for i, (label, value) in enumerate(fields):
            tk.Label(info_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10))
            tk.Label(info_frame, text=str(value)).grid(row=i, column=1, sticky=tk.W, pady=5)

        tk.Button(main_frame, text="Закрыть", command=view_window.destroy).pack(pady=(20, 0))

    def show_author_patents(self):
        selected = self.authors_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите автора")
            return

        author_id = int(self.authors_tree.item(selected[0])['values'][0])
        author_name = self.authors_tree.item(selected[0])['values'][1]

        try:
            applications = self.api_client.get_applications()
            author_apps = [app for app in applications if app.get('author_id') == author_id]

            all_patents = self.api_client.get_patents()
            author_patents = [p for p in all_patents if p.get('application_id') in [a['id'] for a in author_apps]]

            result_window = tk.Toplevel(self.parent_frame)
            result_window.title(f"Патенты автора: {author_name}")
            result_window.geometry("900x500")

            main_frame = ttk.Frame(result_window, padding="20")
            main_frame.pack(fill=tk.BOTH, expand=True)

            ttk.Label(main_frame, text=f"Патенты автора: {author_name}").pack(pady=(0, 20))

            table_frame = ttk.Frame(main_frame)
            table_frame.pack(fill=tk.BOTH, expand=True)

            vsb = ttk.Scrollbar(table_frame, orient="vertical")
            vsb.pack(side=tk.RIGHT, fill=tk.Y)

            columns = ("id", "title", "issue_date", "type", "status")
            tree = ttk.Treeview(table_frame, columns=columns, show="tree headings", yscrollcommand=vsb.set)
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

            for patent in author_patents:
                values = (
                    patent.get('id', ''),
                    patent.get('title', ''),
                    patent.get('issue_date', ''),
                    config.PATENT_TYPE_NAMES.get(patent.get('patent_type_id'), 'Неизвестно'),
                    patent.get('status', {}).get('name', 'Не указан') if patent.get('status') else 'Не указан'
                )
                tree.insert("", tk.END, values=values)

            ttk.Label(main_frame, text=f"Всего патентов: {len(author_patents)}").pack(pady=(10, 0))

            ttk.Button(main_frame, text="Закрыть", command=result_window.destroy).pack(pady=(10, 0))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить патенты автора:\n{str(e)}")

    def load_data(self):
        """Загрузить все данные"""
        self.load_employees()
        self.load_authors()


class EmployeeDialog:
    def __init__(self, parent, positions, passports, employee=None):
        self.positions = positions
        self.passports = passports
        self.employee = employee

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактировать сотрудника")
        self.dialog.geometry("400x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.full_name_var = tk.StringVar()
        self.employment_date_var = tk.StringVar()
        self.phone_number_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.passport_var = tk.StringVar()

        self.employee_payload = None

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="ФИО:").pack(anchor=tk.W)
        self.full_name_var.set(self.employee.get('full_name', '') if self.employee else '')
        ttk.Entry(main_frame, textvariable=self.full_name_var).pack(fill=tk.X, pady=5)

        ttk.Label(main_frame, text="Дата трудоустройства (YYYY-MM-DD):").pack(anchor=tk.W)
        self.employment_date_var.set(self.employee.get('employment_date', '') if self.employee else '')
        ttk.Entry(main_frame, textvariable=self.employment_date_var).pack(fill=tk.X, pady=5)

        ttk.Label(main_frame, text="Телефон:").pack(anchor=tk.W)
        self.phone_number_var.set(self.employee.get('phone_number', '') if self.employee else '')
        ttk.Entry(main_frame, textvariable=self.phone_number_var).pack(fill=tk.X, pady=5)

        ttk.Label(main_frame, text="Должность:").pack(anchor=tk.W)
        positions_names = [p['name'] for p in self.positions]
        pos_combo = ttk.Combobox(main_frame, textvariable=self.position_var, values=positions_names, state="readonly")
        pos_combo.pack(fill=tk.X, pady=5)
        if self.employee and self.employee.get('position_id'):
            pos_name = next((p['name'] for p in self.positions if p['id'] == self.employee['position_id']), '')
            self.position_var.set(pos_name)

        ttk.Label(main_frame, text="Паспорт (серия номер через пробел):").pack(anchor=tk.W)
        if self.employee and self.employee.get('passport_id'):
            pas = next((p for p in self.passports if p['id'] == self.employee['passport_id']), None)
            if pas:
                self.passport_var.set(f"{pas['series']} {pas['number']}")
        ttk.Entry(main_frame, textvariable=self.passport_var).pack(fill=tk.X, pady=5)

        ttk.Button(main_frame, text="Сохранить", command=self.save).pack(pady=10)
        ttk.Button(main_frame, text="Отмена", command=self.dialog.destroy).pack()

    def save(self):
        if not self.full_name_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите ФИО")
            return

        position_id = next((p['id'] for p in self.positions if p['name'] == self.position_var.get()), None) if self.position_var.get() else None

        passport_id = None
        passport_str = self.passport_var.get().strip()
        if passport_str:
            parts = passport_str.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                passport_id = next((p['id'] for p in self.passports if str(p['series']) == parts[0] and str(p['number']) == parts[1]), None)

        self.employee_payload = {
            'full_name': self.full_name_var.get().strip(),
            'employment_date': self.employment_date_var.get() or None,
            'phone_number': self.phone_number_var.get() or None,
            'position_id': position_id,
            'passport_id': passport_id
        }
        self.dialog.destroy()


class AuthorDialog:
    def __init__(self, parent, passports, author=None):
        self.passports = passports
        self.author = author

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать автора" if not author else "Редактировать автора")
        self.dialog.geometry("400x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.full_name_var = tk.StringVar()
        self.passport_var = tk.StringVar()

        self.author_payload = None

        self.create_widgets()
        self.dialog.wait_window()

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="ФИО:").pack(anchor=tk.W)
        self.full_name_var.set(self.author.get('full_name', '') if self.author else '')
        ttk.Entry(main_frame, textvariable=self.full_name_var).pack(fill=tk.X, pady=5)

        ttk.Label(main_frame, text="Паспорт (серия номер через пробел):").pack(anchor=tk.W)
        if self.author and self.author.get('passport_id'):
            pas = next((p for p in self.passports if p['id'] == self.author['passport_id']), None)
            if pas:
                self.passport_var.set(f"{pas['series']} {pas['number']}")
        ttk.Entry(main_frame, textvariable=self.passport_var).pack(fill=tk.X, pady=5)

        ttk.Button(main_frame, text="Сохранить", command=self.save).pack(pady=10)
        ttk.Button(main_frame, text="Отмена", command=self.dialog.destroy).pack()

    def save(self):
        if not self.full_name_var.get().strip():
            messagebox.showwarning("Предупреждение", "Введите ФИО")
            return

        passport_id = None
        passport_str = self.passport_var.get().strip()
        if passport_str:
            parts = passport_str.split()
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                passport_id = next((p['id'] for p in self.passports if str(p['series']) == parts[0] and str(p['number']) == parts[1]), None)

        self.author_payload = {
            'full_name': self.full_name_var.get().strip(),
            'passport_id': passport_id
        }
        self.dialog.destroy()