import requests
from bs4 import BeautifulSoup
import json
import logging

class IvaSmsApi:
    """
    A service class to handle all API interactions with ivasms.com.
    """
    LOGIN_URL = "https://www.ivasms.com/login"
    PORTAL_URL = "https://www.ivasms.com/portal"
    SMS_URL = "https://www.ivasms.com/portal/live/my_sms"
    NUMBERS_URL = "https://www.ivasms.com/portal/live/getNumbers"

    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def _get_csrf_token(self) -> str:
        """Fetches the CSRF token from the portal page."""
        try:
            response = self.session.get(self.PORTAL_URL)
            soup = BeautifulSoup(response.text, "html.parser")
            csrf_token_tag = soup.find("meta", {"name": "csrf-token"})
            if csrf_token_tag:
                return csrf_token_tag["content"]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch CSRF token: {e}")
        return ""

    def login(self, email, password) -> bool:
        """Attempts to log in and returns True on success, False otherwise."""
        try:
            response = self.session.get(self.LOGIN_URL)
            soup = BeautifulSoup(response.text, "html.parser")
            csrf_token_tag = soup.find("input", {"name": "_token"})
            
            if not csrf_token_tag:
                self.logger.error("Login token not found.")
                return False
            csrf_token = csrf_token_tag["value"]

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Referer': self.LOGIN_URL,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://www.ivasms.com',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # NOTE: reCAPTCHA is a major blocker. Using a placeholder for demonstration.
            login_data = {
                '_token': csrf_token,
                'email': email,
                'password': password,
                'remember': 'on',
                'g-recaptcha-response': 'simulated_recaptcha_response', 
                'submit': 'register'
            }
            
            login_response = self.session.post(self.LOGIN_URL, headers=headers, data=login_data)
            
            return "portal" in login_response.url
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Login API error: {e}")
            return False

    def get_sms_messages(self) -> list:
        """Retrieves and parses recent SMS messages."""
        try:
            response = self.session.get(self.SMS_URL)
            if response.status_code != 200:
                self.logger.error(f"Failed to retrieve SMS, status code: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, "html.parser")
            sms_table = soup.find("table", {"id": "my_live_sms_table"})
            
            if not sms_table:
                return []

            messages = []
            rows = sms_table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 3:
                    messages.append({
                        "number": cols[0].text.strip(),
                        "message": cols[1].text.strip(),
                        "date": cols[2].text.strip()
                    })
            return messages
        except requests.exceptions.RequestException as e:
            self.logger.error(f"SMS retrieval API error: {e}")
            return []

    def get_numbers_list(self, termination_id: str) -> list:
        """Retrieves a list of numbers for a given termination_id."""
        try:
            csrf_token = self._get_csrf_token()
            if not csrf_token:
                self.logger.error("CSRF token not available for get_numbers.")
                return []

            headers = {
                'accept': '*/*',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': 'https://www.ivasms.com',
                'referer': self.SMS_URL,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                'X-CSRF-TOKEN': csrf_token,
            }
            
            post_data = {
                'termination_id': termination_id,
                '_token': csrf_token,
            }
            
            response = self.session.post(self.NUMBERS_URL, headers=headers, data=post_data)
            response.raise_for_status()
            
            numbers_data = response.json()
            return numbers_data.get("data", [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Get Numbers API error: {e}")
            return []
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON response from get_numbers API.")
            return []