import numpy as np
import pywt
import cv2


def w2d(img, mode='haar', level=1):
    """Wavelet transform used for edge/texture features.

    Uses COLOR_RGB2GRAY to stay consistent with the training notebook and
    the shipped saved_model.pkl (images are OpenCV BGR arrays in both places).
    If you retrain with COLOR_BGR2GRAY, update this to match and re-export the model.
    """
    imArray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    imArray = np.float32(imArray)
    imArray /= 255.0

    coeffs = pywt.wavedec2(imArray, mode, level=level)

    coeffs_H = list(coeffs)
    coeffs_H[0] *= 0

    imArray_H = pywt.waverec2(coeffs_H, mode)
    imArray_H *= 255.0
    imArray_H = np.uint8(imArray_H)

    return imArray_H
