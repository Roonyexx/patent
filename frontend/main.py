"""
Главный файл запуска приложения
"""
import sys
import os

# Добавляем путь к frontend в sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from api_client import APIClient
from styles import Styles
from windows.login_window import LoginWindow
from windows.main_window import MainWindow


def main():
    """Главная функция"""
    # Инициализируем директории
    Config.init_directories()
    
    # Настраиваем стили
    Styles.configure_styles()
    
    # Создаем API клиент
    api_client = APIClient()
    
    def on_login_success():
        """Callback после успешного входа"""
        main_window = MainWindow(api_client)
        main_window.run()
    
    # Открываем окно входа
    login_window = LoginWindow(api_client, on_login_success)
    login_window.run()


if __name__ == "__main__":
    main()