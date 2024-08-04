import numpy as np
import tensorflow as tf
from PIL import Image
import io
import cv2 as cv

cloudModel = tf.keras.models.load_model('./models/cloudmodel_v1.keras')#, compile=False)
weatherModel = tf.keras.models.load_model('./models/weathermodel_v1.keras')#, compile=False)

def preprocessImage(img):
	h,w,c = img.shape
	centerX, centerY = w // 2, h // 2
	k = (w if w < h else h) // 2
	return cv.resize(img[centerY - k : centerY + k, centerX - k : centerX + k], (128, 128))/ 255.

with open('./testclouds/9.jpg', 'rb') as f:
	content = f.read()
img = np.array(Image.open(io.BytesIO(content)))
# img = cv.imread('./testclouds/9.jpg')

data = ''
with open('data.txt') as f:
	data = f.readlines()[-2].rstrip().split()

windSpeed = float(data[5]) #풍속
temperature = float(data[11]) #기온
humidity = float(data[19]) #습도
atmoPressure = float(data[29]) #기압

# 이미지 전처리
preprocessed_img = preprocessImage(img)
print(f"Preprocessed Image Shape: {preprocessed_img.shape}")


# 모델 예측
cloudPrediction = cloudModel.predict(np.array([preprocessed_img]))
print(f"Cloud Prediction: {cloudPrediction}")

rainPrediction = weatherModel.predict(np.array([[
    (temperature + 20) / 60,
    cloudPrediction[0][0] > 0.5,
    windSpeed / 12,
    humidity / 100,
    (atmoPressure - 980) / 70
]]))
print(f"Rain Prediction: {rainPrediction}")
