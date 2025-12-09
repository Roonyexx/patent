import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date, timedelta

import src.client.ui.ui_extensions as ext
from src.client.client import Client
from src.client.ui.applications_window import ApplicationsWindow
from src.client.ui.patents_window import PatentsWindow
from src.client.ui.export_window import ExportWindow
from src.client.ui.notification_window import NotificationWindow


WINDOW_SIZE = '1400x800'

APPLICATION_PROCESSING_DEADLINE = 10

def is_application_expired(submission_date: str):
    if submission_date:
        try:
            formatted_submission_date = datetime.strptime(submission_date.split('T')[0], '%Y-%m-%d').date()
            deadline_date = formatted_submission_date + timedelta(
                days=APPLICATION_PROCESSING_DEADLINE)
            print(deadline_date - formatted_submission_date)

            if deadline_date >= date.today():
                return False, (deadline_date - formatted_submission_date).days
        except Exception as e:
            print(str(e))

    return True, 0


class MainWindow:
    def __init__(self, client: Client):
        self.client = client
        self.user = self.client.get_current_user()
        
        self.window = tk.Tk()
        self.window.title('Патентный менеджер')
        self.window.geometry(WINDOW_SIZE)

        self.content = None
        self.content_frame = None

        self.create_widgets()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        ext.center_window(self.window)
    
    def create_widgets(self):
        top_frame = tk.Frame(self.window)
        top_frame.pack(fill=tk.X, side=tk.TOP)

        tk.Button(top_frame, text="Выход", command=self.logout).pack(side=tk.RIGHT, padx=(0, 10))
        tk.Label(top_frame, text=f'{self.user.get('username')}').pack(side=tk.RIGHT, padx=(0, 10))

        main_container = tk.Frame(self.window)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        sidebar_frame = tk.Frame(main_container, width=200)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        sidebar_frame.pack_propagate(False)

        tk.Label(sidebar_frame, text="Меню").pack(pady=(0, 10))

        tk.Button(sidebar_frame, text="Заявки", command=lambda: self.show_content("applications")).pack(fill=tk.X,
                                                                                                        pady=(0, 5))
        tk.Button(sidebar_frame, text="Патенты", command=lambda: self.show_content("patents")).pack(fill=tk.X,
                                                                                                    pady=(0, 5))
        tk.Button(sidebar_frame, text="Уведомления", command=self.show_notification_window).pack(fill=tk.X, pady=(0, 5))
        tk.Button(sidebar_frame, text="Экспорт отчетов", command=self.show_export_window).pack(fill=tk.X, pady=(0, 5))

        self.content_frame = tk.Frame(main_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.show_content("applications")
    
    def show_content(self, content_type):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if content_type == "applications":
            self.content = ApplicationsWindow(self.content_frame, self.user, self.client)
        elif content_type == "patents":
            self.content = PatentsWindow(self.content_frame, self.client)

    def show_notification_window(self):
        NotificationWindow(self.collect_notifications()).show()

    def show_export_window(self):
        ExportWindow(self.content_frame, self.client).show()

    def collect_notifications(self):
        notifications = []
        applications = self.client.get_applications()

        for application in applications:
            submission_date = application.get('submission_date')
            is_expired, days_left = is_application_expired(submission_date)

            if not is_expired:
                notifications.append({
                    'id': application.get('id'),
                    'days_left': days_left
                })
        return notifications


    def logout(self):
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти?"):
            try:
                self.client.logout()
            except Exception as e:
                messagebox.showerror(str(e))
            
            self.window.destroy()

            from src.client.ui.login_window import LoginWindow
            LoginWindow(self.client).show()
    
    def on_closing(self):
        if messagebox.askyesno("Выход", "Вы действительно хотите выйти из программы?"):
            try:
                self.client.logout()
            except Exception as e:
                messagebox.showerror(str(e))

            self.window.destroy()
    
    def show(self):
        self.window.mainloop()