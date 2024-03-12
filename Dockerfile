FROM python:3.12-bullseye

COPY . /app
WORKDIR /app

RUN pip install -r /app/requirements/base.txt