import cv2
import numpy as np
from PIL import Image
from src.paths import LOCAL_MODELS_PATH


def detect_objects(img: np.ndarray, thres: float = 0.45):

    classFile = LOCAL_MODELS_PATH / 'coco.names'
    configPath = str(LOCAL_MODELS_PATH /
                     'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
    weightsPath = str(LOCAL_MODELS_PATH / 'frozen_inference_graph.pb')

    with open(classFile, 'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')

    net = cv2.dnn_DetectionModel(weightsPath, configPath)
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    classIds, confs, bbox = net.detect(img, confThreshold=thres)

    return classIds, classNames, confs, bbox


def get_obj_bboxes(img: Image):
    img_ = np.array(img)
    return detect_objects(img_)[-1]


def object_area_coverage(img, bboxes):
    """
    Checks the percentage of each half (left and right)
    of image `img` is occupied by `bboxes`. Returns tuple of list
    of percentages for left and right, respectivelly.
    """
    W, H = img.size
    total_area = W * H

    l_percs = []
    r_percs = []

    for b in bboxes:
        x, y, w, h = b
        b_area_tot = w*h
        b_area_right = max(0, ((x+w)-W/2)*h)
        b_area_left = b_area_tot - b_area_right
        l_percs.append(b_area_left/total_area)
        r_percs.append(b_area_right/total_area)

    return np.array(list(zip(l_percs, r_percs)))


def is_left_more_covered(area_distributions: np.array):
    sums = area_distributions.sum(axis=0)
    return sums[0] > sums[1]


def flip_if_necessary(img: Image):
    bboxes = get_obj_bboxes(img)
    area_dist = object_area_coverage(img, bboxes)
    if is_left_more_covered(area_dist):
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img.convert("RGBA")
