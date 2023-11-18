import base64
from datetime import datetime
import logging
import os
from pathlib import Path
from sys import exit

from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(format="%(levelname)s:%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S", level=logging.INFO)

# Load the required environment variables from .env
load_dotenv()
ZOOM_ACCOUNT_ID = os.environ.get("ZOOM_ACCOUNT_ID")
ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")

# Set the path where you would like to store the recordings
RECORDING_PATH = Path("/Users/cletheren/Recordings")

# Set the timeframe for the download
START_DATE = "2023-10-01T00:00:00"
END_DATE = "2023-10-31T23:59:59"

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
    
class Recording:
    """Object to represent a recorded asset"""

    def __init__(
            self,
            start_time: str,
            engagement_id: str,
            channel_type: str,
            recording_id: str,
            download_url: str
            ) -> None:
        self.start_time = start_time
        self.engagement_id = engagement_id
        self.channel_type = channel_type
        self.recording_id = recording_id
        self.download_url = download_url

    def download(self, client: Client, path: Path) -> None:
        headers = {
            "Authorization": f"Bearer {client.token}"
        }
        start_time = datetime.fromisoformat(self.start_time).strftime("%y%d%m_%H%M%S")
        try:
            if not path.exists():
                path.mkdir(parents=True)
        except PermissionError as err:
            logging.info(f"{err}, please check your RECORDING_PATH and try again")
            quit()
        extension = "mp3" if self.channel_type == "voice" else "mp4"
        filename = f"{start_time}_{self.engagement_id}_{self.recording_id}.{extension}"
        filename = Path(path, filename)
        with requests.Session() as req:
            if client.token_has_expired:
                    logging.debug("Bearer token has expired, generating a new one...")
                    client.get_token()
                    headers["Authorization"] = f"Bearer {client.token}"
            try:
                r = req.get(self.download_url, headers=headers, stream=True)
                logging.debug(f"Downloading {self.download_url}")
                r.raise_for_status()
                with open(filename, mode="wb") as f:
                    logging.info(f"Saving as {filename}")
                    for chunk in r.iter_content(chunk_size=10 * 1204):
                        f.write(chunk)
            except requests.HTTPError as err:
                logging.warning(err)
        return None
        
    def __repr__(self):
        return f"Recording(start_time={self.start_time!r}, engagement_id={self.engagement_id!r}, recording_id={self.recording_id!r}, channel_type={self.channel_type!r}, download_url={self.download_url!r})"

def get_recording_list(client: Client) -> list[Recording]:
    logging.info("Getting list of recordings...")
    recording_list = []
    endpoint = f"{client.base_url}/contact_center/recordings"
    headers = {
        "Authorization": f"Bearer {client.token}",
    }
    params = {
        "from": START_DATE,
        "to": END_DATE,
        "channel_type": "voice",
        "next_page_token": ""
    }

    with requests.Session() as req:
        try:
            while True:
                if client.token_has_expired:
                    logging.debug("Bearer token has expired, generating a new one...")
                    client.get_token()
                    headers["Authorization"] = f"Bearer {client.token}"
                r = requests.get(endpoint, headers=headers)
                r.raise_for_status()
                response_body = r.json()
                if response_body["recordings"]:
                    for recording in response_body["recordings"]:
                        recording_list.append(
                            Recording(
                                recording["recording_start_time"],
                                recording["engagement_id"],
                                recording["channel_type"],
                                recording["recording_id"],
                                recording["download_url"]
                            )
                        )
                params["next_page_token"] == r.json()["next_page_token"]
                if not params["next_page_token"]:
                    break
        except requests.HTTPError as err:
            logging.info("Unable to retrieve the list of recordings")
            logging.debug(err)
            exit(1)
    logging.info(f"Returning {len(recording_list)} records")
    return recording_list

def main() -> None:
    client = Client(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_ACCOUNT_ID)
    client.get_token()
    logging.info(f"Recording path is {RECORDING_PATH}")
    recording_list = get_recording_list(client)
    if recording_list:
        for recording in recording_list:
            recording.download(client, RECORDING_PATH)
        logging.info("Finished!")

if __name__ == "__main__":
    main()