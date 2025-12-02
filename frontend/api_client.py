# frontend/api_client.py
import requests
from typing import Optional, Dict, Any, List
from config import Config


class APIClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL  # https://localhost:8000
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.user_info: Optional[Dict] = None
        self.token: Optional[str] = None
        self.session.verify = False  # для самоподписанного SSL

    def _request(self, method: str, endpoint: str, data: Any = None, params: Any = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=Config.API_TIMEOUT
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            try:
                detail = response.json().get("detail", str(e))
            except:
                detail = str(e)
            raise Exception(f"Ошибка API: {detail}") from e

    # ==================== АУТЕНТИФИКАЦИЯ ====================
    def register(self, data: Dict) -> Dict:
        return self._request("POST", "/auth/register", data=data)

    def login(self, username: str, password: str) -> Dict:
        result = self._request("POST", "/auth/login", data={"username": username, "password": password})
        self.token = result.get("access_token")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})
        self.user_info = result.get("user")
        return result

    def logout(self):
        try:
            self._request("POST", "/auth/logout")
        except:
            pass
        finally:
            self.session.close()

    def get_current_user(self) -> Dict:
        user = self._request("GET", "/auth/me")
        self.user_info = user
        return user

    # ==================== СПРАВОЧНИКИ ====================
    def get_statuses(self) -> List[Dict]:
        return self._request("GET", "/reference/statuses")["data"]

    def get_patent_types(self) -> List[Dict]:
        return self._request("GET", "/reference/types")["data"]

    def get_employees(self) -> List[Dict]:
        return self._request("GET", "/reference/employees")["data"]

    def get_authors(self) -> List[Dict]:
        return self._request("GET", "/reference/authors")["data"]

    def get_rights_holders(self) -> List[Dict]:
        return self._request("GET", "/reference/rightsholders")["data"]

    # ==================== ЗАЯВКИ ====================
    def get_applications(self) -> List[Dict]:
        return self._request("GET", "/applications/")["data"]

    def create_application(self, data: Dict):
        self._request("POST", "/applications/", data=data)

    # ==================== ПАТЕНТЫ ====================
    def get_patents(self) -> List[Dict]:
        return self._request("GET", "/patents/")["data"]

    def get_expired_patents(self) -> List[Dict]:
        return self._request("GET", "/patents/expired")["data"]

    # ==================== АНАЛИТИКА ====================
    def get_activity_report(self) -> Dict:
        return self._request("GET", "/analytics/activity")

    def get_statistics_by_author(self) -> Dict:
        return self._request("GET", "/analytics/by-author")