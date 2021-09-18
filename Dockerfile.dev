FROM python:3-slim

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
ADD app.py app.py
ADD templates/index.html templates/index.html

ENV FLASK_APP=/app/app.py
ENV FLASK_DEBUG=0
ENV VIDEO_PATH=/data/

CMD flask run --host=0.0.0.0 --port=8080
