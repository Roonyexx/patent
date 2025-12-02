"""
Окно управления заявками
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from config import Config
from api_client import APIClient


class ApplicationsWindow:
    """Окно для работы с заявками"""
    
    def __init__(self, parent_frame, api_client: APIClient):
        self.parent_frame = parent_frame
        self.api_client = api_client
        self.applications = []
        self.statuses = []
        
        # Получаем информацию о пользователе
        self.user = api_client.user_info
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Создать виджеты"""
        # Заголовок
        header_frame = ttk.Frame(self.parent_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="Управление заявками",
            style="Subtitle.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Панель инструментов
        toolbar_frame = ttk.Frame(self.parent_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Кнопки
        ttk.Button(
            toolbar_frame,
            text="➕ Создать заявку",
            style="Success.TButton",
            command=self.create_application
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            toolbar_frame,
            text="✏️ Редактировать",
            style="Secondary.TButton",
            command=self.edit_application
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Только сотрудники могут удалять
        if self.user.get('user_type') == Config.USER_TYPE_EMPLOYEE:
            ttk.Button(
                toolbar_frame,
                text="🗑️ Удалить",
                style="Danger.TButton",
                command=self.delete_application
            ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            toolbar_frame,
            text="🔄 Обновить",
            style="Secondary.TButton",
            command=self.load_data
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Фильтр по статусу
        ttk.Label(toolbar_frame, text="Фильтр по статусу:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.status_filter_var = tk.StringVar(value="Все")
        self.status_filter_combo = ttk.Combobox(
            toolbar_frame,
            textvariable=self.status_filter_var,
            state="readonly",
            width=20
        )
        self.status_filter_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.status_filter_combo.bind("<<ComboboxSelected>>", lambda e: self.filter_applications())
        
        # Поиск
        ttk.Label(toolbar_frame, text="Поиск:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_applications())
        search_entry = ttk.Entry(toolbar_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT)
        
        # Таблица
        table_frame = ttk.Frame(self.parent_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("id", "submission_date", "status", "documents", "employee_id", "author_id")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Заголовки
        self.tree.heading("#0", text="")
        self.tree.heading("id", text="ID")
        self.tree.heading("submission_date", text="Дата подачи")
        self.tree.heading("status", text="Статус")
        self.tree.heading("documents", text="Документы")
        self.tree.heading("employee_id", text="ID Сотрудника")
        self.tree.heading("author_id", text="ID Автора")
        
        # Ширина колонок
        self.tree.column("#0", width=0, stretch=False)
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("submission_date", width=150, anchor=tk.CENTER)
        self.tree.column("status", width=150, anchor=tk.CENTER)
        self.tree.column("documents", width=300)
        self.tree.column("employee_id", width=120, anchor=tk.CENTER)
        self.tree.column("author_id", width=120, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Двойной клик для просмотра
        self.tree.bind("<Double-1>", lambda e: self.view_application())
        
        # Статус бар
        self.status_bar = ttk.Label(
            self.parent_frame,
            text="Готово",
            style="Light.TLabel",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def load_data(self):
        """Загрузить данные"""
        try:
            # Загружаем заявки
            self.applications = self.api_client.get_applications()
            
            # Загружаем статусы для фильтра
            self.statuses = self.api_client.get_statuses()
            status_names = ["Все"] + [s['name'] for s in self.statuses]
            self.status_filter_combo['values'] = status_names
            
            # Обновляем таблицу
            self.update_table()
            
            self.status_bar.config(text=f"Загружено заявок: {len(self.applications)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def update_table(self):
        """Обновить таблицу"""
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавляем данные
        for app in self.applications:
            status_name = app.get('status', {}).get('name', 'Неизвестно') if app.get('status') else 'Не указан'
            
            submission_date = app.get('submission_date', '')
            if submission_date:
                try:
                    dt = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
                    submission_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
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
        """Фильтровать заявки"""
        status_filter = self.status_filter_var.get()
        search_text = self.search_var.get().lower()
        
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Фильтруем
        for app in self.applications:
            status_name = app.get('status', {}).get('name', '') if app.get('status') else ''
            
            # Фильтр по статусу
            if status_filter != "Все" and status_name != status_filter:
                continue
            
            # Поиск
            if search_text:
                searchable = f"{app.get('id', '')} {app.get('documents', '')} {status_name}".lower()
                if search_text not in searchable:
                    continue
            
            # Добавляем в таблицу
            submission_date = app.get('submission_date', '')
            if submission_date:
                try:
                    dt = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
                    submission_date = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
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
        """Создать новую заявку"""
        dialog = ApplicationDialog(self.parent_frame, self.api_client, self.statuses)
        if dialog.result:
            try:
                self.api_client.create_application(dialog.result)
                messagebox.showinfo("Успех", "Заявка создана успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать заявку:\n{str(e)}")
    
    def edit_application(self):
        """Редактировать заявку"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для редактирования")
            return
        
        app_id = int(self.tree.item(selected[0])['values'][0])
        app = next((a for a in self.applications if a['id'] == app_id), None)
        
        if not app:
            return
        
        dialog = ApplicationDialog(self.parent_frame, self.api_client, self.statuses, app)
        if dialog.result:
            try:
                self.api_client.update_application(app_id, dialog.result)
                messagebox.showinfo("Успех", "Заявка обновлена успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить заявку:\n{str(e)}")
    
    def view_application(self):
        """Просмотреть заявку"""
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
            ttk.Label(info_frame, text=label, font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL, 'bold')).grid(
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
        """Удалить заявку"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите заявку для удаления")
            return
        
        app_id = int(self.tree.item(selected[0])['values'][0])
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить заявку #{app_id}?"):
            try:
                self.api_client.delete_application(app_id)
                messagebox.showinfo("Успех", "Заявка удалена успешно!")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заявку:\n{str(e)}")


class ApplicationDialog:
    """Диалог создания/редактирования заявки"""
    
    def __init__(self, parent, api_client: APIClient, statuses, application=None):
        self.result = None
        self.api_client = api_client
        self.statuses = statuses
        self.application = application
        
        # Создаем окно
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Создать заявку" if not application else "Редактировать заявку")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Ждем закрытия
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Создать виджеты"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Документы
        ttk.Label(main_frame, text="Документы:").pack(anchor=tk.W, pady=(0, 5))
        self.documents_var = tk.StringVar(value=self.application.get('documents', '') if self.application else '')
        documents_text = tk.Text(main_frame, height=5, font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
        documents_text.pack(fill=tk.X, pady=(0, 15))
        documents_text.insert('1.0', self.documents_var.get())
        
        # Заключение эксперта (только для сотрудников)
        user = self.api_client.user_info
        if user.get('user_type') == Config.USER_TYPE_EMPLOYEE:
            ttk.Label(main_frame, text="Заключение эксперта:").pack(anchor=tk.W, pady=(0, 5))
            self.conclusion_var = tk.StringVar(value=self.application.get('expert_conclusion', '') if self.application else '')
            conclusion_text = tk.Text(main_frame, height=5, font=(Config.FONT_FAMILY, Config.FONT_SIZE_NORMAL))
            conclusion_text.pack(fill=tk.X, pady=(0, 15))
            conclusion_text.insert('1.0', self.conclusion_var.get())
        else:
            conclusion_text = None
        
        # Статус (только для сотрудников)
        if user.get('user_type') == Config.USER_TYPE_EMPLOYEE:
            ttk.Label(main_frame, text="Статус:").pack(anchor=tk.W, pady=(0, 5))
            self.status_var = tk.StringVar()
            status_combo = ttk.Combobox(
                main_frame,
                textvariable=self.status_var,
                state="readonly"
            )
            status_combo['values'] = [s['name'] for s in self.statuses]
            status_combo.pack(fill=tk.X, pady=(0, 15))
            
            if self.application and self.application.get('status'):
                status_combo.set(self.application['status']['name'])
            elif self.statuses:
                status_combo.current(0)
        else:
            status_combo = None
        
        # Кнопки
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            buttons_frame,
            text="Сохранить",
            style="Success.TButton",
            command=lambda: self.save(documents_text, conclusion_text, status_combo)
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        ttk.Button(
            buttons_frame,
            text="Отмена",
            style="Secondary.TButton",
            command=self.dialog.destroy
        ).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(5, 0))
    
    def save(self, documents_text, conclusion_text, status_combo):
        """Сохранить данные"""
        data = {
            "documents": documents_text.get('1.0', tk.END).strip()
        }
        
        # Добавляем заключение и статус для сотрудников
        user = self.api_client.user_info
        if user.get('user_type') == Config.USER_TYPE_EMPLOYEE:
            if conclusion_text:
                data["expert_conclusion"] = conclusion_text.get('1.0', tk.END).strip()
            
            if status_combo:
                status_name = status_combo.get()
                status = next((s for s in self.statuses if s['name'] == status_name), None)
                if status:
                    data["status_id"] = status['id']
        
        self.result = data
        self.dialog.destroy()