
from quote import quote

from src.text import Quote


class QuoteExtractor():

    def __init__(self, query: str, ext_source: str = 'QUOTE_API', limit: int = 10):

        if ext_source == 'QUOTE_API':
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
