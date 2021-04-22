
import cv2
import copy
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor, ImageFilter, ImageEnhance

from src.image import ImageWrapper
from src.helpers import select_closest
from src.paths import LOCAL_RAW_DATA_PATH


class TextDrawer(ImageWrapper):

    def __init__(self, txt: str, font_family='Poppins', font_style='bold', font_size=50, target_ar: float = None, font_color="black", padding: float = 0.5, blured_halo: bool = True):
        self.txt = txt
        self.font_family = font_family
        self.font_style = font_style
        self.font_size = font_size
        self.font_color = font_color
        self.padding = padding
        self.target_ar = target_ar
        self.blured_halo = True

    def compose_font_path(self, font: str, fontstyle: str, format='otf') -> str:
        self.font_path = f'{font.capitalize()}-{fontstyle.capitalize()}.{format}'
        return self.font_path

    def draw_text(self) -> Image:

        txt = self.txt
        font = self.compose_font_path(self.font_family, self.font_style)

        imgfont = ImageFont.truetype(font, self.font_size)
        fontcolor = ImageColor.getcolor(self.font_color, "RGB")

        im_dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(im_dummy)
        W, H = draw.textsize(txt, imgfont)
        W, H = int(W*(1+self.padding)), int(H*(1+self.padding))

        im = Image.new("RGBA", (W, H))
        draw = ImageDraw.Draw(im)
        w, h = draw.textsize(txt, imgfont)
        draw.text(((W-w)/2, (H-h)/2), text=txt, fill=fontcolor, font=imgfont)

        if self.target_ar:
            imgs = []
            for w in range(10, 60, 5):
                wrapped_txt = textwrap.fill(
                    txt, width=w, break_long_words=False)

                td = TextDrawer(txt=wrapped_txt, font_family=self.font_family, font_style=self.font_style, font_size=self.font_size,
                                font_color=self.font_color, padding=self.padding, blured_halo=self.blured_halo)
                img = td.draw_text()

                ar = img.size[0] / img.size[1]
                imgs.append({'width': w, 'aspect_ratio': ar, 'img': img})

            im = select_closest(imgs, self.target_ar, 'aspect_ratio')['img']

        self.img = im.convert('RGBA')

        if self.blured_halo:
            self.img_halo = self.add_blurred_halo(blur_radius=self.font_size/5)
            return self.img_halo

        return self.img

    def add_blurred_halo(self, blur_radius: int = 10) -> Image:
        blurred_halo = self.img.filter(ImageFilter.GaussianBlur(blur_radius))
        blurred_halo_ = blurred_halo.convert('RGBA')
        enhancer = ImageEnhance.Brightness(blurred_halo_)
        gray_halo = enhancer.enhance(0)
        gray_halo.paste(self.img, (0, 0), self.img)
        self.gray_halo = gray_halo
        return self.gray_halo
