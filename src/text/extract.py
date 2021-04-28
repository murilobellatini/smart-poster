
from quote import quote

from src.paths import LOCAL_PROCESSED_DATA_PATH
from src.custom_logging import getLogger
from src.text import Quote
from src import ConfigLoader


class QuoteExtractor(ConfigLoader):

    def __init__(self, query: str, quote_source: str = 'QUOTE_API', limit: int = 10, ignore_used_quotes: bool = True):

        super().__init__()

        self.logger = getLogger(self.__class__.__name__)

        if self.ignore_config:
            self.quote_source = quote_source
            self.ignore_used_quotes = ignore_used_quotes

        self.query = query
        self.limit = limit

        self._extract_quotes()

    def _extract_quotes(self) -> None:
        self.logger.debug(f'Extracting quotes from `{self.quote_source}`...')

        quotes_to_ignore = []

        if self.ignore_used_quotes:
            used_quotes_path = LOCAL_PROCESSED_DATA_PATH / "used_data/used_quotes.txt"
            if used_quotes_path.is_file():
                with open(used_quotes_path, mode="r") as fp:
                    quotes_to_ignore = [l.split(',')[0]
                                        for l in fp.read().splitlines()]

        if self.quote_source == 'QUOTE_API':
            unused_results = results = []
            limit = self.limit

            while not unused_results:

                for r in quote(search=self.query, limit=limit):

                    q = Quote(
                        author=r.get('author'),
                        quote=r.get('quote'),
                        source=r.get('book'),
                        source_type='book'
                    )
                    results.append(q)

                unused_results = [
                    q for q in results if q.id not in quotes_to_ignore]

                limit = limit*2  # @todo: improve logic
            self.results = unused_results[:self.limit]
        else:
            raise NotImplementedError
