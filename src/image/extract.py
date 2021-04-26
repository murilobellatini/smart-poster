import os
from pyunsplash import PyUnsplash
from google_images_search import GoogleImagesSearch

from time import sleep
from src.custom_logging import getLogger
from src.paths import LOCAL_PROCESSED_DATA_PATH
from src.credentials import unsplash_credentials


logger = getLogger(__name__)

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

    def __init__(self, api: str, ignore_used_imgs: bool = True) -> None:

        if api not in api_instances.keys():
            raise NotImplementedError

        self.api = api
        self.api_instance = api_instances[self.api]
        self.img_urls = set()  # all found image urls (accumulated)
        self.curr_img_urls = set()  # image urls from current pagination only
        self.ignore_used_imgs = ignore_used_imgs

    def query(self, _search_params: dict) -> None:
        """
        _search_params = {
            'q': '...',
            'num': 10,
            'safe': 'high|medium|off',
            'fileType': 'jpg|gif|png',
            'imgType': google -> 'clipart|face|lineart|news|photo' / unsplash -> 'photos|colletions|users'
            'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
            'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow',
            'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
            'img_urls_to_ignore': [...],
            'return_count': 10
        }
        """
        img_urls_to_ignore = []

        if self.ignore_used_imgs:
            used_imgs_path = LOCAL_PROCESSED_DATA_PATH / "USED_URLS/used_img_urls.txt"
            if used_imgs_path.is_file():
                with open(used_imgs_path, mode="r") as fp:
                    img_urls_to_ignore = fp.read().splitlines()

        if self.api == 'unsplash':
            while not self.img_urls:
                try:
                    self.cursor = self.api_instance.search(
                        type_=_search_params['imgType'], query=_search_params['q'])  # @todo: generalize for `collections` and `users`
                except Exception as e:
                    logger.error(
                        f'Image API `{self.api}` returned error. Probably quota has been exceeded... Waiting 10 min to retry request.')
                    sleep(60*10)

            self._update_img_urls(
                img_urls_to_ignore=img_urls_to_ignore,
                min_return_count=_search_params.get('return_count')
            )

        elif self.api == 'google':
            self.api_instance.search(
                search_params=_search_params)
            self.cursor = self.api_instance.results()
            self._update_img_urls(
                img_urls_to_ignore=img_urls_to_ignore,
                min_return_count=_search_params.get('return_count')
            )

    def _update_img_urls(self, img_urls_to_ignore: list = None, min_return_count: int = 1) -> None:

        while len(self.img_urls) < min_return_count:
            if self.api == 'unsplash':
                self.curr_img_urls = set(r['urls']['full']
                                         for r in list(self.cursor.body['results'])
                                         if r['urls']['full'] not in img_urls_to_ignore)

            if self.api == 'google':
                self.curr_img_urls = set(im.url
                                         for im in list(self.cursor)
                                         if im.url not in img_urls_to_ignore)

            self.img_urls.update(self.curr_img_urls)

            self.img_urls = set(
                url for url in list(self.img_urls) if url not in img_urls_to_ignore)

            try:
                self.paginate_results(ignore_img_update=True)
            except Exception as e:
                logger.error(
                    'Pagination failed. Skipping process. `self.img_urls` might be unstable;')
                break

    def paginate_results(self, ignore_img_update: bool = False) -> None:
        if self.api == 'unsplash':
            self.cursor = self.cursor.get_next_page()
        if self.api == 'google':
            self.api_instance.next_page()
            self.cursor = self.api_instance.results()

        if not ignore_img_update:
            self._update_img_urls()
