
from quote import quote

from src.paths import LOCAL_PROCESSED_DATA_PATH
from src.custom_logging import getLogger
from src.text import Quote
from src import ConfigLoader

logger = getLogger(__name__)


class QuoteExtractor(ConfigLoader):

    def __init__(self, query: str, quote_source: str = 'QUOTE_API', limit: int = None, ignore_used_quotes: bool = True):

        super().__init__()

        if self.ignore_config:
            self.quote_source = quote_source
            self.ignore_used_quotes = ignore_used_quotes

        self.query = query
        self.limit = limit

        self._extract_quotes()

    def _extract_quotes(self) -> None:
        logger.debug(f'Extracting quotes from `{self.quote_source}`...')

        quotes_to_ignore = []

        if self.ignore_used_quotes:
            used_quotes_path = LOCAL_PROCESSED_DATA_PATH / "used_data/used_quotes.txt"
            if used_quotes_path.is_file():
                with open(used_quotes_path, mode="r") as fp:
                    quotes_to_ignore = [l.split(',')[0]
                                        for l in fp.read().splitlines()]

        if self.quote_source == 'QUOTE_API':
            results = []
            for r in quote(search=self.query, limit=self.limit):
                q = Quote(
                    author=r.get('author'),
                    quote=r.get('quote'),
                    source=r.get('book'),
                    source_type='book'
                )
                results.append(q)
            self.results = [q for q in results if q.id not in quotes_to_ignore]
        else:
            raise NotImplementedError
