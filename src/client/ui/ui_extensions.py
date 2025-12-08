import tkinter as tk


def add_entry_field(parent, label_text, entry_var, label_row, label_col, entry_row, entry_col):
    tk.Label(parent, text=label_text).grid(row=label_row, column=label_col)
    tk.Entry(parent, textvariable=entry_var, width=50).grid(row=entry_row, column=entry_col)

def center_window(window: tk.Tk):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() - width) // 2
    y = (window.winfo_screenheight() - height) // 2
    window.geometry(f'{width}x{height}+{x}+{y}')
