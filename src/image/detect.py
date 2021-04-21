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


def get_obj_bboxes(img: Image, thresh: float = 0.55):
    img_ = np.array(img)

    bboxes = detect_objects(img_)[-1]
    conf_lvls = detect_objects(img_)[-2]

    filtered_bboxes = []

    for c, b in zip(conf_lvls, bboxes):
        if c >= thresh:
            filtered_bboxes.append(b)

    return np.array(filtered_bboxes)


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
    try:
        for b in bboxes:
            x, y, w, h = b
            b_area_tot = w*h
            b_area_right = max(0, ((x+w)-W/2)*h)
            b_area_left = b_area_tot - b_area_right
            l_percs.append(b_area_left/total_area)
            r_percs.append(b_area_right/total_area)
    except Exception as e:
        print('b      :', b)
        print('bboxes :', bboxes)
        raise e

    return np.array(list(zip(l_percs, r_percs)))


def is_left_more_covered(area_distributions: np.array):
    if len(area_distributions) == 0:
        return False
    sums = area_distributions.sum(axis=0)
    return sums[0] > sums[1]


def flip_if_necessary(img: Image, min_conf: float = 0.65):
    bboxes = get_obj_bboxes(img)
    if not len(bboxes) == 0:
        area_dist = object_area_coverage(img, bboxes)
        if is_left_more_covered(area_dist):
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img.convert("RGBA")
