# zcc-recording-archiver

## Python script to download historical recordings from Zoom Contact Center

This script will query the ZCC API for historic recordings based on a date/time window specified in the main.py file (refer to **START_DATE** and **END_DATE** variables). Each recording found will create an instance of the Recording class, and a list of Recording objects will be returned.

Recording objects have a **download** method which can be used to download the recording to the path specified in the **RECORDING_PATH** variable. The list of recording objects is interated over, and the `download` method is called on each. The `download` method will perform a GET request to the download URL and store the recording locally within the specified path (refer to the **RECORDING_PATH** variable)

To run this script you must install the modules shown in the **requirements.txt** file by running the following command.

`pip install -r requirements.txt`

Next, open the `main.py` file and modify the following variables:

**START_DATE**: The start date/time of the date range that you'd like to query
**END_DATE**: The end date/time of the date range that you'd like to query
**RECORDING_PATH**: The path to the location where you would like to store the downloaded recordings

You must login to <https://marketplace.zoom.us> and create a new Server-to-Server OAuth app with the `contact_center_recording:read:admin` scope enabled. Once this is created you must populate the **ACCOUNT_ID**, **CLIENT_ID** and **CLIENT_SECRET** environment variables using the values from your Server-to-Server app. Rename the `.env_sample` file to `.env` and populate these values here. Note, the use of quotation marks is NOT required in the .env file.

Further information about Server-to-Server OAuth can be found here:

<https://marketplace.zoom.us/docs/guides/build/server-to-server-oauth-app/>

Information about the ZCC API endpoint used to provide historical recordings can be found here:

<https://developers.zoom.us/docs/api/rest/reference/contact-center/methods/#operation/listRecordings>
