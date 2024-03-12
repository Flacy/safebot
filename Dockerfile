FROM python:3.12-bullseye

# Workspace
COPY . /app
WORKDIR /app

# Enviroment
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

RUN pip install -r /app/requirements/base.txt