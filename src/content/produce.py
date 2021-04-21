from src.image.merge import compose_creative
import requests
from PIL import Image
from src.image.crop import crop
from src.image.merge import compose_creative
from src.text.manipulate import break_text
from src.image.extract import ApiImgExtractor
from src.paths import LOCAL_PROCESSED_DATA_PATH

from src.text.extract import generate_hashtags
from pathlib import Path


def produce_content():
    pass


def build_post(q: dict, img_url: str, profile_name: str, output_size=(1080, 1080), txt_aspect_ratio: str = 'NARROW', max_words: int = 16):

    img = crop(img_url, export=False, output_size=output_size)

    txt = q.get('quote')
    tb_txt = 'Unknown Author'

    if (q.get('author') != '') and (len(q.get('author').split(' ')) > 1):
        tb_txt = q['author']
    elif q.get('book') != '':
        tb_txt = "Book: " + q['book']

    txt = txt.replace('.', '. ').replace('  ', ' ')

    txt2draw, caption = break_text(txt=txt, word_count=max_words)

    hashtags = generate_hashtags(' '.join(q.values()))

    cta = ['\n']

    if q.get('book') and (q.get('book') != ''):
        cta.append('Book: "' + q['book'] + '"')
    if q.get('author') and (q.get('author') != ''):
        cta.append('Author: ' + q['author'])

    cta.extend([
        '\n💥 Pages for you to like!',
        f'👉 {profile_name}',
        10*'➖',
        '🤐 Comment 6x with 💪 and like our post! 🤫',
        10*'➖',
        '❤Like 💬Comment ✔Follow us',
        10*'➖',
        '#️⃣Hashtags:⠀',
    ])

    cta.append(' '.join(hashtags))

    cta.extend([
        10*'➖',
        '☆ We wish you a lot of wisdom!'
    ])

    caption += '\n'.join(cta)

    post = compose_creative(img, txt2draw, bottom_right_txt=tb_txt,
                            top_right_txt=profile_name,
                            txt_aspect_ratio=txt_aspect_ratio,
                            txt_brightness=3)

    return post, caption.strip()


def export_post(post: Image, filepath: Path, format_: str = 'PNG'):
    post.save(filepath, format_, quality=90)


def export_caption(caption: str, filepath: Path):
    with open(filepath, mode='w', encoding='utf8') as fp:
        fp.write(caption)
