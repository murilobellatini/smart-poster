import cv2
import numpy as np
from src.paths import LOCAL_MODELS_PATH


def detect_objects(img:np.ndarray, thres:float = 0.45):

    classFile = LOCAL_MODELS_PATH / 'coco.names'
    configPath = str(LOCAL_MODELS_PATH / 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt')
    weightsPath = str(LOCAL_MODELS_PATH / 'frozen_inference_graph.pb')
    
    with open(classFile,'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')

    net = cv2.dnn_DetectionModel(weightsPath,configPath)
    net.setInputSize(320,320)
    net.setInputScale(1.0/ 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)

    classIds, confs, bbox = net.detect(img,confThreshold=thres)
    
    return classIds, classNames, confs, bbox