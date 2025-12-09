import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog
from docx import Document

from src.client.client import Client


WINDOW_SIZE = '600x300'
PREVIEW_WINDOW_SIZE = '500x300'

REPORT_TYPES = [
            ("Отчет по авторам", "author"),
            ("Отчет по годам", "year"),
            ("Отчет по типу патента", "type"),
            ("Отчет по патентной активности", "activity")
]

EXPORT_FORMATS = [
    ('Word (.doc)', 'word'),
]

FILE_TYPES = {
    'word': [('Word files', '.doc')]
}

TABLE_HEADERS = {
    'author': ['Автор', 'Количество патентов'],
    'year': ['Год', 'Количество патентов'],
    'type': ['Тип патента', 'Количество патентов'],
    'activity': ['Количество патентов', 'Количество заявок', 'Количество истекших патентов']
}

def add_word_report_table(doc, data, headers):
    if len(data) == 0:
        return

    print(data)
    df = pd.DataFrame(data)

    table = doc.add_table(rows=1, cols=len(df.columns))
    header_cells = table.rows[0].cells

    for i in range(len(headers)):
        header_cells[i].text = headers[i]

    for _, row in df.iterrows():
        row_cells = table.add_row().cells

        for i, value in enumerate(row):
            row_cells[i].text = str(value)


class ExportWindow:
    def __init__(self, parent, client: Client):
        self.client = client

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Экспорт")
        self.dialog.geometry(WINDOW_SIZE)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self.report_type = tk.StringVar(self.dialog, value=REPORT_TYPES[0][1])
        self.export_format = tk.StringVar(self.dialog, value=EXPORT_FORMATS[0][1])
        self.path_var = tk.StringVar(self.dialog)
        self.file_name_var = tk.StringVar(self.dialog)

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.dialog, padx=20)
        frame.pack(fill='both', expand=True)

        for i in range(8):
            frame.rowconfigure(index=i, weight=1)

        for j in range(2):
            frame.columnconfigure(index=j, weight=1)

        tk.Label(frame, text="Тип отчета:").grid(row=0, column=0, sticky='w')

        for i, (text, value) in enumerate(REPORT_TYPES):
            tk.Radiobutton(frame, text=text, variable=self.report_type, value=value).grid(
                row=i + 1, column=0, columnspan=2, sticky='w')

        tk.Label(frame, text="Формат экспорта:").grid(row=0, column=1, sticky='w')

        for i, (text, value) in enumerate(EXPORT_FORMATS):
            tk.Radiobutton(frame, text=text, variable=self.export_format, value=value).grid(
                row=i + 1, column=1, sticky='w')

        path_row = max(len(REPORT_TYPES), len(EXPORT_FORMATS)) + 1
        tk.Label(frame, text="Путь:").grid(row=path_row, column=0, sticky='w')

        path_frame = tk.Frame(frame)
        path_frame.grid(row=path_row, column=1, sticky='ew')
        path_frame.columnconfigure(index=0, weight=2)
        path_frame.columnconfigure(index=1, weight=1)

        self.path_var.set(os.path.join(os.getcwd()))
        tk.Entry(path_frame, textvariable=self.path_var, state='disabled').grid(row=0, column=0, sticky='ew')

        tk.Button(path_frame, text="Обзор...", command=self.browse_path).grid(row=0, column=1)

        tk.Label(frame, text="Имя файла:").grid(row=path_row + 1, column=0, sticky='w')
        tk.Entry(frame, textvariable=self.file_name_var).grid(row=path_row + 1, column=1, sticky='ew')

        tk.Button(frame, text="Экспортировать отчет", command=self.export_report, width=25).grid(
            row=path_row + 2, column=0)
        tk.Button(frame, text="Предварительный просмотр", command=self.preview_report, width=25).grid(
            row=path_row + 2, column=1)

    def browse_path(self):
        filename = filedialog.askdirectory(
            initialdir=os.getcwd()
        )

        if filename:
            self.path_var.set(filename)

    def preview_report(self):
        data = self.get_export_data()
        df = pd.DataFrame(data)

        if len(data) > 0:
            df.columns = TABLE_HEADERS.get(self.report_type.get())

        preview_window = tk.Toplevel(self.dialog)
        preview_window.title('Предварительный просмотр отчета')
        preview_window.geometry(PREVIEW_WINDOW_SIZE)

        text_widget = tk.Text(preview_window, wrap=tk.NONE)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text_widget.insert(tk.END, f'{self.get_report_name()}\n')
        text_widget.insert(tk.END, '-' * 50 + '\n')

        if len(data) > 0:
            text_widget.insert(tk.END, df.to_string(index=False))

        text_widget.config(state=tk.DISABLED)

        scroll_y = tk.Scrollbar(preview_window, orient=tk.VERTICAL, command=text_widget.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=scroll_y.set)

        scroll_x = tk.Scrollbar(preview_window, orient=tk.HORIZONTAL, command=text_widget.xview)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        text_widget.configure(xscrollcommand=scroll_x.set)

    def export_report(self):
        try:
            filepath = self.path_var.get()

            if not filepath:
                messagebox.showerror('Ошибка', 'Укажите путь для сохранения файла')
                return

            if not self.file_name_var.get():
                messagebox.showerror('Ошибка', 'Укажите имя файла')
                return

            export_format = self.export_format.get()
            file_type = FILE_TYPES.get(export_format)[0][1]
            filepath += '/' + self.file_name_var.get() + file_type

            if export_format == 'word':
                self.export_to_word(filepath)
                message = f'Отчет успешно экспортирован в Word:\n{filepath}'
            else:
                messagebox.showerror('Ошибка', f'Неизвестный формат: {export_format}')
                return

            result = messagebox.askyesno(
                'Успешный экспорт',
                f'{message}\n\nОткрыть папку с файлом?'
            )

            if result:
                os.startfile(os.path.dirname(filepath))
        except Exception as e:
            messagebox.showerror('Ошибка экспорта', str(e))

    def export_to_word(self, filepath):
        doc = Document()
        doc.add_heading(self.get_report_name(), 0)
        data = self.get_export_data()
        add_word_report_table(doc, data, TABLE_HEADERS.get(self.report_type.get()))
        doc.save(filepath)

    def get_report_name(self):
        for report_type in REPORT_TYPES:
            if report_type[1] == self.report_type.get():
                return report_type[0]
        return 'Без названия'

    def get_export_data(self):
        if self.report_type.get() == 'author':
            return self.client.get_statistics_by_author().get('data')
        elif self.report_type.get() == 'year':
            return self.client.get_statistics_by_year().get('data')
        elif self.report_type.get() == 'type':
            response = self.client.get_statistics_by_type().get('data')
            data = []

            for item in response:
                patent_type = self.client.get_patent_type_name(item.get('type_id'))
                data.append({'patent_type': patent_type, 'patent_count': item.get('patent_count')})

            return data
        else:
            return [self.client.get_activity_report()]

    def show(self):
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.dialog.mainloop()

    def on_closing(self):
        self.dialog.destroy()
