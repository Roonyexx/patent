import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import src.client.config as config
from src.client.client import Client


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
        
        columns = ("id", "submission_date", "status", "documents", "employee_id", "author_id")
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
        self.tree.heading("employee_id", text="ID Сотрудника")
        self.tree.heading("author_id", text="ID Автора")

        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("submission_date", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=150, anchor=tk.CENTER)
        self.tree.column("documents", width=300)
        self.tree.column("employee_id", width=120, anchor=tk.CENTER)
        self.tree.column("author_id", width=120, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<Double-1>", lambda e: self.view_application())
    
    def load_data(self):
        try:
            self.applications = self.client.get_applications()
            self.statuses = self.client.get_statuses()

            statuses_names = [s['name'] for s in self.statuses]
            combobox_values = ['Все'] + statuses_names + ['По дате']

            self.filter_combobox['values'] = combobox_values

            self.update_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for app in self.applications:
            status_name = app.get('status', {}).get('name', 'Неизвестно') if app.get('status') else 'Не указан'
            
            submission_date = app.get('submission_date', '')
            if submission_date:
                try:
                    dt = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
                    submission_date = dt.strftime('%Y-%m-%d %H:%M')
                except Exception as e:
                    messagebox.showerror('Ошибка', str(e))
            
            values = (
                app.get('id', ''),
                submission_date,
                status_name,
                app.get('documents', '')[:50] + '...' if app.get('documents') and len(app.get('documents', '')) > 50 else app.get('documents', ''),
                app.get('employee_id', '-'),
                app.get('author_id', '-')
            )
            
            self.tree.insert("", tk.END, values=values, tags=(app.get('id'),))
    
    def filter_applications(self):
        filter_param = self.filter_var.get()
        search_text = self.search_var.get().lower()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for app in self.applications:
            status_name = app.get('status', {}).get('name', '') if app.get('status') else ''
            submission_date = app.get('submission_date', '')

            if submission_date:
                try:
                    dt = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
                    submission_date = dt.strftime('%Y-%m-%d')
                except Exception as e:
                    messagebox.showwarning('Предупреждение', str(e))

            if filter_param != "Все":
                if status_name != filter_param and filter_param != 'По дате':
                    continue

                if search_text:
                    if filter_param == 'По дате' and search_text != submission_date:
                        continue
            
            values = (
                app.get('id', ''),
                submission_date,
                status_name,
                app.get('documents', '')[:50] + '...' if app.get('documents') and len(app.get('documents', '')) > 50 else app.get('documents', ''),
                app.get('employee_id', '-'),
                app.get('author_id', '-')
            )
            
            self.tree.insert("", tk.END, values=values, tags=(app.get('id'),))
    
    def create_application(self):
        dialog = ApplicationDialog(self.parent_frame, self.statuses)

        if dialog.result:
            try:
                self.client.create_application(dialog.result)
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
        
        dialog = ApplicationDialog(self.parent_frame, self.statuses, app)
        if dialog.result:
            try:
                self.client.update_application(app_id, dialog.result)
                messagebox.showinfo("Успех", "Заявка обновлена успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить заявку:\n{str(e)}")
    
    def view_application(self):
        selected = self.tree.selection()
        if not selected:
            return
        
        app_id = int(self.tree.item(selected[0])['values'][0])
        app = next((a for a in self.applications if a['id'] == app_id), None)
        
        if not app:
            return
        
        # Создаем окно просмотра
        view_window = tk.Toplevel(self.parent_frame)
        view_window.title(f"Заявка #{app_id}")
        view_window.geometry("600x500")
        
        # Контент
        main_frame = ttk.Frame(view_window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Информация
        ttk.Label(main_frame, text=f"Заявка #{app_id}", style="Title.TLabel").pack(pady=(0, 20))
        
        info_frame = ttk.Frame(main_frame)
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
            ttk.Label(info_frame, text=label, font=(config.FONT_FAMILY, config.FONT_SIZE_NORMAL, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=5, padx=(0, 10)
            )
            ttk.Label(info_frame, text=str(value)).grid(
                row=i, column=1, sticky=tk.W, pady=5
            )
        
        # Кнопка закрытия
        ttk.Button(
            main_frame,
            text="Закрыть",
            style="Secondary.TButton",
            command=view_window.destroy
        ).pack(pady=(20, 0))
    
    def delete_application(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для удаления")
            return
        
        app_id = int(self.tree.item(selected[0])['values'][0])
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить заявку #{app_id}?"):
            try:
                self.client.delete_application(app_id)
                messagebox.showinfo("Успех", "Заявка удалена успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заявку:\n{str(e)}")


class ApplicationDialog:
    def __init__(self, parent, statuses, application=None):
        self.statuses = statuses
        self.application = application

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать заявку" if not application else "Редактировать заявку")
        self.dialog.geometry("400x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.full_name_var = tk.StringVar()
        self.passport_var = tk.StringVar()
        self.documents_text = None
        self.conclusion_text = None
        self.status_combobox = None
        self.result = None
        
        self.create_widgets()
        self.dialog.wait_window()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="ФИО автора:").pack(anchor=tk.W, pady=(0, 5))
        tk.Entry(main_frame, textvariable=self.full_name_var).pack(fill=tk.X, pady=(0, 15))

        tk.Label(main_frame, text="Серия и номер паспорта (через пробел):").pack(anchor=tk.W, pady=(0, 5))
        tk.Entry(main_frame, textvariable=self.passport_var).pack(fill=tk.X, pady=(0, 15))

        tk.Label(main_frame, text="Документы:").pack(anchor=tk.W, pady=(0, 5))
        documents_var = tk.StringVar(value=self.application.get('documents', '') if self.application else '')
        self.documents_text = tk.Text(main_frame, height=5)
        self.documents_text.pack(fill=tk.X, pady=(0, 15))
        self.documents_text.insert('1.0', documents_var.get())

        tk.Label(main_frame, text="Заключение эксперта:").pack(anchor=tk.W, pady=(0, 5))
        conclusion_var = tk.StringVar(value=self.application.get('expert_conclusion', '') if self.application else '')
        self.conclusion_text = tk.Text(main_frame, height=5)
        self.conclusion_text.pack(fill=tk.X, pady=(0, 15))
        self.conclusion_text.insert('1.0', conclusion_var.get())

        tk.Label(main_frame, text="Статус:").pack(anchor=tk.W, pady=(0, 5))
        status_var = tk.StringVar()
        combobox_values = [s['name'] for s in self.statuses]
        self.status_combobox = ttk.Combobox(main_frame, textvariable=status_var, state="readonly", values=combobox_values)
        self.status_combobox.pack(fill=tk.X, pady=(0, 15))

        if self.application and self.application.get('status'):
            self.status_combobox.set(self.application['status']['name'])
        elif self.statuses:
            self.status_combobox.current(0)

        buttons_frame = tk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(buttons_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, expand=True, fill=tk.X,
                                                                           padx=(0, 5))

        tk.Button(buttons_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, expand=True,
                                                                                  fill=tk.X, padx=(5, 0))
    
    def save(self):
        data = {
            "documents": self.documents_text.get('1.0', tk.END).strip()
        }

        if self.conclusion_text:
            data["expert_conclusion"] = self.conclusion_text.get('1.0', tk.END).strip()

        if self.status_combobox:
            status_name = self.status_combobox.get()
            status = next((s for s in self.statuses if s['name'] == status_name), None)
            if status:
                data["status_id"] = status['id']
        
        self.result = data
        self.dialog.destroy()