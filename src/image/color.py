import io
from PIL import Image
from colorthief import ColorThief
from colormap import rgb2hex as rgb2hex_
from colorsys import rgb_to_hsv, hsv_to_rgb, rgb_to_hls

def get_most_saturated_color(rgb_palette):
    hsl_palette = [rgb_to_hls(*c) for c in rgb_palette]
    i = hsl_palette.index(min(hsl_palette, key=lambda t: t[2]))
    return rgb_palette[i]


def saturate_color(rgb: tuple, sat: float = 1):
    hsv = rgb_to_hsv(*rgb)
    output_hsv = (hsv[0], sat, hsv[2])
    return hsv_to_rgb(*output_hsv)

def increase_brightness(rgb, pct:float=0.5) -> tuple:
    r, g, b = rgb
    r = min(255, r*(1+pct))
    g = min(255, g*(1+pct))
    b = min(255, b*(1+pct))
    return (r, g, b)

def get_dominant_color(img: Image, quality: int = 5):

    with io.BytesIO() as file_object:
        img.save(file_object, "PNG")
        cf = ColorThief(file_object)
        color = cf.get_color(quality=quality)
    
    return color


def get_color_palette(img: Image, quality: int = 5, color_count: int = 6):

    with io.BytesIO() as file_object:
        img.save(file_object, "PNG")
        cf = ColorThief(file_object)
        palette = cf.get_palette(color_count=color_count, quality=quality)

    return palette

def rgb2hex(rgb:tuple) -> tuple:
    return rgb2hex_(*(int(c) for c in rgb))

def get_contrast_color(image:Image, sat:float=1, brightness:float=.5) -> str:
    palette = get_color_palette(image.convert("RGBA"))
    most_sat_color = get_most_saturated_color(palette)
    txt_color = rgb2hex(increase_brightness(saturate_color(most_sat_color, sat=1), pct=brightness))
    return txt_color