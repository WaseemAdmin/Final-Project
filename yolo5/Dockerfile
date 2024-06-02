FROM ultralytics/yolov5:latest-cpu
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN curl -L https://github.com/ultralytics/yolov5/releases/download/v6.1/yolov5s.pt -o yolov5s.pt

COPY . .

ENV AWS_ACCESS_KEY_ID="AKIA5SPWCQVQPIYAZUWP"
ENV AWS_SECRET_ACCESS_KEY="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"

CMD ["python3", "app.py"]