from smartcrop import SmartCrop
from PIL import Image
import requests
import hashlib
import time


from src.paths import LOCAL_PROCESSED_DATA_PATH


def crop(url:str, export:bool = False, output_size:tuple=(1080,1080), format:str="JPEG", filename:str=None):
    ratio = output_size[0]/output_size[1]
    image = Image.open(requests.get(url, stream=True).raw)
    cropper = SmartCrop()
    result = cropper.crop(image, 100*ratio, 100)
    box = (
            result['top_crop']['x'],
            result['top_crop']['y'],
            result['top_crop']['width'] + result['top_crop']['x'],
            result['top_crop']['height'] + result['top_crop']['y']
        )
    cropped_image = image.crop(box)
    resized_image = cropped_image.resize(output_size)

    setattr(resized_image, "url", url)

    if export:
        if not filename:
            hash_ = hashlib.sha1()
            hash_.update(str(time.time()).encode('utf8'))
            filename = hash_.hexdigest()

        filepath = LOCAL_PROCESSED_DATA_PATH / f"{filename}.{format}"

        setattr(resized_image, "filename", filename)
        setattr(resized_image, "path", filepath)

        resized_image.save(filepath, format, quality=90)

    return resized_image