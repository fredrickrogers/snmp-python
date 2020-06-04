FROM python:3.8

WORKDIR /app

COPY src/requirements.txt ./

RUN pip install -r requirements.txt
COPY src /app

CMD ["python", "app.py"]