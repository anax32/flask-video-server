FROM python:3-slim

ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
ADD src/__init__.py .
ADD src/app.py .
ADD templates/index.html templates/index.html

ENV FLASK_DEBUG=0
ENV FLASK_ENV=production
ENV VIDEO_PATH=/data/
ENV PYTHONUNBUFFERED=TRUE

# 10*(1<<x)
ENV BUFFER_SIZE_MULTIPLIER=14

EXPOSE 5000

CMD gunicorn --bind=0.0.0.0:5000 app:app --log-level debug
