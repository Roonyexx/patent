API_BASE_URL = "https://localhost:8000"
API_TIMEOUT = 30

APP_TITLE = "Патентный Менеджер"
APP_VERSION = "1.0.0"

LOGIN_WINDOW_SIZE = "400x200"
MAIN_WINDOW_SIZE = "1400x800"

PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
SUCCESS_COLOR = "#27ae60"
DANGER_COLOR = "#e74c3c"
WARNING_COLOR = "#f39c12"
LIGHT_BG = "#ecf0f1"
DARK_TEXT = "#2c3e50"
LIGHT_TEXT = "#7f8c8d"

FONT_FAMILY = "Segoe UI"
FONT_SIZE_SMALL = 9
FONT_SIZE_NORMAL = 10
FONT_SIZE_LARGE = 12
FONT_SIZE_TITLE = 16

STATUS_CREATED = 1
STATUS_DRAFT = 2
STATUS_SUBMITTED = 3
STATUS_UNDER_REVIEW = 4
STATUS_APPROVED = 5
STATUS_REJECTED = 6
STATUS_ACTIVE = 7
STATUS_EXPIRED = 8
STATUS_IN_CORRECTION = 9
STATUS_WITHDRAWN = 10

STATUS_NAMES = {
    1: "Создан",
    2: "Черновик",
    3: "Отправлен",
    4: "На рассмотрении",
    5: "Одобрен",
    6: "Отклонён",
    7: "Активен",
    8: "Истёкший",
    9: "На исправлении",
    10: "Отозван"
}

PATENT_TYPE_INVENTION = 1
PATENT_TYPE_UTILITY_MODEL = 2
PATENT_TYPE_INDUSTRIAL_DESIGN = 3

PATENT_TYPE_NAMES = {
    1: "Изобретение",
    2: "Полезная модель",
    3: "Промышленный образец"
}

USER_TYPE_EMPLOYEE = "employee"
USER_TYPE_AUTHOR = "author"

USER_TYPE_NAMES = {
    "employee": "Сотрудник",
    "author": "Автор"
}