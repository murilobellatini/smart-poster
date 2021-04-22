from src.text import Quote
from src.image.merge import Creative


from src.image.extract import ApiImgExtractor

from src.paths import LOCAL_PROCESSED_DATA_PATH

from pathlib import Path


class Post():

    def __init__(self, quote: Quote, img_url: str, profile_name: str,
                 output_size: tuple = (1080, 1080), txt_aspect_ratio: str = 'NARROW',
                 font_family: str = 'Poppins', font_style: str = 'Bold',
                 font_color: str = 'AUTO') -> None:
        self.quote = quote
        self.img_url = img_url
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
            txt=self.quote.quote,
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
            f'{self.quote.source_type.title()}: {self.quote.source.title()}')
        cta.append(f'Author: {self.quote.author.title()}')

        cta.extend([
            '\n💥 Pages for you to like!',
            f'👉 {self.profile_name}',
            10*'➖',
            '🤐 Comment 6x with 💪 and like our post! 🤫',
            10*'➖',
            '❤Like 💬Comment ✔Follow us',
            10*'➖',
            '#️⃣Hashtags:⠀',
        ])

        cta.append(' '.join(self.hashtags))

        cta.extend([
            10*'➖',
            '☆ We wish you a lot of wisdom!'
        ])

        self.caption += '\n'.join(cta)

        self.caption = self.caption.strip()

        return self.creative, self.caption

    def export_post(self, filepath: Path, format_: str = 'PNG'):
        self.creative.save(filepath, format_, quality=90)

    def export_caption(self, filepath: Path):
        with open(filepath, mode='w', encoding='utf8') as fp:
            fp.write(self.caption)


class ContentProducer():
    pass


def produce_content(themes: list, posts_per_theme: int, profile_name: str, txt_aspect_ratio: str = "NARROW", format_: str = "PNG", max_words: int = 16, output_size: tuple = (1080, 1080), api_: str = 'unsplash'):
    content = []

    for t in themes:
        api = ApiImgExtractor(api_)
        quotes = quote(t, limit=posts_per_theme)
        api.query(_search_params={
            'q': t,
            'imgType': 'photos'
        })

        if not quotes:
            continue

        for i, (q, img_url) in enumerate(zip(quotes, api.img_urls)):

            filepath = LOCAL_PROCESSED_DATA_PATH / f"{t}_{i}.{format_}"
            filepath_txt = LOCAL_PROCESSED_DATA_PATH / f"{t}_{i}.txt"

            if not q or not img_url:
                break

            post, caption = build_post(q=q, img_url=img_url, profile_name=profile_name,
                                       txt_aspect_ratio=txt_aspect_ratio, output_size=output_size, max_words=max_words)
            export_post(post, filepath)
            export_caption(caption, filepath_txt)

            content.append({
                'id': filepath.stem,
                'theme': t,
                'filepath': filepath,
                'filepath_txt': filepath_txt
            })

    return content
