
from src.image.color import ColorPicker
import cv2
import copy
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter, ImageEnhance

from src.custom_logging import getLogger
from src.paths import LOCAL_GLOBAL_DATA
from src.helpers import select_closest
from src.image import ImageWrapper

logger = getLogger(__name__)


class TextDrawer(ImageWrapper):

    def __init__(self, txt: str, font_family: str = 'Poppins', font_style: str = 'bold',
                 font_color: str = "black", font_size: int = 50, target_ar: float = None,
                 padding_pct: float = 0.25, blurred_halo: bool = True, size: tuple = None,
                 txt_brightness: float = None):

        self.txt = txt
        self.font_family = font_family
        self.font_style = font_style
        self.font_size = font_size

        if isinstance(font_color, tuple):
            cp = ColorPicker()
            self.font_color = cp.rgb2hex(font_color)
        else:
            self.font_color = font_color

        self.padding_pct = padding_pct
        self.target_ar = target_ar
        self.blurred_halo = blurred_halo

        if size:
            self.font_size = 200

        self.img = self._draw_text()

        if size:
            self.img = self.resize_img(xy=size)

        if txt_brightness:
            self.set_img_brightness(txt_brightness)

    def _draw_text(self) -> Image:
        logger.debug(f'Drawing text image...')

        txt = self.txt
        font = self._compose_font_path(self.font_family, self.font_style)

        imgfont = ImageFont.truetype(font, self.font_size)
        fontcolor = ImageColor.getcolor(self.font_color, "RGB")

        im_dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(im_dummy)
        W, H = draw.textsize(txt, imgfont)
        # larger padding_pct at height to avoid cropping blurred halo
        W, H = int(W*(1+self.padding_pct)), int(H*(1+self.padding_pct*1.25))

        im = Image.new("RGBA", (W, H))
        draw = ImageDraw.Draw(im)
        w, h = draw.textsize(txt, imgfont)
        draw.text(((W-w)/2, (H-h)/2), text=txt, fill=fontcolor, font=imgfont)

        if self.target_ar:
            imgs = []
            for w in range(10, 60, 5):
                wrapped_txt = textwrap.fill(
                    txt, width=w, break_long_words=False)

                img = TextDrawer(txt=wrapped_txt, font_family=self.font_family,
                                 font_style=self.font_style, font_size=self.font_size,
                                 font_color=self.font_color, padding_pct=self.padding_pct,
                                 blurred_halo=self.blurred_halo).img

                ar = img.size[0] / img.size[1]
                imgs.append({'width': w, 'aspect_ratio': ar, 'img': img})

            im = select_closest(imgs, self.target_ar, 'aspect_ratio')['img']

        self.img = im.convert('RGBA')

        if self.blurred_halo:
            self.img = self._add_blurred_halo(blur_radius=self.font_size/5)

        return self.img

    def _compose_font_path(self, font: str, fontstyle: str, format='ttf') -> str:
        logger.debug(f'Composing font path...')

        font_name = f'{font.capitalize()}-{fontstyle.capitalize()}.{format}'
        self.font_path = str(LOCAL_GLOBAL_DATA / f'fonts/{font_name}')
        return self.font_path

    def _add_blurred_halo(self, blur_radius: int = 10) -> Image:
        logger.debug(f'Adding blurred halo to text...')

        blurred_halo = self.img.filter(ImageFilter.GaussianBlur(blur_radius))
        blurred_halo_ = blurred_halo.convert('RGBA')
        enhancer = ImageEnhance.Brightness(blurred_halo_)
        gray_halo = enhancer.enhance(0)
        gray_halo.paste(self.img, (0, 0), self.img)
        self.gray_halo = gray_halo
        return self.gray_halo
