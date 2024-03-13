FROM python:3.12-bullseye AS base

# Arguments
ARG dev=false

# Workspace
COPY ./safebot /app/safebot
COPY ./requirements /app/requirements
WORKDIR /app

# Enviroment
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Requirements
RUN pip install -r /app/requirements/base.txt
RUN if [ ${dev} = true ]; then pip install -r /app/requirements/dev.txt; fi