FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN apt-get update
RUN apt-get install apt-transport-https ca-certificates -y
RUN update-ca-certificates

ENV LISTEN_PORT 8080
EXPOSE 8080

COPY . /app

ENV STATIC_PATH /app/static

RUN pip install -r /app/requirements.txt

