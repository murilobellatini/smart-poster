import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageColor
from src.paths import LOCAL_RAW_DATA_PATH, LOCAL_MODELS_PATH


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

def draw_boxes(img:np.ndarray, classIds:np.ndarray, classNames:list, confs:np.ndarray, bbox:np.ndarray):
    
    img_boxed = img.copy()
    
    output_rectangles = np.zeros(img_boxed.shape, dtype="uint8")
    
    for classId, confidence,box in zip(classIds.flatten(), confs.flatten(), bbox):
        cv2.rectangle(img_boxed,box,color=(0,255,0),thickness=2)
        rectangle = cv2.rectangle(output_rectangles,box,color=(255,255,255),thickness=cv2.FILLED)
        output_rectangles = cv2.bitwise_or(output_rectangles, rectangle)
        cv2.putText(img_boxed,classNames[classId-1].upper(),(box[0]+10,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
        cv2.putText(img_boxed,str(round(confidence*100,2)),(box[0]+200,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
            
    return img_boxed, output_rectangles
