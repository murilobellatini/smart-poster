import io
from os import getlogin
from colorthief import ColorThief
from PIL import Image, ImageEnhance
from colormap import rgb2hex as rgb2hex_
from colorsys import rgb_to_hsv, hsv_to_rgb, rgb_to_hls

from requests.api import get

from src.custom_logging import getLogger
from src.image import ImageWrapper

logger = getLogger(__name__)


class ColorPicker(ImageWrapper):

    def __init__(self) -> None:
        super().__init__()

    def scan_image(self):
        self.get_contrast_color()
        self.get_dominant_color(self.img)

    def get_most_saturated_color(self, rgb_palette: list) -> tuple:
        logger.debug('Getting most saturated color...')
        hsl_palette = [rgb_to_hls(*c) for c in rgb_palette]
        i = hsl_palette.index(min(hsl_palette, key=lambda t: t[2]))
        most_sat_color = rgb_palette[i]
        return most_sat_color

    def saturate_color(self, rgb: tuple, sat: float = 1) -> tuple:
        logger.debug(
            f'Setting saturating represent color `{rgb}` to `{sat:.0%}`...')
        hsv = rgb_to_hsv(*rgb)
        output_hsv = (hsv[0], sat, hsv[2])
        return hsv_to_rgb(*output_hsv)

    def increase_brightness(self, rgb, pct: float = 0.5) -> tuple:
        logger.debug(f'Increasing color brightness `{rgb}` by `{pct:.0%}`...')
        r, g, b = rgb
        r = min(255, r*(1+pct))
        g = min(255, g*(1+pct))
        b = min(255, b*(1+pct))
        return (r, g, b)

    def get_dominant_color(self, img: Image, quality: int = 5) -> tuple:
        logger.debug(f'Getting dominant color from image')

        with io.BytesIO() as file_object:
            img.save(file_object, "PNG")
            cf = ColorThief(file_object)
            self.dominant_color = cf.get_color(quality=quality)

        return self.dominant_color

    def get_color_palette(self, img: Image, quality: int = 10, color_count: int = 6) -> list:
        logger.debug(f'Getting color palette from image')
        with io.BytesIO() as file_object:
            img.save(file_object, "PNG")
            cf = ColorThief(file_object)
            self.palette = cf.get_palette(
                color_count=color_count, quality=quality)

        return self.palette

    def rgb2hex(self, rgb: tuple) -> str:
        return rgb2hex_(*(int(c) for c in rgb))

    def get_contrast_color(self, sat: float = 1, brightness: float = .5) -> tuple:
        logger.debug(f'Getting color with most contrast')
        palette = self.get_color_palette(self.img.convert("RGBA"))
        most_sat_color = self.get_most_saturated_color(palette)
        contrast_color = self.increase_brightness(
            self.saturate_color(most_sat_color, sat=sat), pct=brightness)
        self.contrast_color = contrast_color
        return self.contrast_color
