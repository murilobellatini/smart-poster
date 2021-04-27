"""
Credential files are loaded and stored in variables here.
"""
import os
import json
from src.paths import LOCAL_CREDENTIALS_PATH

# load facebook api data
AD_ACCOUNT_ID = os.environ.get('AD_ACCOUNT_ID')
API_VERSION = os.environ.get('API_VERSION', 10.0)
FB_ACCESS_TOKEN = os.environ.get('FB_ACCESS_TOKEN')
FB_ACCESS_TOKEN_SANDBOX = os.environ.get('FB_ACCESS_TOKEN_SANDBOX')

# Loads GCloud Credentials
GOOGLE_CLOUD_CREDENTIALS_PATH = LOCAL_CREDENTIALS_PATH / \
    'gcloud.json'

with open(GOOGLE_CLOUD_CREDENTIALS_PATH, mode='r') as json_file:
    gcloud_credentials_dict = json.load(json_file)

# Loads Unsplash Credentials

UNSPLASH_CRED_PATH = LOCAL_CREDENTIALS_PATH / 'unsplash.json'

with open(UNSPLASH_CRED_PATH, mode='r') as json_file:
    unsplash_credentials = json.load(json_file)
