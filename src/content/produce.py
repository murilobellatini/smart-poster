import random
import wikipedia
from pathlib import Path

from src.text import Quote
from src import ConfigLoader
from src.image.merge import Creative
from src.custom_logging import getLogger
from src.text.extract import QuoteExtractor
from src.image.extract import ImgExtractorFactory
from src.paths import LOCAL_PROCESSED_DATA_PATH


class Post(ConfigLoader):

    def __init__(self, quote: Quote, img_url: str, img_meta: dict = None, profile_name: str = ' ',
                 output_size: tuple = (1080, 1080), txt_aspect_ratio: str = 'NARROW',
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO') -> None:

        super().__init__()

        self.logger = getLogger(self.__class__.__name__)

        self.logger.debug('Constructing Post...')

        self.quote = quote
        self.img_url = img_url

        if self.ignore_config:
            self.logger.debug('Loading data from `config.yaml` file')
            self.profile_name = profile_name
            self.output_size = output_size
            self.txt_aspect_ratio = txt_aspect_ratio
            self.font_family = font_family
            self.font_style = font_style
            self.font_color = font_color

        self.img_meta = img_meta
        self.caption = quote.caption
        self.hashtags = quote.hashtags
        self.txt2draw = quote.main_txt
        self.creative, self.caption = self.build_post()

    def build_post(self) -> tuple:

        self.logger.debug('Building Post...')

        c = Creative(
            txt=self.quote.main_txt,
            bottom_right_txt=self.quote.author,
            top_right_txt=self.profile_name,
            img_url=self.img_url,
            txt_aspect_ratio=self.txt_aspect_ratio,
            font_family=self.font_family,
            font_style=self.font_style,
            font_color=self.font_color,
            output_size=self.output_size
        )

        self.creative = c.creative

        cta = ['\n💬 About the Quote...']

        cta.append(
            f'📕 {self.quote.source_type.title()}: {self.quote.source.title()}')
        cta.append(f'✍️ Author: {self.quote.author.title()}')

        if self.img_meta:
            cta.append(10*'➖')
            cta.append(
                f'📷 About the Photographer...')
            if self.img_meta.get('author_name'):
                cta.append(
                    f"👤 Name: {self.img_meta.get('author_name').title()}")
            if self.img_meta.get('instagram_username'):
                cta.append(
                    f"🖼️ Instagram: @{self.img_meta.get('instagram_username')}")
            elif self.img_meta.get('username'):
                cta.append(f"🖼️ Unsplash: @{self.img_meta.get('username')}")
            if self.img_meta.get('portfolio_url'):
                cta.append(
                    f"🔗 Portfolio: {self.img_meta.get('portfolio_url')}")

        cta.extend([
            10*'➖',
            '💥 Pages for you to like!',
            f'👉 {self.profile_name}',
            10*'➖',
            '🤐 Comment 6x with 💪 and like our post! 🤫',
            10*'➖',
            '❤️Like 💬Comment 👣Follow us',
            10*'➖',
            '#️⃣Hashtags⠀',
        ])

        cta.append(' '.join(self.hashtags))

        w_urls = []
        for query in (self.quote.author, self.quote.source):
            w_url = self.get_wiki_url(query)
            if w_url:
                w_urls.append(w_url)

        if w_urls:
            cta.extend([
                10*'➖',
                '📙 Learn more on Wikipedia'
            ] + w_urls)

        cta.extend([
            10*'➖',
            '⭐ We wish you a lot of wisdom!'
        ])

        self.caption += '\n'.join(cta)

        self.caption = self.caption

        with open(LOCAL_PROCESSED_DATA_PATH / "used_data/used_quotes.txt", "a") as fp:
            fp.write(f'{self.quote.id},"{self.quote.main_txt}"\n')

        with open(LOCAL_PROCESSED_DATA_PATH / "used_data/used_img_urls.txt", "a") as fp:
            fp.write(self.img_url + '\n')

        self.logger.debug('Post built successfully...')

        return self.creative, self.caption

    def get_wiki_url(self, query: str) -> str:

        self.logger.debug(f'Getting Wiki URL for query `{query}`...')

        if not "Unknown" in query:
            results = wikipedia.search(query)
            for r in results:
                try:
                    p = wikipedia.page(r)
                    break
                except Exception as e:
                    self.logger.warning(
                        f'Exception thrown for `{r}`. Skipping result...\n`{e}`')
            return p.url

    def export_post(self, filepath: Path, img_format: str = 'PNG') -> None:
        self.logger.debug(f'Exporting post to {filepath}...')
        self.creative.save(filepath, img_format, quality=90)

    def export_caption(self, filepath: Path) -> None:
        self.logger.debug(f'Exporting caption to {filepath}...')
        with open(filepath, mode='w', encoding='utf8') as fp:
            fp.write(self.caption)


class ContentProducer(ConfigLoader):

    def __init__(self, themes: list, posts_per_theme: int, img_search: str = 'THEME_BASED',
                 profile_name: str = ' ', txt_aspect_ratio: str = "NARROW",
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO', img_format: str = "PNG", txt_word_count: int = 16,
                 output_size: tuple = (1080, 1080), img_api: str = 'unsplash') -> None:

        super().__init__()

        self.logger = getLogger(self.__class__.__name__)

        self.themes = themes
        self.posts_per_theme = posts_per_theme

        if self.ignore_config:

            self.profile_name = profile_name
            self.txt_aspect_ratio = txt_aspect_ratio
            self.img_format = img_format
            self.txt_word_count = txt_word_count
            self.output_size = output_size
            self.img_api = img_api
            self.font_family = font_family
            self.font_style = font_style
            self.font_color = font_color
            self.img_search = img_search

    def produce_content(self):
        content = []
        img_urls_to_ignore = []

        for t in self.themes:

            ie = ImgExtractorFactory().create_extractor(api=self.img_api)
            qe = QuoteExtractor(
                query=t, quote_source='QUOTE_API', limit=self.posts_per_theme)

            if self.img_search == "THEME_BASED":
                ie.query(_search_params={
                    'q': t,
                    'imgType': 'photos',
                    'num': self.posts_per_theme,
                })

            if not qe.results:
                continue

            for i, q in enumerate(qe.results):

                if self.img_search == "THEME_BASED":
                    img_url = list(ie.img_urls)[i]
                elif self.img_search == "QUOTE_BASED":

                    tokens = [str(t) for t in set(
                              q.filter_tags(tags="NOUN") +
                              q.filter_tags(tags="NOUN", title=True) +
                              q.filter_tags(tags="PROPN") +
                              q.filter_tags(tags="VERB") +
                              [t])]

                    ie = ImgExtractorFactory().create_extractor(api=self.img_api)
                    while not ie.img_urls:
                        chosen_t = random.choice(tokens)
                        ie.query(_search_params={
                            'q': chosen_t,
                            'imgType': 'photos',
                            'num': self.posts_per_theme,
                        })
                        tokens.remove(chosen_t)
                        if not tokens:
                            self.logger.warning(
                                "No image available for any the text options... Skipping creative.")
                            continue
                    img_url = list(ie.img_urls)[0]
                else:
                    raise NotImplementedError

                filepath_img = LOCAL_PROCESSED_DATA_PATH / \
                    f"{t}_{i}.{self.img_format}"
                filepath_txt = LOCAL_PROCESSED_DATA_PATH / f"{t}_{i}.txt"

                if not q or not img_url:
                    break

                p = Post(quote=q, img_url=img_url,
                         img_meta=ie.metadata.get(img_url),
                         profile_name=self.profile_name,
                         output_size=self.output_size,
                         txt_aspect_ratio=self.txt_aspect_ratio,
                         font_family=self.font_family,
                         font_style=self.font_style,
                         font_color=self.font_color,
                         )

                p.export_post(filepath_img)
                p.export_caption(filepath_txt)

                content.append({
                    'id': filepath_img.stem,
                    'theme': t,
                    'filepath': filepath_img,
                    'filepath_txt': filepath_txt
                })

        self.logger.info(f'Content successfully produced...')

        return content
