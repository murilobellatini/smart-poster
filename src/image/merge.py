import numpy as np
from PIL import Image, ImageEnhance
from src.image.detect import flip_if_necessary
from src.image.draw import draw_text, resize_img
from src.image.color import get_contrast_color, set_img_brightness
from src.paths import LOCAL_GLOBAL_DATA


def merge_text_to_image(img: Image, txt: str, bottom_right_txt: str = ' ', top_right_txt: str = ' ', padding: float = 60, txt_brightness: float = 1, txt_aspect_ratio: str = 'NARROW'):
    """
    Merges text `txt` to image `img` with possible overlays below:

    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT'

    Output with squared aspect ratio.
    """

    canvas_black, canvas, overlay = load_layers(img)

    txt_, top_right_txt_, bottom_right_txt_ = get_txt_layers(
        img_=img, texts=(txt, top_right_txt, bottom_right_txt),
        txt_brightness=txt_brightness, txt_aspect_ratio=txt_aspect_ratio)

    img_ = flip_if_necessary(img.convert("RGB"))

    canvas = merge_layers(bg=canvas, fg=img_,
                          align='TOP_LEFT')
    canvas = merge_layers(bg=canvas, fg=overlay,
                          align='TOP_RIGHT')
    canvas = merge_layers(bg=canvas, fg=txt_,
                          align='LEFT_CENTERED_PADDED', padding=padding)
    canvas = merge_layers(bg=canvas, fg=top_right_txt_,
                          align='TOP_RIGHT_PADDED', padding=padding)
    canvas = merge_layers(bg=canvas, fg=bottom_right_txt_,
                          align='BOTTOM_RIGHT_PADDED', padding=padding)
    canvas = merge_layers(bg=canvas_black, fg=canvas,
                          align='TOP_LEFT', padding=padding)

    return canvas.convert('RGB')


def np2img(numpy_image: np.array):
    return Image.fromarray(numpy_image.astype('uint8'), 'RGBA')


def load_layers(img: Image, overlay: str = 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT'):

    canvas_black = Image.open(
        str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS_BLACK.png')).convert("RGBA")

    canvas = Image.open(
        str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS.png')).convert("RGBA")

    if canvas.size == img.size:
        overlay_ = Image.open(str(LOCAL_GLOBAL_DATA / f'{overlay}.png'))
    else:
        overlay_ = Image.open(
            str(LOCAL_GLOBAL_DATA / 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT.png'))

    return canvas_black, canvas, overlay_


def get_txt_layers(img_: Image, texts: tuple, txt_brightness: float, txt_aspect_ratio: str = 'NARROW') -> tuple:

    txt2draw, top_right_txt, bottom_right_txt = texts

    ar, txt_w, txt_h = get_txt_stats(img_, txt_aspect_ratio)

    txt_color = get_contrast_color(img_, brightness=txt_brightness)

    txt_ = resize_img(draw_text(txt2draw, fontsize=200,
                      fontcolor_hex=txt_color, target_ar=ar), (txt_w, txt_h))
    txt_ = set_img_brightness(txt_, txt_brightness)

    top_right_txt_ = resize_img(draw_text(f'{top_right_txt}',
                                          font='Poppins-Light.otf', fontsize=200, fontcolor_hex=txt_color), (0, 0.05*img_.size[1]))
    top_right_txt_ = set_img_brightness(top_right_txt_, txt_brightness)

    bottom_right_txt_ = resize_img(draw_text(f'{bottom_right_txt}',
                                             font='Poppins-Italic.otf', fontsize=200, fontcolor_hex=txt_color), (0, 0.05*img_.size[1]))
    bottom_right_txt_ = set_img_brightness(bottom_right_txt_, txt_brightness)

    return txt_, top_right_txt_, bottom_right_txt_


def get_txt_stats(img_: Image, txt_aspect_ratio: str):

    if txt_aspect_ratio == 'NARROW':
        txt_w, txt_h = (0, img_.size[1]*.92)
        ar = 0.3
    elif txt_aspect_ratio == 'WIDE':
        txt_w, txt_h = (img_.size[0]*.92, 0)
        ar = 3.3
    else:
        raise NotImplementedError

    return ar, txt_w, txt_h


def merge_layers(bg: Image, fg: Image, align: str, pos_: tuple = None, padding: int = 0):

    if align == 'TOP_LEFT':
        pos = (0, 0)

    elif align == 'TOP_RIGHT':
        pos = (int(bg.size[0] - fg.size[0]), 0)

    elif align == 'TOP_RIGHT_PADDED':
        pos = (int(bg.size[0]-padding/2-fg.size[0]),
               int(padding/2))

    elif align == 'BOTTOM_RIGHT_PADDED':
        pos = (int(bg.size[0]-padding/2-fg.size[0]),
               int(bg.size[1]-padding/2-fg.size[1]))

    elif align == 'LEFT_CENTERED_PADDED':
        pos = (padding,
               int((bg.size[1] - fg.size[1])/2))

    elif align == 'CUSTOM':
        pos = pos_

    else:
        raise NotImplementedError

    bg.paste(fg, pos, fg)

    return bg
