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

    def get_patent_types(self):
        return self.make_request("GET", "/reference/types")

    def get_employees(self):
        return self.make_request("GET", "/reference/employees")

    def get_authors(self):
        return self.make_request("GET", "/reference/authors")

    def get_rights_holders(self):
        return self.make_request("GET", "/reference/rightsholders")

    def get_applications(self):
        return self.make_request("GET", "/applications/")

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
        return self.make_request("GET", "/analytics/activity")

    def get_statistics_by_author(self):
        return self.make_request("GET", "/analytics/by-author")
