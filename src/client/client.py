import requests
import urllib3
from typing import Optional, Dict, Any

import src.client.config as config


urllib3.disable_warnings()


class Client:
    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.user: Optional[Dict] = None
        self.session.verify = False

    def make_request(self, method: str, endpoint: str, data: Any = None, params: Any = None):
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=config.API_TIMEOUT
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            try:
                detail = response.json().get("detail", str(e))
            except:
                detail = str(e)
            raise Exception(f"Ошибка API: {detail}") from e

    def get_positions(self):
        return self.make_request("GET", "/reference/positions")

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

    def get_statuses(self):
        return self.make_request("GET", "/reference/statuses/")

    def get_status(self, status_id: int):
        return self.make_request("GET", f"/reference/statuses/{status_id}")

    def get_patent_types(self):
        return self.make_request("GET", "/reference/types/")

    def get_employees(self):
        return self.make_request("GET", "/reference/employees")

    def get_employee(self, employee_id: int):
        return self.make_request("GET", f"/reference/employees/{employee_id}")

    def get_authors(self):
        return self.make_request("GET", "/reference/authors/")

    def get_author(self, author_id: int):
        return self.make_request("GET", f"/reference/authors/{author_id}")

    def get_passports(self):
        return self.make_request("GET", "/reference/passports/")

    def create_passport(self, data: Dict):
        return self.make_request("POST", "/reference/passports/", data=data)

    def create_author(self, data: Dict):
        return self.make_request("POST", "/reference/authors/", data=data)

    def get_rights_holders(self):
        return self.make_request("GET", "/reference/rightsholders/")

    def get_rights_holder(self, rights_holder_id: int):
        return self.make_request("GET", f"/reference/rightsholders/{rights_holder_id}")

    def create_rights_holder(self, data: Dict):
        return self.make_request("POST", "/reference/rightsholders/", data=data)

    def get_applications(self):
        return self.make_request("GET", "/applications/")

    def get_application(self, application_id: int):
        return self.make_request("GET", f"/applications/{application_id}")

    def create_application(self, data: Dict):
        self.make_request("POST", "/applications/", data=data)

    def delete_application(self, id):
        self.make_request("DELETE", f"/applications/{id}")

    def update_application(self, id: int, data: Dict):
        self.make_request("PUT", f"/applications/{id}", data=data)

    def create_patent(self, data: Dict):
        self.make_request("POST", "/patents/", data=data)

    def update_patent(self, id: int, data: Dict):
        self.make_request("PUT", f"/patents/{id}", data=data)

    def delete_patent(self, id: int):
        self.make_request("DELETE", f"/patents/{id}")

    def get_patents(self):
        return self.make_request("GET", "/patents/")

    def get_expired_patents(self):
        return self.make_request("GET", "/patents/expired")

    def get_activity_report(self):
        return self.make_request("GET", "/analytics/activity-report")

    def get_statistics_by_author(self):
        return self.make_request("GET", "/analytics/by-author")

    def get_statistics_by_year(self):
        return self.make_request("GET", "/analytics/by-year")

    def get_statistics_by_type(self):
        return self.make_request("GET", "/analytics/by-type")

    def get_employee_full_name(self, employee_id: int):
        employee = self.get_employee(employee_id)
        return employee['full_name']

    def get_author_full_name(self, author_id: int):
        authors = self.get_authors()

        for author in authors:
            if author['id'] == author_id:
                return author['full_name']
        return '-'

    def get_patent_type_name(self, patent_type_id: int) -> str:
        patent_types = self.get_patent_types()

        for patent_type in patent_types:
            if patent_type.get('id') == patent_type_id:
                return patent_type.get('name')
        return '-'

    def get_status_id_by_name(self, name: str):
        statuses = self.get_statuses()

        for status in statuses:
            if status.get('name') == name:
                return status.get('id')
        return -1

    def get_patent_type_id_by_name(self, name: str):
        patent_types = self.get_patent_types()

        for patent_type in patent_types:
            if patent_type.get('name') == name:
                return patent_type.get('id')
        return -1

    def get_rights_holder_id_by_name(self, name: str):
        rights_holders = self.get_rights_holders()

        for rights_holder in rights_holders:
            if rights_holder.get('name') == name:
                return rights_holder.get('id')
        return -1

    def get_rights_holder_name(self, rights_holder_id: int):
        rights_holders = self.get_rights_holders()

        for rights_holder in rights_holders:
            if rights_holder.get('id') == rights_holder_id:
                return rights_holder.get('name')
        return '-'
