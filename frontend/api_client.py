import requests
import json
from typing import Optional, Dict, Any, List
from config import Config

class APIClient:
    def __init__(self):
        self.base_url = Config.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.user_info: Optional[Dict] = None
        self.token: Optional[str] = None

    def _request(self, method: str, endpoint: str, data: Any = None, params: Any = None) -> Dict:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=Config.API_TIMEOUT,
                verify=False
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка API: {str(e)}") from e

    # ============================================================
    #                       АУТЕНТИФИКАЦИЯ
    # ============================================================

    def login(self, username: str, password: str) -> Dict:
        data = {"username": username, "password": password}

        result = self._request("POST", "/api/login", data=data)

        # Берём токен
        self.token = result.get("access_token")
        if self.token:
            self.session.headers.update({"Authorization": f"Bearer {self.token}"})


        # Загружаем профиль user_type + id
        self.user_info = result.get("user")
        return result

    def register(self, username: str, password: str, email: str, user_type: str) -> Dict:
  

        data = {
            "username": username,
            "password": password,
            "email": email,
            "user_type": user_type
        }

        return self._request("POST", "/api/register", data=data)

    def logout(self):
        try:
            self._request("POST", "/api/logout")
        except:
            pass
        finally:
            self.session.close()

    def get_current_user(self) -> Dict:
        user = self._request("GET", "/api/me")
        self.user_info = user
        return user

    # ============================================================
    #                       ЗАЯВКИ
    # ============================================================

    def get_applications(self) -> List[Dict]:
        return self._request("GET", "/api/applications")["data"]

    def get_application(self, app_id: int) -> Dict:
        return self._request("GET", f"/api/applications/{app_id}")

    def create_application(self, data: Dict):
        self._request("POST", "/api/applications", data=data)

    def update_application(self, app_id: int, data: Dict):
        self._request("PUT", f"/api/applications/{app_id}", data=data)

    def delete_application(self, app_id: int):
        self._request("DELETE", f"/api/applications/{app_id}")

    # ============================================================
    #                       ПАТЕНТЫ
    # ============================================================

    def get_patents(self) -> List[Dict]:
        return self._request("GET", "/api/patents")["data"]

    def get_expired_patents(self) -> List[Dict]:
        return self._request("GET", "/api/patents/expired")["data"]

    def create_patent(self, data: Dict):
        self._request("POST", "/api/patents", data=data)

    def update_patent(self, patent_id: int, data: Dict):
        self._request("PUT", f"/api/patents/{patent_id}", data=data)

    def delete_patent(self, patent_id: int):
        self._request("DELETE", f"/api/patents/{patent_id}")

    # ============================================================
    #                       Справочники
    # ============================================================

    def get_statuses(self) -> List[Dict]:
        return self._request("GET", "/api/statuses")["data"]

    def get_patent_types(self) -> List[Dict]:
        return self._request("GET", "/api/patent-types")["data"]

    def get_employees(self) -> List[Dict]:
        return self._request("GET", "/api/employees")["data"]

    def get_authors(self) -> List[Dict]:
        return self._request("GET", "/api/authors")["data"]

    def get_rights_holders(self) -> List[Dict]:
        return self._request("GET", "/api/rights-holders")["data"]

    # ============================================================
    #                       Аналитика
    # ============================================================

    def get_activity_report(self) -> Dict:
        return self._request("GET", "/api/reports/activity")

    def get_statistics_by_author(self) -> Dict:
        return self._request("GET", "/api/reports/by-author")

    def get_statistics_by_year(self) -> Dict:
        return self._request("GET", "/api/reports/by-year")

    def get_statistics_by_type(self) -> Dict:
        return self._request("GET", "/api/reports/by-type")
