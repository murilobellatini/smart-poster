import os
import ast
import requests
from hashlib import sha256
from functools import wraps

from src.custom_logging import getLogger
from src.credentials import AD_ACCOUNT_ID, API_VERSION, FB_ACCESS_TOKEN_SANDBOX

logger = getLogger(__name__)


class SocialMediaInteractor():
    def __init__(self, endpoint: str,
                 api_version: str = API_VERSION,
                 ad_account_id: str = AD_ACCOUNT_ID,
                 access_token: str = FB_ACCESS_TOKEN_SANDBOX,
                 limit: int = 45,
                 locale: str = 'en_US'):

        self.endpoint = endpoint
        self.api_version = api_version
        self.ad_account_id = ad_account_id
        self.access_token = access_token
        self.limit = limit
        self.locale = locale
        self.url = self.compose_url()

    def compose_url(self):
        return f"https://graph.facebook.com/v{self.api_version}/act_{self.ad_account_id}/{self.endpoint}"

    def get(self, params: tuple):
        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        return requests.get(self.url, params=params, headers=headers)

    def get_authenticated(self, params: tuple):
        params = params + (('access_token', self.access_token),
                           ('limit', self.limit), ('locale', self.locale))
        return self.get(params=params)
