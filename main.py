"""
Connect to the Zoom Contact Center API, download recorded conversations and
store them locally. Recordings are downloaded within a specified date/time range.
"""

import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import requests
import timeframes
from zoom import Client

# Configure logging
logging.basicConfig(format="%(levelname)s:%(asctime)s %(message)s", datefmt="%d/%m/%Y %H:%M:%S", level=logging.INFO)

# Load the environment variables from .env file. These should be populated with information from the Zoom S2S marketplace app.
load_dotenv()
ZOOM_ACCOUNT_ID = str(os.environ.get("ZOOM_ACCOUNT_ID"))
ZOOM_CLIENT_ID = str(os.environ.get("ZOOM_CLIENT_ID"))
ZOOM_CLIENT_SECRET = str(os.environ.get("ZOOM_CLIENT_SECRET"))

# Set the path where you would like to store the recordings
RECORDING_PATH = Path.home() / "Desktop" / "Recordings"


class Recording:
    """Object to represent a recorded asset

    The __init__ method may be documented in either the class level
    docstring, or as a docstring on the __init__ method itself.

    Either form is acceptable, but the two should not be mixed. Choose one
    convention to document the __init__ method and be consistent with it.

    Args:
        start_time (str): The time and date the recording started, in ISO 8601 format.
        engagement_id (str): The unique identifier for the engagement from the Zoom API.
        channel_type (str): The channel type, either voice, video, chat or sms.
        recording_id (str): The unique identifier for the recording from the Zoom API.
        download_url (str): The URL provided by the Zoom API that is used to download the recording.

    Attributes:
        start_time (str): The time and date the recording started, in ISO 8601 format.
        engagement_id (str): The unique identifier for the engagement from the Zoom API.
        channel_type (str): The channel type, either voice, video, chat or sms.
        recording_id (str): The unique identifier for the recording from the Zoom API.
        download_url (str): The URL provided by the Zoom API that is used to download the recording.
        filename (str): The filename generated based on start_time, engagement_id, recording_id and channel_type.

    """

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
        self.filename = f"{start_time}_{self.engagement_id}_{self.recording_id}.{
            "mp3" if self.channel_type == "voice" else "mp4"}"

    def download(self, client: Client, path: Path) -> bool:
        """Method to download the recorded asset represented by the object. This method will accept a client connection
        object containing a valid bearer token for accessing the Zoom API, and a Path object containing the path where
        the recording should be saved. 

        Args:
            client (zoom.Client): The Zoom client connection object that contains the bearer token and base URL.
            path (pathlib.Path): A path object, where the recording should be stored locally. 

        Returns:
            True if successful. Any failed attempt to download will exit with sys.exit(1)
        """
        headers = {
            "Authorization": f"Bearer {client.token}"
        }
        # start_time = datetime.fromisoformat(self.start_time).strftime("%y%d%m_%H%M%S")
        try:
            if not path.exists():
                path.mkdir(parents=True)
        except PermissionError as err:
            logging.info(
                "%s, please check your RECORDING_PATH and try again", err)
            exit(1)
        filename = Path(path, self.filename)
        with requests.Session() as req:
            if client.token_has_expired:
                logging.debug(
                    "Bearer token has expired, generating a new one...")
                client.get_token()
                headers["Authorization"] = f"Bearer {client.token}"
            try:
                r = req.get(self.download_url, headers=headers, stream=True)
                logging.debug("Downloading %s", self.download_url)
                r.raise_for_status()
                with open(filename, mode="wb") as f:
                    logging.info("Saving as %s", filename)
                    for chunk in r.iter_content(chunk_size=10 * 1204):
                        f.write(chunk)
            except requests.HTTPError as err:
                logging.warning(err)
        return True

    def __repr__(self):
        return f"Recording(start_time={self.start_time!r}, engagement_id={self.engagement_id!r}, recording_id={self.recording_id!r}, channel_type={self.channel_type!r}, download_url={self.download_url!r})"


def get_recording_list(client: Client, date_range: callable) -> list[Recording]:
    """Method to query the Zoom API to obtain a list of recordings based on the start and end date range provided.

    Args:
        client (zoom.Client): The Zoom client connection object that contains the bearer token and base URL.
        start_range (str): The starting date & time in ISO 8601 format, example '2023-09-01T00:00:00'.
        end_range (str): The ending date & time in ISO 8601 format, example '2023-09-30T23:59:59'.

    Returns:
        A list of Recording objects. If no recordings are returned by the API then an empty list is returned.
    """
    logging.info("Getting list of recordings...")
    recording_list = []
    endpoint = f"{client.base_url}/contact_center/recordings"
    headers = {
        "Authorization": f"Bearer {client.token}",
    }
    params = {
        **date_range(),
        "channel_type": "voice",
        "next_page_token": ""
    }

    with requests.Session() as req:
        try:
            while True:
                if client.token_has_expired:
                    logging.debug(
                        "Bearer token has expired, generating a new one...")
                    client.get_token()
                    headers["Authorization"] = f"Bearer {client.token}"
                r = req.get(endpoint, headers=headers, timeout=3000)
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
                params["next_page_token"] = r.json()["next_page_token"]
                if not params["next_page_token"]:
                    break
        except requests.HTTPError as err:
            logging.info("Unable to retrieve the list of recordings")
            logging.debug(err)
            sys.exit(1)
    logging.info("Returning %s records", len(recording_list))
    return recording_list


def main() -> None:
    """Main loop."""
    client = Client(ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, ZOOM_ACCOUNT_ID)
    client.get_token()
    logging.info("Recording path is %s", RECORDING_PATH)
    recording_list = get_recording_list(client, timeframes.last_week)
    if recording_list:
        for recording in recording_list:
            recording.download(client, RECORDING_PATH)
        logging.info("Finished!")


if __name__ == "__main__":
    main()
