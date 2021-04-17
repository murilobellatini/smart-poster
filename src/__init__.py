"""
Scripts for storing global objects with preset parameters.
"""
from gcloud import storage
# from src.paths import GCS_BUCKET
from src import custom_logging as logging
from src.credentials import gcloud_credentials_dict
from oauth2client.service_account import ServiceAccountCredentials

# # loads Google Cloud credentials
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(
#     gcloud_credentials_dict)

# # creates GCP client and storage bucket object
# client = storage.Client(credentials=credentials)
# bucket = client.get_bucket(str(GCS_BUCKET))
