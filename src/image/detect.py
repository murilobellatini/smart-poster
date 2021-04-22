import cv2
import requests
import numpy as np
from PIL import Image
from smartcrop import SmartCrop

from src.custom_logging import getLogger
from src.paths import LOCAL_MODELS_PATH
from src.image import ImageWrapper

logger = getLogger(__name__)


class ComputerVision(ImageWrapper):

    def __init__(self, model: str = "OpenCV_dnn_DetectionModel") -> None:
        if model == "OpenCV_dnn_DetectionModel":
            self.model = model
        else:
            raise NotImplementedError

        self._setup_model()

    def detect_objects(self, thresh: float = 0.65) -> None:

        detection_available = hasattr(self, 'thresh')

        if not detection_available:
            self.thresh = thresh

        if (self.thresh != thresh) or not detection_available:
            self.thresh = thresh
            self.classIds, self.confs, self.bboxes = self.net.detect(
                self.img_np, confThreshold=thresh)
            logger.info(
                f'{len(self.bboxes)} object(s) detected. Minimum confidence level: {thresh}')
        else:
            logger.info(
                f'Using available detected objects (count: {len(self.bboxes)}). Minimum confidence level: {self.thresh}')

    def flip_if_necessary(self, area_to_keep_free: str = 'LEFT', thresh: float = 0.65) -> Image:

        if area_to_keep_free in ('LEFT', 'RIGHT'):
            keep_left_free = area_to_keep_free == 'LEFT'
        else:
            raise NotImplementedError

        self.detect_objects(thresh=thresh)

        if not len(self.bboxes) == 0:
            self._get_coverage_per_half()
            self._check_if_left_more_covered()
            if self.is_left_more_covered == keep_left_free:
                logger.info('Image flipped')
                return self.img.transpose(Image.FLIP_LEFT_RIGHT).convert("RGBA")
            else:
                logger.info('Image not flipped')
                return self.img.convert("RGBA")

    def draw_detection_bboxes(self, thresh: float = 0.65) -> np.array:

        self.detect_objects(thresh=thresh)

        if len(self.bboxes) == 0:
            logger.info(
                "No objects detected... Aborting drawing of bounding boxes.")
            return

        img_boxed = self.img_np.copy()
        gray = cv2.cvtColor(self.img_np, cv2.COLOR_BGR2GRAY)

        output_rectangles = np.zeros(img_boxed.shape, dtype="uint8")

        for classId, confidence, box in zip(self.classIds.flatten(), self.confs.flatten(), self.bboxes):
            cv2.rectangle(img_boxed, box, color=(0, 255, 0), thickness=2)
            cv2.rectangle(gray, box, color=(0, 0, 0), thickness=cv2.FILLED)
            rectangle = cv2.rectangle(output_rectangles, box, color=(
                255, 255, 255), thickness=cv2.FILLED)
            output_rectangles = cv2.bitwise_or(output_rectangles, rectangle)
            cv2.putText(img_boxed, self.classNames[classId-1].upper(), (box[0]+10,
                        box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(img_boxed, str(round(confidence*100, 2)),
                        (box[0]+200, box[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

        self.img_np_boxed = img_boxed
        self.img_np_boxed_gray = gray
        self.img_np_boxed_bw = output_rectangles

        return self.img_np_boxed

    def smart_crop(self, output_size: tuple = (1080, 1080)):
        ratio = output_size[0]/output_size[1]
        cropper = SmartCrop()
        result = cropper.crop(self.img, 100*ratio, 100)
        box = (
            result['top_crop']['x'],
            result['top_crop']['y'],
            result['top_crop']['width'] + result['top_crop']['x'],
            result['top_crop']['height'] + result['top_crop']['y']
        )
        cropped_image = self.img.crop(box)
        self.resized_image = cropped_image.resize(output_size)

        return self.resized_image

    def _setup_model(self) -> None:

        classFile = LOCAL_MODELS_PATH / 'coco.names'
        configPath = str(LOCAL_MODELS_PATH /
                         'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
        weightsPath = str(LOCAL_MODELS_PATH / 'frozen_inference_graph.pb')

        with open(classFile, 'rt') as f:
            self.classNames = f.read().rstrip('\n').split('\n')

        net = cv2.dnn_DetectionModel(weightsPath, configPath)
        net.setInputSize(320, 320)
        net.setInputScale(1.0 / 127.5)
        net.setInputMean((127.5, 127.5, 127.5))
        net.setInputSwapRB(True)

        self.net = net

        logger.info(f'Computer Vision setup with model: `{self.model}`')

    def _get_coverage_per_half(self) -> np.array:
        """
        Checks the percentage of each half (left and right)
        of image `img` is occupied by `bboxes`. Returns tuple of list
        of percentages for left and right, respectivelly.
        """
        W, H = self.img.size
        total_area = W * H

        l_percs = []
        r_percs = []
        try:
            for b in self.bboxes:
                x, y, w, h = b
                b_area_tot = w*h
                b_area_right = max(0, ((x+w)-W/2)*h)
                b_area_left = b_area_tot - b_area_right
                l_percs.append(b_area_left/total_area)
                r_percs.append(b_area_right/total_area)
        except Exception as e:
            print('b      :', b)
            print('bboxes :', self.bboxes)
            raise e

        self.area_coverages_per_half = np.array(list(zip(l_percs, r_percs)))

        return self.area_coverages_per_half

    def _check_if_left_more_covered(self) -> bool:
        if len(self.area_coverages_per_half) == 0:
            return False
        sums = self.area_coverages_per_half.sum(axis=0)
        self.is_left_more_covered = sums[0] > sums[1]
        return self.is_left_more_covered
