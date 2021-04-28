"""
Scripts for storing global objects with preset parameters.
"""
import yaml
from gcloud import storage
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# from src.paths import GCS_BUCKET
from src.paths import root_path
from src import custom_logging as logging
from src.credentials import gcloud_credentials_dict


load_dotenv()


class ConfigLoader():

    def __init__(self, config_path: str = root_path / 'config.yaml'):

        with open(config_path) as stream:
            try:
                config = yaml.safe_load(stream).values()
                self.config = {k: v for d in config for k, v in d.items()}
            except yaml.YAMLError as exc:
                print(exc)

        for k, v in self.config.items():

            if v == "[IGNORE]" or k.endswith('_VALUES'):
                continue

            setattr(self, k, v)

# # loads Google Cloud credentials
# credentials = ServiceAccountCredentials.from_json_keyfile_dict(
#     gcloud_credentials_dict)

# # creates GCP client and storage bucket object
# client = storage.Client(credentials=credentials)
# bucket = client.get_bucket(str(GCS_BUCKET))
