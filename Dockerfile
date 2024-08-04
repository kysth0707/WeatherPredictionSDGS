FROM python:3.10.5

RUN pip install numpy==1.26.4
RUN pip install tensorflow==2.17.0
RUN pip install fastapi==0.79.0
RUN pip install uvicorn[standard]
RUN pip install pillow==9.2.0
RUN pip install opencv-python==4.5.5.64
RUN pip install python-multipart

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN mkdir -p /test
WORKDIR /test

ENTRYPOINT ["python", "app.py"]