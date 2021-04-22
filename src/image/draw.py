import cv2
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter, ImageEnhance

from src.helpers import select_closest
from src.paths import LOCAL_RAW_DATA_PATH


def draw_text(txt: str, target_ar: float = None, font='Poppins-Bold.otf', fontsize=50, fontcolor_hex="black", padding: float = 0.2, blured_halo: bool = True):
    imgfont = ImageFont.truetype(font, fontsize)
    fontcolor = ImageColor.getcolor(fontcolor_hex, "RGB")

    im_dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(im_dummy)
    W, H = draw.textsize(txt, imgfont)
    W, H = int(W*(1+padding)), int(H*(1+padding))

    im = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(txt, imgfont)
    draw.text(((W-w)/2, (H-h)/2), text=txt, fill=fontcolor, font=imgfont)

    if target_ar:
        imgs = []
        for w in range(10, 60, 5):
            wrapped_txt = textwrap.fill(txt, width=w, break_long_words=False)
            img = draw_text(txt=wrapped_txt, target_ar=None, font=font, fontsize=fontsize,
                            fontcolor_hex=fontcolor_hex, padding=padding, blured_halo=blured_halo)
            ar = img.size[0] / img.size[1]
            imgs.append({'width': w, 'aspect_ratio': ar, 'img': img})

        im = select_closest(imgs, target_ar, 'aspect_ratio')['img']

    if blured_halo:
        im = add_blurred_halo(im, blur_radius=fontsize/5)

    setattr(im, 'txt', txt)

    return im.convert('RGBA')


def export_txt(txt_img: Image, format: str = "PNG"):
    filename = txt_img.txt.replace(
        '\n', '-').replace(':', '').replace(';', '').replace(',', '').replace('.', '')
    txt_img.save(LOCAL_RAW_DATA_PATH / f"{filename}.{format}", format)


def resize_img(img, xy: tuple):
    """
    Resizes image `img` according to tuple `xy`
    Keeps aspect ratio if one dimension is set to zero.
    """
    if min(xy) == 0:
        ar = img.size[0] / img.size[1]
        if xy[0] == 0:
            xy = (xy[1]*ar, xy[1])
        else:
            xy = (xy[0], xy[0]/ar)

    return img.resize((int(xy[0]), int(xy[1])))


def add_blurred_halo(im, blur_radius: int = 10):
    blurred_halo = im.filter(ImageFilter.GaussianBlur(blur_radius))
    blurred_halo_ = blurred_halo.convert('RGBA')
    enhancer = ImageEnhance.Brightness(blurred_halo_)
    gray_halo = enhancer.enhance(0)
    gray_halo.paste(im, (0, 0), im)
    return gray_halo


def draw_brighter_text(txt, xy, font, color, brightness_factor):

    txt_ = resize_img(draw_text(f'{txt}',
                                font=font, fontsize=200, fontcolor_hex=color), xy)
    txt_ = ImageEnhance.Brightness(
        txt_).enhance((1+brightness_factor))

    return txt_
