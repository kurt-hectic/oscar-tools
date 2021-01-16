FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV LISTEN_PORT 8080
EXPOSE 8080

COPY . /app

ENV STATIC_PATH /app/static

RUN pip install -r /app/requirements.txt

