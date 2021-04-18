from PIL import Image, ImageDraw, ImageFont, ImageColor
from src.paths import LOCAL_RAW_DATA_PATH


def draw_text(txt, font='Poppins-Bold.otf', fontsize=35, fontcolor_hex="black", export=False, format="PNG"):
    font = ImageFont.truetype(font, fontsize)
    fontcolor = ImageColor.getcolor(fontcolor_hex, "RGB")

    filename = txt.replace('\n', '-').replace(':', '').replace(';', '').replace(',', '').replace('.', '')

    im_dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(im_dummy)
    W, H = draw.textsize(txt, font)

    im = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(txt, font)

    draw.text(((W-w)/2, (H-h)/2), text=txt, fill=fontcolor, font=font)

    if export:
        im.save(LOCAL_RAW_DATA_PATH / f"{filename}.{format}", format)

    return im
