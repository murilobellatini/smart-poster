from pathlib import Path
from PIL import Image
import numpy as np


from src.image.detect import ComputerVision
from src.image.color import ColorPicker
from src.image.text import TextDrawer
from src.image import ImageWrapper
from src.paths import LOCAL_GLOBAL_DATA


class Creative(ImageWrapper):

    def __init__(self, txt: str, bottom_right_txt: str = ' ', top_right_txt: str = ' ',
                 img: Image = None, img_path: Path = None, img_url: str = None,
                 img_np: np.array = None, padding: float = 60, txt_brightness: float = 1,
                 txt_aspect_ratio: str = 'NARROW', font_family: str = 'Poppins',
                 font_style: str = 'bold', font_color: str = 'AUTO', font_size: int = 50,
                 output_size: tuple = (1080, 1080)):

        self.txt = txt
        self.bottom_right_txt = bottom_right_txt
        self.top_right_txt = top_right_txt
        self.padding = padding
        self.txt_brightness = txt_brightness
        self.txt_aspect_ratio = txt_aspect_ratio
        self.font_family = font_family
        self.font_style = font_style
        self.font_size = font_size
        self.font_color = font_color
        self.output_size = output_size

        if img:
            self.load_img(img)
        elif img_path:
            self.load_path(img_path)
        elif img_url:
            self.load_url(img_url)
        elif img_np:
            self.load_numpy(img_np)
        else:
            raise AttributeError

        self.creative = self.compose_creative()

    def compose_creative(self) -> Image:
        """
        Merges text `txt` to image `img` with possible overlays below:
        Output with squared aspect ratio.
        """

        canvas_black, canvas, overlay = self.load_layers()
        txt_, top_right_txt_, bottom_right_txt_ = self.get_txt_layers()

        cp = ComputerVision()
        img_ = cp.load_img(self.img)
        img_ = cp.smart_crop(self.output_size)
        img_ = cp.flip_if_necessary()

        canvas = self.merge_layers(bg=canvas, fg=img_,
                                   align='TOP_LEFT')
        canvas = self.merge_layers(bg=canvas, fg=overlay,
                                   align='TOP_RIGHT')
        canvas = self.merge_layers(bg=canvas, fg=txt_,
                                   align='LEFT_CENTERED_PADDED')
        canvas = self.merge_layers(bg=canvas, fg=top_right_txt_,
                                   align='TOP_RIGHT_PADDED')
        canvas = self.merge_layers(bg=canvas, fg=bottom_right_txt_,
                                   align='BOTTOM_RIGHT_PADDED')
        canvas = self.merge_layers(bg=canvas_black, fg=canvas,
                                   align='TOP_LEFT')

        self.creative = canvas.convert('RGB')

        return self.creative

    def load_layers(self, overlay: str = 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT_SOFT') -> tuple:

        canvas_black = Image.open(
            str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS_BLACK.png')).convert("RGBA")

        canvas = Image.open(
            str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS.png')).convert("RGBA")

        if canvas.size == self.img.size:
            overlay_ = Image.open(str(LOCAL_GLOBAL_DATA / f'{overlay}.png'))
        else:
            overlay_ = Image.open(
                str(LOCAL_GLOBAL_DATA / 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT_SOFT.png'))

        self.canvas_black = canvas_black
        self.canvas = canvas
        self.overlay_ = overlay_

        return canvas_black, canvas, overlay_

    def get_txt_layers(self) -> tuple:

        ar, txt_w, txt_h = self.get_txt_stats()

        if self.font_color == 'AUTO':
            cp = ColorPicker()
            cp.load_img(self.img)
            txt_color = cp.get_contrast_color(brightness=self.txt_brightness)
        else:
            txt_color = self.font_color

        td = TextDrawer(txt=self.txt, font_family=self.font_family, font_color=txt_color,
                        font_style=self.font_style, font_size=200, target_ar=ar)
        td.draw_text()

        self.img_txt = td.resize_img((txt_w, txt_h))

        self.img_txt = td.set_img_brightness(self.txt_brightness)

        td = TextDrawer(txt=self.top_right_txt, font_family=self.font_family, font_color=txt_color,
                        font_style='Light', font_size=200, target_ar=ar)
        td.draw_text()

        self.img_txt_tr = td.resize_img((0, 0.05*self.img.size[1]))

        self.img_txt_tr = td.set_img_brightness(self.txt_brightness)

        td = TextDrawer(txt=self.bottom_right_txt, font_family=self.font_family, font_color=txt_color,
                        font_style='Italic', font_size=200, target_ar=ar)
        td.draw_text()

        self.img_txt_br = td.resize_img((0, 0.05*self.img.size[1]))

        self.img_txt_br = td.set_img_brightness(self.txt_brightness)

        return self.img_txt, self.img_txt_tr, self.img_txt_br

    def get_txt_stats(self) -> tuple:

        if self.txt_aspect_ratio == 'NARROW':
            txt_w, txt_h = (0, self.img.size[1]*.92)
            ar = 0.3
        elif self.txt_aspect_ratio == 'WIDE':
            txt_w, txt_h = (self.img.size[0]*.92, 0)
            ar = 3.3
        else:
            raise NotImplementedError

        self.ar, self.txt_w, self.txt_h = ar, txt_w, txt_h

        return ar, txt_w, txt_h

    def merge_layers(self, bg: Image, fg: Image, align: str, pos_: tuple = None):

        if align == 'TOP_LEFT':
            pos = (0, 0)

        elif align == 'TOP_RIGHT':
            pos = (int(bg.size[0] - fg.size[0]), 0)

        elif align == 'TOP_RIGHT_PADDED':
            pos = (int(bg.size[0]-self.padding/2-fg.size[0]),
                   int(self.padding/2))

        elif align == 'BOTTOM_RIGHT_PADDED':
            pos = (int(bg.size[0]-self.padding/2-fg.size[0]),
                   int(bg.size[1]-self.padding/2-fg.size[1]))

        elif align == 'LEFT_CENTERED_PADDED':
            pos = (self.padding,
                   int((bg.size[1] - fg.size[1])/2))

        elif align == 'CUSTOM':
            pos = pos_

        else:
            raise NotImplementedError

        bg.paste(fg, pos, fg)

        return bg
