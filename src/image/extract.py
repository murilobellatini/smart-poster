import pyunsplash
from pyunsplash import PyUnsplash
from src.credentials import unsplash_credentials

api_key = unsplash_credentials['ACCESS_KEY']

# instantiate PyUnsplash object
unsplash = PyUnsplash(api_key=api_key)


def search(query: str, type_: str = 'photos', api="unsplash"):
    """
    Searchs `type_` data (`photos`, `collections` or `users`)
    based on `query` via `api`
    """
    if api == "unsplash":
        return unsplash.search(type_=type_, query=query)
    else:
        raise NotImplementedError
