import pandas as pd
import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model('./models/weathermodel_v1.keras')#, compile=False)

df = pd.read_csv('./hour_dataset.csv', encoding='EUC-KR')

labelsToRemove = ['지점', '일시', '풍향(16방위)',
'증기압(hPa)', '이슬점온도(°C)', '해면기압(hPa)', '일조(hr)',
'일사(MJ/m2)', '적설(cm)', '3시간신적설(cm)', '중하층운량(10분위)',
'운형(운형약어)', '최저운고(100m )', '시정(10m)', '지면상태(지면상태코드)', '현상번호(국내식)',
'지면온도(°C)', '5cm 지중온도(°C)', '10cm 지중온도(°C)', '20cm 지중온도(°C)',
'30cm 지중온도(°C)']

for label in labelsToRemove:
	df = df.drop(label, axis=1)

df = df.rename(
	columns = {
		"기온(°C)" : "기온",
		"강수량(mm)" : "강수량",
		"풍속(m/s)" : "풍속",
		"습도(%)" : "습도",
		"현지기압(hPa)" : "기압",
		"전운량(10분위)" : "운량"
	}
)
df.head()

df = df.fillna(0)

df['기온'] = (df['기온'] + 20) / 60
df['강수량'] = df['강수량'].apply(lambda x: 1 if x > 0 else 0)
df['풍속'] = df['풍속'] / 12
df['습도'] = df['습도'] / 100
df['기압'] = (df['기압'] - 980) / 70
df['운량'] = df['운량'].replace([0,1,2,3], 0).replace([4,5,6,7,8,9,10], 1)

dataX = np.array(list(zip(df['기온'], df['운량'], df['풍속'], df['습도'], df['기압'])))
dataY = np.array(df['강수량'])

for i in range(30, len(dataX)):
	if dataY[i] == 1:
		tmp = dataX[i]
		tmp[1] = 0.
		# print(tmp)
		pre1 = model.predict(np.array([tmp]))
		tmp[1] = 1.
		pre2 = model.predict(np.array([tmp]))

		if pre2 > pre1:
			print(dataX[i])
			break