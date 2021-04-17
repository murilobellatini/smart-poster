"""
Credential files are loaded and stored in variables here.
"""
import json
from src.paths import LOCAL_CREDENTIALS_PATH

GOOGLE_CLOUD_CREDENTIALS_PATH = LOCAL_CREDENTIALS_PATH / \
    'google-cloud-credentials.json'

with open(GOOGLE_CLOUD_CREDENTIALS_PATH, mode='r') as json_file:
    gcloud_credentials_dict = json.load(json_file)
