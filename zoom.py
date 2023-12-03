"""
Module used to authenticate with a Zoom Server to Server marketplace app. A class
represents the connection, with methods to request and subsequently renew a temporary
bearer token used for authenticating with the Zoom API.
"""

from datetime import datetime
import base64
import logging
import sys

import requests

logging.basicConfig(format="%(levelname)s:%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S", level=logging.INFO)


class Client:
    """Connect to a Zoom Server to Server OAuth app and manage the bearer token
    for subsequent API calls.

    Args:
        client_id (str): The Marketplace app Client ID
        client_secret (str): The Marketplace app Client Secret
        account_id (str): The Marketplace app Account ID

    Attributes:
        client_id (str): The Marketplace app Client ID
        account_id (str): The Marketplace app Account ID
        token (str): The bearer token used to authenticate API calls
        expiry_time (float): The expiry time of the bearer token in POSIX timestamp
        b64 (str): Basic token used for authenticating a bearer token request
    """

    base_url = "https://api.zoom.us/v2"

    def __init__(self, client_id: str, client_secret: str, account_id: str) -> None:
        self.account_id = account_id
        self.client_id = client_id
        self.token = None
        self.expiry_time = None
        self.b64 = base64.b64encode(
            f"{self.client_id}:{client_secret}".encode()).decode()

    def get_token(self) -> str:
        """Contact the Zoom OAuth endpoint to generate a new token.

        Returns:
            The new bearer token as a string.
        """

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
            r = requests.post(url, headers=headers, params=params, timeout=3000)
            r.raise_for_status()
            response_body = r.json()
            self.token = response_body["access_token"]
            self.expiry_time = datetime.now().timestamp() + response_body["expires_in"]
            logging.debug("New token generated, expires at %s", self.expiry_time)
        except requests.HTTPError as err:
            print(err)
            sys.exit(1)
        return r.json()["access_token"]

    @property
    def token_has_expired(self) -> bool:
        """Check if the current bearer token is still valid.

        Returns:
            bool: True if the token has expired, otherwise False.
        """
        now = datetime.now().timestamp()
        return now > self.expiry_time
