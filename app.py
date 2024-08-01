from fastapi import FastAPI, Request, UploadFile
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import time
import tensorflow as tf
import numpy as np
import io
from PIL import Image
import cv2 as cv

TIME_FOR_PREDICT = 10

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def preprocessImage(img):
    h,w,c = img.shape
    centerX, centerY = w // 2, h // 2
    k = (w if w < h else h) // 2
    return cv.resize(img[centerY - k : centerY + k, centerX - k : centerX + k], (128, 128))/ 255.

ipDict = {}

# 모델 로드
cloudModel = tf.keras.models.load_model('./models/cloudmodel_v1.h5', compile=False)
weatherModel = tf.keras.models.load_model('./models/weathermodel_v1.h5', compile=False)

cloudModel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
weatherModel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# 비동기 처리
@app.post('/api/predict')
async def APIpredict(request: Request, file : UploadFile):
	ipAddress = request.client.host
	current_time = int(time.time())
	if ipDict.get(ipAddress) is None:
		ipDict[ipAddress] = current_time
	else:
		if current_time - ipDict[ipAddress] < TIME_FOR_PREDICT:
			return {
				"Status": False,
				"Cause": "limitation for server"
			}


	content = file.file.read()
	img = np.array(Image.open(io.BytesIO(content)))

	# 예측하자
	cloudPrediction = cloudModel.predict(np.array([
		preprocessImage(img)
	]))
	isCloudy = cloudPrediction[0][0] > 0.5

	


	return {
		"Status": True,
		"prediction": 1
	}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=999, reload=True)
