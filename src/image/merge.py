from PIL import Image
from src.image.color import get_contrast_color
from src.image.draw import draw_text, resize_img
from src.paths import LOCAL_GLOBAL_DATA, LOCAL_PROCESSED_DATA_PATH


def merge_text_to_image(img:Image, txt:str, overlay:str='OVERLAY_80%OP_BLACK_BOTTOM_LEFT', left_padding:float=60, txt_aspect_ratio:float=0.3):
    """
    Merges text `txt` to image `img` with possible overlays below:

    - 'OVERLAY_100%OP_BLACK_BOTTOM_LEFT'
    - 'OVERLAY_80%OP_BLACK_BOTTOM_LEFT'

    Output with squared aspect ratio.
    """
    canvas = Image.open(str(LOCAL_GLOBAL_DATA / 'SQUARED_CANVAS.png')).convert("RGBA")
    img_ = img.convert("RGBA")
    overlay = Image.open(str(LOCAL_GLOBAL_DATA / f'{overlay}.png'))
    txt_color = get_contrast_color(img_)
    txt_ = resize_img(draw_text(txt, fontsize=200, fontcolor_hex=txt_color, target_ar=txt_aspect_ratio), (0,1000))
    
    canvas.paste(img_, (int(canvas.size[0] - img_.size[0]),0), img_)
    canvas.paste(overlay, (0,0), overlay)
    canvas.paste(txt_, (left_padding,int((img_.size[1] - txt_.size[1])/2)), txt_)
    
    return canvas
