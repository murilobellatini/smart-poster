import requests
import numpy as np
from io import BytesIO
from src import ConfigLoader
from PIL import Image, ImageEnhance

RESET = '\033[0m'


def get_color_escape(r, g, b, background=False):
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)


class ImageWrapper(ConfigLoader):

    def __init__(self):
        super().__init__()

    def load_img(self, img: Image) -> None:
        self.img = img
        self.img_np = self.img2np(self.img)

    def load_numpy(self, img_np: np.array) -> None:
        self.img_np = img_np
        self.img = self.img2np(self.img_np)

    def load_path(self, img_path: str) -> None:
        self.img = Image.open(img_path)
        self.img_np = self.img2np(self.img)

    def load_url(self, img_url: str) -> None:
        self.img = Image.open(BytesIO(requests.get(
            img_url, stream=True, headers={"User-Agent": "XY"}).content))
        self.img_np = self.img2np(self.img)

    def set_img_brightness(self, bightness_factor: float) -> Image:
        self.img = ImageEnhance.Brightness(
            self.img).enhance((1+bightness_factor))
        return self.img

    def img2np(self, img: Image) -> np.array:
        return np.array(img)

    def np2img(self, img_np: np.array) -> Image:
        return Image.fromarray(img_np)

    def resize_img(self, xy: tuple) -> Image:
        """
        Resizes image `self.img` according to dimensions `xy`
        Keeps aspect ratio if one dimension is set to zero.
        """
        if min(xy) == 0:
            ar = self.img.size[0] / self.img.size[1]
            if xy[0] == 0:
                xy = (xy[1]*ar, xy[1])
            else:
                xy = (xy[0], xy[0]/ar)

        self.img = self.img.resize((int(xy[0]), int(xy[1])))

        return self.img
