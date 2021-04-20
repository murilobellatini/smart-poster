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
api_instances = {
    'unsplash': PyUnsplash(api_key=unsplash_key),
    'google': GoogleImagesSearch(google_key, google_cx)
}


class ApiImgExtractor():

    def __init__(self, api: str):

        if api not in api_instances.keys():
            raise NotImplementedError

        self.api = api
        self.api_instance = api_instances[self.api]
        self.img_urls = set()  # all found image urls (accumulated)
        self.curr_img_urls = set()  # image urls from current pagination only

    def query(self, _search_params: dict):
        """
        _search_params = {
            'q': '...',
            'num': 10,
            'safe': 'high|medium|off',
            'fileType': 'jpg|gif|png',
            'imgType': google -> 'clipart|face|lineart|news|photo' / unsplash -> 'photos|colletions|users'
            'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
            'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow',
            'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived'
        }
        """
        if self.api == 'unsplash':
            self.cursor = self.api_instance.search(
                type_=_search_params['imgType'], query=_search_params['q'])  # @todo: generalize for `collections` and `users`
            self._update_img_urls()

        elif self.api == 'google':
            self.api_instance.search(
                search_params=_search_params)
            self.cursor = self.api_instance.results()
            self._update_img_urls()

    def _update_img_urls(self):

        if self.api == 'unsplash':
            self.curr_img_urls = set(r['urls']['full']
                                     for r in self.cursor.body['results'])

        if self.api == 'google':
            self.curr_img_urls = set(im.url
                                     for im in self.cursor)

        self.img_urls.update(self.curr_img_urls)

    def paginate_results(self):
        if self.api == 'unsplash':
            self.cursor = self.cursor.get_next_page()
            self._update_img_urls()
        if self.api == 'google':
            self.api_instance.next_page()
            self.cursor = self.api_instance.results()
            self._update_img_urls()
