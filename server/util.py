import joblib
import json
import os
import numpy as np
import base64
import cv2
from wavelet import w2d

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARTIFACTS_DIR = os.path.join(BASE_DIR, "artifacts")
OPENCV_DIR = os.path.join(BASE_DIR, "opencv", "haarcascades")

__class_name_to_number = {}
__class_number_to_name = {}
__model = None
__face_cascade = None
__face_cascade_alt = None
__eye_cascade = None


def classify_image(image_base64_data, file_path=None):
    if __model is None or not __class_name_to_number or not __class_number_to_name:
        load_saved_artifacts()

    imgs = get_cropped_image_if_2_eyes(file_path, image_base64_data)

    if not imgs:
        return []

    result = []
    for img in imgs:
        scalled_raw_img = cv2.resize(img, (32, 32))
        img_har = w2d(img, 'db1', 5)
        scalled_img_har = cv2.resize(img_har, (32, 32))
        combined_img = np.vstack((
            scalled_raw_img.reshape(32 * 32 * 3, 1),
            scalled_img_har.reshape(32 * 32, 1)
        ))

        len_image_array = 32 * 32 * 3 + 32 * 32
        final = combined_img.reshape(1, len_image_array).astype(float)

        # Use probability argmax so the shown label always matches the confidence bars.
        # SVC predict() can disagree with predict_proba() on borderline cases.
        probabilities = np.around(__model.predict_proba(final) * 100, 2).tolist()[0]
        best_class_num = int(np.argmax(probabilities))

        result.append({
            'class': class_number_to_name(best_class_num),
            'class_probability': probabilities,
            'class_dictionary': __class_name_to_number
        })

    return result


def class_number_to_name(class_num):
    return __class_number_to_name[class_num]


def load_saved_artifacts():
    print("loading saved artifacts...start")
    global __class_name_to_number
    global __class_number_to_name
    global __model
    global __face_cascade
    global __face_cascade_alt
    global __eye_cascade

    class_dict_path = os.path.join(ARTIFACTS_DIR, "class_dictionary.json")
    model_path = os.path.join(ARTIFACTS_DIR, "saved_model.pkl")

    with open(class_dict_path, "r", encoding="utf-8") as f:
        raw_class_mapping = json.load(f)
        __class_name_to_number = {os.path.basename(k): v for k, v in raw_class_mapping.items()}
        __class_number_to_name = {v: os.path.basename(k) for k, v in raw_class_mapping.items()}

    if __model is None:
        with open(model_path, "rb") as f:
            __model = joblib.load(f)

    if __face_cascade is None:
        __face_cascade = cv2.CascadeClassifier(
            os.path.join(OPENCV_DIR, "haarcascade_frontalface_default.xml")
        )
    if __face_cascade_alt is None:
        __face_cascade_alt = cv2.CascadeClassifier(
            os.path.join(OPENCV_DIR, "haarcascade_frontalface_alt2.xml")
        )
    if __eye_cascade is None:
        __eye_cascade = cv2.CascadeClassifier(
            os.path.join(OPENCV_DIR, "haarcascade_eye.xml")
        )

    print("loading saved artifacts...done")


def get_cv2_image_from_base64_string(b64str):
    if not b64str or not isinstance(b64str, str):
        return None

    try:
        if "," in b64str:
            encoded_data = b64str.split(",", 1)[1]
        else:
            encoded_data = b64str

        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception:
        return None


def _detect_faces(gray):
    """Try a few Haar settings so angled / smaller faces are not missed."""
    detection_attempts = [
        (__face_cascade, 1.3, 5),
        (__face_cascade, 1.1, 3),
        (__face_cascade_alt, 1.1, 3),
        (__face_cascade, 1.05, 3),
    ]

    for cascade, scale_factor, min_neighbors in detection_attempts:
        if cascade is None or cascade.empty():
            continue
        faces = cascade.detectMultiScale(gray, scale_factor, min_neighbors)
        if len(faces) > 0:
            return faces

    return []


def get_cropped_image_if_2_eyes(image_path, image_base64_data):
    if __face_cascade is None or __eye_cascade is None:
        load_saved_artifacts()

    if image_path:
        img = cv2.imread(image_path)
    else:
        img = get_cv2_image_from_base64_string(image_base64_data)

    if img is None:
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = _detect_faces(gray)

    faces_with_eyes = []
    faces_only = []

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = __eye_cascade.detectMultiScale(roi_gray)
        if len(eyes) >= 2:
            faces_with_eyes.append(roi_color)
        else:
            faces_only.append(roi_color)

    # Prefer eye-validated faces, then any face, then the full image
    # (so action shots still classify like before).
    if faces_with_eyes:
        return faces_with_eyes
    if faces_only:
        return faces_only
    return [img]


def get_b64_test_image_for_virat():
    with open(os.path.join(BASE_DIR, "b64.txt"), encoding="utf-8") as f:
        return f.read()


if __name__ == '__main__':
    load_saved_artifacts()
    print(classify_image(get_b64_test_image_for_virat(), None))
