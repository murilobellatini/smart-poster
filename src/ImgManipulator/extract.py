import pyunsplash
from pyunsplash import PyUnsplash
from src.credentials import unsplash_credentials

api_key = unsplash_credentials['ACCESS_KEY']

# instantiate PyUnsplash object
unsplash = PyUnsplash(api_key=api_key)
