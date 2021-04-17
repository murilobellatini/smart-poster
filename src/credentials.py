"""
Credential files are loaded and stored in variables here.
"""
import json
from src.paths import LOCAL_CREDENTIALS_PATH

# Loads GCloud Credentials
GOOGLE_CLOUD_CREDENTIALS_PATH = LOCAL_CREDENTIALS_PATH / \
    'gcloud.json'

with open(GOOGLE_CLOUD_CREDENTIALS_PATH, mode='r') as json_file:
    gcloud_credentials_dict = json.load(json_file)

# Loads Unsplash Credentials

UNSPLASH_CRED_PATH = LOCAL_CREDENTIALS_PATH / 'unsplash.json'

with open(UNSPLASH_CRED_PATH, mode='r') as json_file:
    unsplash_credentials = json.load(json_file)
