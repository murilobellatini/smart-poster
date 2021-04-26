
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from gensim import corpora
from nltk import download
import gensim
import string
import spacy
import re

from src import ConfigLoader
from src.custom_logging import getLogger
from src.helpers import get_hashed_str, capitalize_first_letter

download('stopwords')
download('wordnet')
nlp = spacy.load('en_core_web_sm')


regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Quote(ConfigLoader):

    def __init__(self, quote: str, author: str, source: str,
                 source_type: str, lang: str = 'english'):

        super().__init__()

        self.logger = getLogger(self.__class__.__name__)

        if self.ignore_config:
            self.lang = lang

        q = re.sub(r'(\.|\,|;)', r'\1 ', quote).replace(
            '  ', ' ').strip()
        self.quote = '. '.join(capitalize_first_letter(i)
                               for i in q.split('. '))
        self.id = get_hashed_str(self.quote)
        self.author = author if author != '' else 'Unknown Author'
        self.source = source if source != '' else 'Unknown Source'
        self.source_type = source_type
        self.hashtags = self.generate_hashtags()
        self.word_count = len(self.quote.split(' '))
        self.main_txt, self.caption = self.break_text()

    def __repr__(self):
        return f"<Quote author:`{self.author}` source:`{self.source}` quote_prev:`{self.quote[:15]}...`>"

    def to_dict(self):
        self.logger.debug(f'Converting Quote to Text...')

        return {
            'quote': self.quote,
            'author': self.author,
            'source': self.source,
            'source_type': self.source_type,
            'lang': self.lang,
        }

    def filter_tags(self, from_: str = "main_txt", title: bool = False, tags: list = ['NOUN']):
        self.logger.debug(f'Filtering Quote\'s tags...')

        if from_ == "main_txt":
            txt = self.main_txt
        elif from_ == "quote":
            txt = self.quote
        else:
            raise NotImplementedError

        if title:
            txt = txt.title()

        output = []

        doc = nlp(txt)
        output = [token for token in doc if token.pos_ in tags]

        return output

    def generate_hashtags(self, num_topics: int = 10, passes: int = 3) -> list:
        self.logger.debug(f'Generating Quote\'s hashtags...')

        text = ' '.join(self.to_dict().values())

        stop = set(stopwords.words(self.lang))
        exclude = set(string.punctuation)
        lemma = WordNetLemmatizer()

        doc_complete = text.split('\n')

        def clean(doc):
            stop_free = " ".join(
                [i for i in doc.lower().split() if i not in stop])
            punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
            normalized = " ".join(lemma.lemmatize(word)
                                  for word in punc_free.split())
            return normalized

        doc_clean = [clean(doc).split() for doc in doc_complete]
        dictionary = corpora.Dictionary(doc_clean)
        doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
        Lda = gensim.models.ldamodel.LdaModel
        ldamodel = Lda(doc_term_matrix, num_topics=num_topics,
                       id2word=dictionary, passes=passes)
        topic = ldamodel.print_topics(num_topics=5, num_words=5)

        hashtags = []
        for t in topic:
            for h in t[1].split('+'):
                hashtags.append('#'+h[h.find('"')+1:h.rfind('"')])

        self.hashtags = list(set(hashtags))

        return self.hashtags

    def break_text(self, word_count: int = 16):
        self.logger.debug(f'Breaking Quote\'s text into main the rest...')

        quote_words = self.quote.strip().split(' ')
        main_txt = ' '.join(quote_words[:word_count])
        caption = ''

        if word_count < self.word_count:
            main_txt += ' ...'
            caption = '... ' + ' '.join(quote_words[word_count:])

        self.main_txt = main_txt.strip()
        self.caption = caption.strip()

        return self.main_txt, self.caption
