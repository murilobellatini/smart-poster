import io
from PIL import Image, ImageEnhance
from src.image.color import get_contrast_color
from src.image.draw import draw_text, resize_img
from src.paths import LOCAL_GLOBAL_DATA, LOCAL_PROCESSED_DATA_PATH


def merge_text_to_image(img: Image, txt: str, profile_url: str = None, overlay: str = 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT', padding: float = 60, txt_aspect_ratio: float = 0.3, txt_brightness: float = 1, max_words: int = 16):
    """
    Merges text `txt` to image `img` with possible overlays below:

    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT'

    Output with squared aspect ratio.
    """

    txt2draw = ' '.join(txt.split(' ')[:max_words])
    caption = ''

    if max_words < len(txt.split(' ')):
        txt2draw += ' ...'
        caption = '... ' + ' '.join(txt.split(' ')[max_words:])

    canvas = Image.open(
        str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS.png')).convert("RGBA")
    img_ = img.convert("RGBA")
    if canvas.size != img_.size:
        overlay = Image.open(
            str(LOCAL_GLOBAL_DATA / 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT.png'))
    else:
        overlay = Image.open(str(LOCAL_GLOBAL_DATA / f'{overlay}.png'))

    txt_color = get_contrast_color(img_, brightness=txt_brightness)
    txt_ = resize_img(draw_text(txt2draw, fontsize=200,
                      fontcolor_hex=txt_color, target_ar=txt_aspect_ratio), (0, 1000))
    txt_ = ImageEnhance.Brightness(txt_).enhance((1+txt_brightness))

    profile_url_ = resize_img(draw_text(f'{profile_url}',
                                        font='Poppins-Light.otf', fontsize=200, fontcolor_hex=txt_color), (400, 0))
    profile_url_ = ImageEnhance.Brightness(
        profile_url_).enhance((1+txt_brightness))

    canvas.paste(img_, (int(canvas.size[0] - img_.size[0]), 0), img_)
    canvas.paste(overlay, (0, 0), overlay)
    canvas.paste(txt_, (padding,
                        int((img_.size[1] - txt_.size[1])/2)), txt_)

    if profile_url:
        canvas.paste(profile_url_, (int(img_.size[0]-padding/2-profile_url_.size[0]),
                     int(padding/2)), profile_url_)

    canvas_black = Image.open(
        str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVA_BLACK.png')).convert("RGBA")

    with io.BytesIO() as f:
        canvas.save(f, "PNG")
        canva_reloaded = Image.open(f).convert('RGBA')
        canvas_black.paste(canva_reloaded, (0, 0), canva_reloaded)
        return canvas_black.convert("RGBA")
