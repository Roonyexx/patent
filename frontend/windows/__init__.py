# frontend/__init__.py
"""
Патентный Менеджер - Frontend
"""

__version__ = "1.0.0"
__author__ = "Patent Team"


# frontend/windows/__init__.py
"""
Модуль окон приложения
"""

from .login_window import LoginWindow
from .register_window import RegisterWindow
from .main_window import MainWindow
from .applications_window import ApplicationsWindow
from .patents_window import PatentsWindow
from .analytics_window import AnalyticsWindow
from .references_window import ReferencesWindow

__all__ = [
    'LoginWindow',
    'RegisterWindow',
    'MainWindow',
    'ApplicationsWindow',
    'PatentsWindow',
    'AnalyticsWindow',
    'ReferencesWindow'
]