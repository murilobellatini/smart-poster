import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor

from src.helpers import select_closest
from src.paths import LOCAL_RAW_DATA_PATH


def draw_text(txt: str, target_ar: float = None, font='Poppins-Bold.otf', fontsize=50, fontcolor_hex="black"):
    imgfont = ImageFont.truetype(font, fontsize)
    fontcolor = ImageColor.getcolor(fontcolor_hex, "RGB")

    im_dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(im_dummy)
    W, H = draw.textsize(txt, imgfont)

    im = Image.new("RGBA", (W, H))
    draw = ImageDraw.Draw(im)
    w, h = draw.textsize(txt, imgfont)
    draw.text(((W-w)/2, (H-h)/2), text=txt, fill=fontcolor, font=imgfont)

    if target_ar:
        imgs = []
        for cw in range(1, 10):
            words = [
                w if (i+1) % cw != 0 else f"{w}\n" for i, w in enumerate(txt.split(' '))]
            txt2 = ' '.join(words)
            img = draw_text(txt=txt2, target_ar=None, font=font, fontsize=fontsize,
                            fontcolor_hex=fontcolor_hex)
            ar = img.size[0] / img.size[1]
            imgs.append({'cw': cw, 'aspect_ratio': ar, 'img': img})

        im = select_closest(imgs, target_ar, 'aspect_ratio')['img']

    setattr(im, 'txt', txt)

    return im


def export_txt(txt_img: Image, format: str = "PNG"):
    filename = txt_img.txt.replace(
        '\n', '-').replace(':', '').replace(';', '').replace(',', '').replace('.', '')
    im.save(LOCAL_RAW_DATA_PATH / f"{filename}.{format}", format)


def draw_boxes(img: np.ndarray, classIds: np.ndarray, classNames: list, confs: np.ndarray, bbox: np.ndarray):

    img_boxed = img.copy()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    output_rectangles = np.zeros(img_boxed.shape, dtype="uint8")

    for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
        cv2.rectangle(img_boxed, box, color=(0, 255, 0), thickness=2)
        cv2.rectangle(gray, box, color=(0, 0, 0), thickness=cv2.FILLED)
        rectangle = cv2.rectangle(output_rectangles, box, color=(
            255, 255, 255), thickness=cv2.FILLED)
        output_rectangles = cv2.bitwise_or(output_rectangles, rectangle)
        cv2.putText(img_boxed, classNames[classId-1].upper(), (box[0]+10,
                    box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(img_boxed, str(round(confidence*100, 2)),
                    (box[0]+200, box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    return img_boxed, gray
