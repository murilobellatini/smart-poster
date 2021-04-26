import random

from src.text import Quote
from src import ConfigLoader
from src.image.merge import Creative
from src.text.extract import QuoteExtractor
from src.image.extract import ApiImgExtractor

from src.paths import LOCAL_PROCESSED_DATA_PATH

from pathlib import Path


class Post(ConfigLoader):

    def __init__(self, quote: Quote, img_url: str, profile_name: str = ' ',
                 output_size: tuple = (1080, 1080), txt_aspect_ratio: str = 'NARROW',
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO') -> None:

        super().__init__()

        self.quote = quote
        self.img_url = img_url

        if self.ignore_config:
            self.profile_name = profile_name
            self.output_size = output_size
            self.txt_aspect_ratio = txt_aspect_ratio
            self.font_family = font_family
            self.font_style = font_style
            self.font_color = font_color

        self.caption = quote.caption
        self.hashtags = quote.hashtags
        self.txt2draw = quote.main_txt
        self.creative, self.caption = self.build_post()

    def build_post(self) -> tuple:

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

        cta = ['\n']

        cta.append(
            f'📕 {self.quote.source_type.title()}: {self.quote.source.title()}')
        cta.append(f'✍️ Author: {self.quote.author.title()}')

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

        cta.extend([
            10*'➖',
            '⭐ We wish you a lot of wisdom!'
        ])

        self.caption += '\n'.join(cta)

        self.caption = self.caption.strip()

        with open(LOCAL_PROCESSED_DATA_PATH / "USED_URLS/used_img_urls.txt", "a") as fp:
            fp.write(self.img_url + '\n')

        return self.creative, self.caption

    def export_post(self, filepath: Path, img_format: str = 'PNG') -> None:
        self.creative.save(filepath, img_format, quality=90)

    def export_caption(self, filepath: Path) -> None:
        with open(filepath, mode='w', encoding='utf8') as fp:
            fp.write(self.caption)


class ContentProducer(ConfigLoader):

    def __init__(self, themes: list, posts_per_theme: int, img_search: str = 'THEME_BASED',
                 profile_name: str = ' ', txt_aspect_ratio: str = "NARROW",
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO', img_format: str = "PNG", txt_word_count: int = 16,
                 output_size: tuple = (1080, 1080), img_api: str = 'unsplash') -> None:

        super().__init__()

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

            ie = ApiImgExtractor(self.img_api)
            qe = QuoteExtractor(
                query=t, quote_source='QUOTE_API', limit=self.posts_per_theme)

            if self.img_search == "THEME_BASED":
                ie.query(_search_params={
                    'q': t,
                    'imgType': 'photos',
                    'return_count': self.posts_per_theme,
                })

            if not qe.results:
                continue

            for i, q in enumerate(qe.results):

                if self.img_search == "THEME_BASED":
                    img_url = list(ie.img_urls)[i]
                elif self.img_search == "QUOTE_BASED":
                    tokens = q.filter_tags(tags="NOUN")
                    if not tokens:
                        tokens = q.filter_tags(tags="NOUN", title=True)
                    if not tokens:
                        tokens = [t]

                    ie = ApiImgExtractor(self.img_api)
                    ie.query(_search_params={
                        'q': random.choice(tokens),
                        'imgType': 'photos',
                        'return_count': self.posts_per_theme,
                    })
                    img_url = list(ie.img_urls)[0]
                else:
                    raise NotImplementedError

                filepath_img = LOCAL_PROCESSED_DATA_PATH / \
                    f"{t}_{i}.{self.img_format}"
                filepath_txt = LOCAL_PROCESSED_DATA_PATH / f"{t}_{i}.txt"

                if not q or not img_url:
                    break

                p = Post(quote=q, img_url=img_url,
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

        return content
