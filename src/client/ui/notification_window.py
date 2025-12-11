import tkinter as tk
from tkinter import ttk

import src.client.ui.ui_extensions as ext


TITLE = 'Необходимо обработать заявку'
EXPIRES_MESSAGE = 'Истекает срок обработки заявки №'
EXPIRED_MESSAGE = 'Истек срок обработки заявки №'


class NotificationWindow:
    def __init__(self, notifications):
        self.window = tk.Tk()
        self.window.title("Уведомления")
        self.window.geometry("400x500")

        self.counter_label = None
        self.notifications_frame = None
        self.canvas = None

        self.create_widgets()

        self.notifications = []

        for notification in notifications:
            if notification.get('is_expired'):
                self.add_notification(TITLE,
                    f'{EXPIRED_MESSAGE}{notification.get('id')}')
            else:
                self.add_notification(TITLE,
                    f'{EXPIRES_MESSAGE}{notification.get('id')} (осталось {notification.get('days_left')} дней)')

        ext.center_window(self.window)

    def create_widgets(self):
        control_frame = tk.Frame(self.window, padx=10, pady=10)
        control_frame.pack(fill="x")

        tk.Button(control_frame, text="Очистить все", command=self.clear_all_notifications).pack(side="right", padx=5)

        self.counter_label = tk.Label(control_frame, text="Уведомлений (0)")
        self.counter_label.pack(side='left', pady=5)

        canvas_frame = tk.Frame(self.window)
        canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)

        self.notifications_frame = tk.Frame(self.canvas)
        self.notifications_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.notifications_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def add_notification(self, title, message):
        notification_frame = tk.Frame(self.notifications_frame, borderwidth=1, padx=15, pady=10)
        notification_frame.pack(fill="x", pady=5)

        title_frame = tk.Frame(notification_frame)
        title_frame.pack(fill="x")

        tk.Label(title_frame, text=title, anchor="w").pack(side="left")
        tk.Label(notification_frame, text=message, wraplength=350, justify="left", anchor="w").pack(fill="x", pady=(5, 0))

        tk.Button(notification_frame, text="x", fg="gray", borderwidth=0,
                              command=lambda: self.remove_notification(notification_frame)).place(relx=1.0, rely=0.0,
                                                                                                  anchor="ne", x=-5, y=5)

        self.notifications.append(notification_frame)
        self.update_counter()
        return notification_frame

    def remove_notification(self, notification_frame):
        if notification_frame in self.notifications:
            notification_frame.destroy()
            self.notifications.remove(notification_frame)
            self.update_counter()

    def clear_all_notifications(self):
        for notification in self.notifications[:]:
            notification.destroy()
        self.notifications.clear()
        self.update_counter()

    def update_counter(self):
        count = len(self.notifications)
        self.counter_label.config(text=f"Уведомлений ({count})")

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def show(self):
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.mainloop()

    def on_closing(self):
        self.window.destroy()
