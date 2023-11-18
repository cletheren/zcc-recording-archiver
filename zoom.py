from datetime import datetime
import base64
import logging

import requests

logging.basicConfig(format="%(levelname)s:%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S", level=logging.INFO)

class Client:
    """Connect to Zoom via OAuth and manage the bearer token"""

    base_url = "https://api.zoom.us/v2"
    
    def __init__(self, client_id: str, client_secret: str, account_id: str) -> None:
        self.account_id = account_id
        self.client_id = client_id
        self.b64 = base64.b64encode(f"{self.client_id}:{client_secret}".encode()).decode()

    def get_token(self) -> str:
        url = "https://zoom.us/oauth/token"
        headers = {
            "Authorization": f"Basic {self.b64}",
        }
        params = {
            "account_id": self.account_id,
            "grant_type": "account_credentials"
        }
        try:
            logging.debug("Generating a new bearer token...")
            r = requests.post(url, headers=headers, params=params)
            r.raise_for_status()
            response_body = r.json()
            self.token = response_body["access_token"]
            self.expiry_time = datetime.now().timestamp() + response_body["expires_in"]
            logging.debug(f"New token generated, expires at {self.expiry_time}")
        except requests.HTTPError as err:
            print(err)
            exit(1)
        return r.json()["access_token"]
    
    @property
    def token_has_expired(self) -> bool:
        now = datetime.now().timestamp()
        return now > self.expiry_time
