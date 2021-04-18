import os
import pyunsplash
from pyunsplash import PyUnsplash
from google_images_search import GoogleImagesSearch

from src.credentials import unsplash_credentials

# get keys for apis
unsplash_key = os.environ.get('UNSPLASH_ACCESS_KEY')
google_key = os.environ.get('GCP_KEY')
google_cx = os.environ.get('GCX')

# instantiate image search objects
unsplash = PyUnsplash(api_key=unsplash_key)
gis = GoogleImagesSearch(google_key, google_cx)


def search(query: str, type_: str = 'photos', api:str="unsplash", min_results:int=10):
    """
    Searchs `type_` data (`photos`, `collections` or `users`)
    based on `query` via `api`
    """
    if api == "unsplash":
        return unsplash.search(type_=type_, query=query)
    elif api == 'google':
        _search_params = {
            'q': query,
            'imgType': type_,
            'num': min_results
        }
        gis.search(search_params=_search_params)
        return gis
    else:
        raise NotImplementedError
