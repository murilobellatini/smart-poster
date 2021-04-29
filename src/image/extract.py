import os
from src import ConfigLoader
from pyunsplash import PyUnsplash
from google_images_search import GoogleImagesSearch

from time import sleep
from src.custom_logging import getLogger
from src.paths import LOCAL_PROCESSED_DATA_PATH
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


class ImgExtractorFactory:

    def create_extractor(self, api: str, ignore_used_imgs: bool = True):
        if api == 'unsplash':
            return UnsplashImgExtractor(api=api, ignore_used_imgs=ignore_used_imgs)
        elif api == 'google':
            return GoogleImgExtractor(api=api, ignore_used_imgs=ignore_used_imgs)
        else:
            raise NotImplementedError


class ImgExtractor(ConfigLoader):

    def __init__(self, api: str, ignore_used_imgs: bool = True) -> None:
        super().__init__()

        self.logger = getLogger(self.__class__.__name__)
        if api not in api_instances.keys():
            raise NotImplementedError

        self.api = api
        self.api_instance = api_instances[self.api]
        self.metadata = {}
        self.curr_metadata = {}
        self.img_urls = set()  # all found image urls (accumulated)
        self.curr_img_urls = set()  # image urls from current pagination only
        if self.ignore_config:
            self.ignore_used_imgs = ignore_used_imgs


class UnsplashImgExtractor(ImgExtractor):

    def query(self, _search_params: dict) -> None:
        """
        _search_params = {
            'q': '...',
            'num': 10,
            'safe': 'high|medium|off',
            'fileType': 'jpg|gif|png',
            # imgType defaults to `photo`
            'imgType': google -> 'clipart|face|lineart|news|photo' / unsplash -> 'photos|colletions|users'
            'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
            'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow',
            'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
            'img_urls_to_ignore': [...],
            'num': 10
        }
        """
        self.logger.debug(
            f'Requesting API {self.api} for images... Query: {_search_params["q"]}')

        _search_params = self._get_default_params(_search_params)

        img_urls_to_ignore = []

        if self.ignore_used_imgs:
            used_imgs_path = LOCAL_PROCESSED_DATA_PATH / "used_data/used_img_urls.txt"
            if used_imgs_path.is_file():
                with open(used_imgs_path, mode="r") as fp:
                    img_urls_to_ignore = fp.read().splitlines()

        i = 0
        while not self.curr_img_urls:
            try:
                self.cursor = self.api_instance.search(
                    type_=_search_params['imgType'], query=_search_params['q'])  # @todo: generalize for `collections` and `users`
                self._update_img_metadata(
                    img_urls_to_ignore=img_urls_to_ignore,
                    min_return_count=_search_params.get('num')
                )
                i += 1
                if i == 7:
                    self.logger.warning(
                        f"7  Attempts made to retrieve Images  for query `{_search_params['q']}` with no results. Aborting process.")
                    break
            except Exception as e:
                self.logger.warning(
                    f'Image API `{self.api}` returned error. Probably quota has been exceeded... Waiting 10 min to retry request.\bError:')
                sleep(60*10)

    def _update_img_metadata(self, img_urls_to_ignore: list = None, min_return_count: int = 1) -> None:
        self.logger.debug(f'Gathering image urls into single list...')

        while len(self.img_urls) < min_return_count:
            self.curr_metadata = {
                r['urls']['full']: {
                    'author_name': r['user']['name'],
                    'instagram_username': r['user']['instagram_username'],
                    'username': r['user']['username'],
                    'portfolio_url': r['links']['html'],
                } for r in self.cursor.body['results']
                if r['urls']['full'] not in img_urls_to_ignore}

            self.curr_img_urls = set(self.curr_metadata.keys())

            self.img_urls.update(self.curr_img_urls)

            self.img_urls = set(
                url for url in list(self.img_urls) if url not in img_urls_to_ignore)

            self.metadata.update(self.curr_metadata)

            try:
                self.paginate_results(ignore_img_update=True)
            except Exception as e:
                self.logger.warning(
                    f'Pagination failed. Skipping process. `{self.img_urls}` might be unstable.\nError {e} ')
                break

    def _get_default_params(self, _search_params: dict) -> dict:

        if (not _search_params.get('imgType')) or ('photo' in _search_params.get('imgType')):
            _search_params['imgType'] = 'photos'

        if not _search_params.get('num'):
            _search_params['num'] = 10

        return _search_params

    def paginate_results(self, ignore_img_update: bool = False) -> None:
        self.logger.debug(f'Paginating image API results...')

        self.cursor = self.cursor.get_next_page()

        if not ignore_img_update:
            self._update_img_metadata()


class GoogleImgExtractor(ImgExtractor):

    def query(self, _search_params: dict) -> None:
        """
        _search_params = {
            'q': '...',
            'num': 10,
            'safe': 'high|medium|off',
            'fileType': 'jpg|gif|png',
            # imgType defaults to `photo`
            'imgType': google -> 'clipart|face|lineart|news|photo' / unsplash -> 'photos|colletions|users'
            'imgSize': 'huge|icon|large|medium|small|xlarge|xxlarge',
            'imgDominantColor': 'black|blue|brown|gray|green|pink|purple|teal|white|yellow',
            'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
            'img_urls_to_ignore': [...],
            'num': 10
        }
        """
        self.logger.debug(
            f'Requesting API {self.api} for images... Query: {_search_params["q"]}')

        _search_params = self._get_default_params(_search_params)

        img_urls_to_ignore = []

        if self.ignore_used_imgs:
            used_imgs_path = LOCAL_PROCESSED_DATA_PATH / "used_data/used_img_urls.txt"
            if used_imgs_path.is_file():
                with open(used_imgs_path, mode="r") as fp:
                    img_urls_to_ignore = fp.read().splitlines()

        self.api_instance.search(
            search_params=_search_params)
        self.cursor = self.api_instance.results()
        self._update_img_metadata(
            img_urls_to_ignore=img_urls_to_ignore,
            min_return_count=_search_params.get('num')
        )

    def _update_img_metadata(self, img_urls_to_ignore: list = None, min_return_count: int = 1) -> None:
        self.logger.debug(f'Gathering image urls into single list...')

        while len(self.img_urls) < min_return_count:

            self.curr_img_urls = set(im.url
                                     for im in list(self.cursor)
                                     if im.url not in img_urls_to_ignore)

            self.img_urls.update(self.curr_img_urls)

            self.img_urls = set(
                url for url in list(self.img_urls) if url not in img_urls_to_ignore)

            self.metadata.update(self.curr_metadata)

            try:
                self.paginate_results(ignore_img_update=True)
            except Exception as e:
                self.logger.warning(
                    f'Pagination failed. Skipping process. `{self.img_urls}` might be unstable.\nError {e} ')
                break

    def _get_default_params(self, _search_params: dict) -> dict:

        if (not _search_params.get('imgType')) or ('photo' in _search_params.get('imgType')):
            _search_params['imgType'] = 'photo'

        if not _search_params.get('num'):
            _search_params['num'] = 10

        return _search_params

    def paginate_results(self, ignore_img_update: bool = False) -> None:
        self.logger.debug(f'Paginating image API results...')

        self.api_instance.next_page()
        self.cursor = self.api_instance.results()

        if not ignore_img_update:
            self._update_img_metadata()
