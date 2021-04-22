
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from gensim import corpora
from nltk import download
import gensim
import string
import re

download('stopwords')
download('wordnet')

regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class Quote():

    def __init__(self, quote: str, author: str, source: str, source_type: str, lang: str = 'english'):
        self.quote = quote
        self.author = author
        self.source = source
        self.source_type = source_type
        self.lang = lang
        self.hashtags = self.generate_hashtags()
        self.word_count = len(self.quote.split(' '))
        self.main_txt, self.caption = self.break_text()

    def __repr__(self):
        return f"<Quote author:`{self.author}` source:`{self.source}` quote_prev:`{self.quote[:15]}...`>"

    def to_dict(self):
        return {
            'quote': self.quote,
            'author': self.author,
            'source': self.source,
            'source_type': self.source_type,
            'lang': self.lang,
        }

    def generate_hashtags(self, num_topics: int = 10, passes: int = 3) -> list:

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
        quote_words = self.quote.strip().split(' ')
        main_txt = ' '.join(quote_words[:word_count])
        caption = ''

        if word_count < self.word_count:
            main_txt += ' ...'
            caption = '... ' + ' '.join(quote_words[word_count:])

        self.main_txt = main_txt.strip()
        self.caption = caption.strip()

        return self.main_txt, self.caption
