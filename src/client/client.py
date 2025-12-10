import requests
import urllib3
from typing import Optional, Dict, Any
import src.client.config as config

urllib3.disable_warnings()


class Client:
    def __init__(self):
        # Гарантируем, что base_url не заканчивается на слэш
        self.base_url = config.API_BASE_URL.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.user: Optional[Dict] = None
        self.session.verify = False

    def make_request(self, method: str, endpoint: str, data: Any = None, params: Any = None):
        # Правильная сборка URL: убираем лишний слэш в начале эндпоинта
        clean_endpoint = endpoint.lstrip('/')
        url = f"{self.base_url}/{clean_endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=config.API_TIMEOUT
            )

            # Добавим вывод для отладки 405 ошибки
            if response.status_code == 405:
                print(f"DEBUG: 405 Method Not Allowed on {method} {url}")

            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            try:
                # Пытаемся достать описание ошибки из JSON ответа бэкенда
                detail = response.json().get("detail", str(e))
            except:
                detail = str(e)
            raise Exception(f"Ошибка API ({method} {url}): {detail}") from e

    # === Аутентификация ===
    def register(self, data: Dict):
        user_response = self.make_request("POST", "/auth/register", data=data)
        self.process_user_authorization(user_response)
        return user_response

    def login(self, username: str, password: str):
        user_response = self.make_request("POST", "/auth/login", data={"username": username, "password": password})
        self.process_user_authorization(user_response)
        return user_response

    def process_user_authorization(self, user_response):
        token = user_response.get("access_token")
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def logout(self):
        try:
            self.make_request("POST", "/auth/logout")
        finally:
            self.session.close()

    def get_current_user(self):
        user = self.make_request("GET", "/auth/me")
        self.user = user
        return user

    # === Справочники ===
    def get_positions(self):
        # Используем путь без завершающего слэша, если он не нужен в бэкенде
        return self.make_request("GET", "/reference/positions")

    def get_statuses(self):
        return self.make_request("GET", "/reference/statuses/")

    def get_status(self, status_id: int):
        return self.make_request("GET", f"/reference/statuses/{status_id}")

    def get_patent_types(self):
        return self.make_request("GET", "/reference/types/")

    def get_status_id_by_name(self, status_name: str) -> int:
        """Получить ID статуса по названию"""
        try:
            statuses = self.get_statuses()
            for status in statuses:
                if status.get('name') == status_name:
                    return status.get('id')
            return 1  # По умолчанию первый статус
        except:
            return 1

    def get_patent_type_id_by_name(self, type_name: str) -> int:
        """Получить ID типа патента по названию"""
        try:
            types = self.get_patent_types()
            for patent_type in types:
                if patent_type.get('name') == type_name:
                    return patent_type.get('id')
            return 1  # По умолчанию первый тип
        except:
            return 1

    # === Сотрудники (фильтры + обновление + удаление) ===
    # Сокращено с использованием **kwargs для чистоты
    def get_employees(self, **kwargs):
        params = {k: v for k, v in kwargs.items() if v is not None}
        return self.make_request("GET", "/reference/employees/", params=params)

    def get_employee(self, employee_id: int):
        return self.make_request("GET", f"/reference/employees/{employee_id}")

    def create_employee(self, data: Dict):
        return self.make_request("POST", "/reference/employees/", data=data)

    def update_employee(self, employee_id: int, data: Dict):
        return self.make_request("PUT", f"/reference/employees/{employee_id}", data=data)

    def delete_employee(self, employee_id: int):
        return self.make_request("DELETE", f"/reference/employees/{employee_id}")

    # === Авторы ===
    # Сокращено с использованием **kwargs для чистоты
    def get_authors(self, **kwargs):
        params = {k: v for k, v in kwargs.items() if v is not None}
        return self.make_request("GET", "/reference/authors/", params=params)

    def get_author(self, author_id: int):
        return self.make_request("GET", f"/reference/authors/{author_id}")

    def create_author(self, data: Dict):
        return self.make_request("POST", "/reference/authors/", data=data)

    def update_author(self, author_id: int, data: Dict):
        return self.make_request("PUT", f"/reference/authors/{author_id}", data=data)

    def delete_author(self, author_id: int):
        return self.make_request("DELETE", f"/reference/authors/{author_id}")

    # === Паспорта ===
    def get_passports(self, skip: int = 0, limit: int = 100):
        return self.make_request("GET", "/reference/passports/", params={"skip": skip, "limit": limit})

    def get_passport(self, passport_id: int):
        return self.make_request("GET", f"/reference/passports/{passport_id}")

    def create_passport(self, data: Dict):
        return self.make_request("POST", "/reference/passports/", data=data)

    def update_passport(self, passport_id: int, data: Dict):
        return self.make_request("PUT", f"/reference/passports/{passport_id}", data=data)

    def delete_passport(self, passport_id: int):
        return self.make_request("DELETE", f"/reference/passports/{passport_id}")

    # === Правообладатели ===
    def get_rights_holders(self, skip: int = 0, limit: int = 100):
        return self.make_request("GET", "/reference/rightsholders/", params={"skip": skip, "limit": limit})

    def get_rights_holder(self, holder_id: int):
        return self.make_request("GET", f"/reference/rightsholders/{holder_id}")

    def create_rights_holder(self, data: Dict):
        return self.make_request("POST", "/reference/rightsholders/", data=data)

    # === Заявки ===
    def get_applications(self):
        return self.make_request("GET", "/applications/")

    def get_application(self, application_id: int):
        return self.make_request("GET", f"/applications/{application_id}")

    def create_application(self, data: Dict):
        return self.make_request("POST", "/applications/", data=data)

    def update_application(self, application_id: int, data: Dict):
        return self.make_request("PUT", f"/applications/{application_id}", data=data)

    def delete_application(self, application_id: int):
        return self.make_request("DELETE", f"/applications/{application_id}")

    # === Патенты ===
    def get_patents(self):
        return self.make_request("GET", "/patents/")

    def get_patent(self, patent_id: int):
        return self.make_request("GET", f"/patents/{patent_id}")

    def create_patent(self, data: Dict):
        return self.make_request("POST", "/patents/", data=data)

    def update_patent(self, patent_id: int, data: Dict):
        return self.make_request("PUT", f"/patents/{patent_id}", data=data)

    def delete_patent(self, patent_id: int):
        return self.make_request("DELETE", f"/patents/{patent_id}")

    def get_expired_patents(self):
        return self.make_request("GET", "/patents/expired")

    # === Аналитика ===
    def get_activity_report(self):
        return self.make_request("GET", "/analytics/activity-report")

    def get_statistics_by_author(self):
        return self.make_request("GET", "/analytics/by-author")

    def get_statistics_by_year(self):
        return self.make_request("GET", "/analytics/by-year")

    def get_statistics_by_type(self):
        return self.make_request("GET", "/analytics/by-type")

    # === Вспомогательные ===
    def get_employee_full_name(self, employee_id: int) -> str:
        try:
            emp = self.get_employee(employee_id)
            return emp.get("full_name", "-")
        except:
            return "-"

    def get_author_full_name(self, author_id: int) -> str:
        try:
            author = self.get_author(author_id)
            return author.get("full_name", "-")
        except:
            return "-"

    def get_patent_type_name(self, patent_type_id: int) -> str:
        try:
            types = self.get_patent_types()
            for t in types:
                if t.get("id") == patent_type_id:
                    return t.get("name", "-")
            return "-"
        except:
            return "-"

    def get_status_name(self, status_id: int) -> str:
        try:
            statuses = self.get_statuses()
            for s in statuses:
                if s.get("id") == status_id:
                    return s.get("name", "-")
            return "-"
        except:
            return "-"