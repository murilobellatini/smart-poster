
from quote import quote

from src.custom_logging import getLogger
from src.text import Quote
from src import ConfigLoader

logger = getLogger(__name__)


class QuoteExtractor(ConfigLoader):

    def __init__(self, query: str, quote_source: str = 'QUOTE_API', limit: int = 10):

        super().__init__()

        if self.ignore_config:
            self.quote_source = quote_source

        if self.quote_source == 'QUOTE_API':
            results = []
            for r in quote(search=query, limit=limit):
                q = Quote(
                    author=r.get('author'),
                    quote=r.get('quote'),
                    source=r.get('book'),
                    source_type='book'
                )
                results.append(q)
            self.results = results
        else:
            raise NotImplementedError
