from fastapi import FastAPI, Request, UploadFile
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import time
import tensorflow as tf
import numpy as np
import io
from PIL import Image
import cv2 as cv

TIME_FOR_PREDICT = 1

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


# 기상청 API가 너무 느려서 데이터를 미리 작성합니다
# data = ''
# with open('data.txt') as f:
# 	data = f.readlines()[-2].rstrip().split()

tmpData = "[0.38       1.         0.41666667 0.85       0.37285714]".split()
temperature = float(tmpData[0][1:])
windSpeed = float(tmpData[2])
humidity = float(tmpData[3])
atmoPressure = float(tmpData[4][:-1])

# windSpeed = float(data[5]) #풍속
# temperature = float(data[11]) #기온
# humidity = float(data[19]) #습도
# atmoPressure = float(data[29]) #기압

print(windSpeed, temperature, humidity, atmoPressure)

"""
df['기온'] = (df['기온'] + 20) / 60
df['강수량'] = df['강수량'].apply(lambda x: 1 if x > 0 else 0)
df['풍속'] = df['풍속'] / 12
df['습도'] = df['습도'] / 100
df['기압'] = (df['기압'] - 980) / 70
df['운량'] = df['운량'].replace([0,1,2,3], 0).replace([4,5,6,7,8,9,10], 1)
"""


def preprocessImage(img):
	h,w,c = img.shape
	centerX, centerY = w // 2, h // 2
	k = (w if w < h else h) // 2
	return cv.resize(img[centerY - k : centerY + k, centerX - k : centerX + k], (128, 128))/ 255.

ipDict = {}

# 모델 로드
cloudModel = tf.keras.models.load_model('./models/cloudmodel_v1.keras')#, compile=False)
weatherModel = tf.keras.models.load_model('./models/weathermodel_v1.keras')#, compile=False)

# cloudModel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
# weatherModel.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

@app.get('/api/ok')
def isOk():
	return True

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
		ipDict[ipAddress] = current_time


	content = file.file.read()
	img = np.array(Image.open(io.BytesIO(content)))[:,:,::-1]
	# BGR이므로 변경
	# Image.fromarray((preprocessImage(img)*255).astype(np.uint8)).save(f"{int(time.time())}.jpg")

	# 예측하자
	cloudPrediction = cloudModel.predict(np.array(
		[preprocessImage(img)]
	))
	
	# isCloudy = 1. if cloudPrediction[0][0] > 0.5 else 0.
	isCloudy = cloudPrediction[0][0]

	# print(temperature,
	# 	isCloudy,
	# 	windSpeed,
	# 	humidity,
	# 	atmoPressure)

	# df['기온'], df['운량'], df['풍속'], df['습도'], df['기압']
	rainPrediction = weatherModel.predict(np.array([[
		temperature,
		isCloudy,
		windSpeed,
		humidity,
		atmoPressure
	]]))
	# [(temperature + 20) / 60,
	# isCloudy,
	# windSpeed / 12,
	# humidity / 100,
	# (atmoPressure - 980) / 70]

	returnText = {
		"Status": True,
		"prediction": {
			"rain" : float(rainPrediction[0][0]),
			"cloud" : float(cloudPrediction[0][0])
		}
	}
	# print(returnText)
	return returnText

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=999, reload=True)
