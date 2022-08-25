FROM python:3.9-slim-buster as base

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt-get update && apt-get install redis -y

WORKDIR /code

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM base as local

COPY requirements_dev.txt requirements_dev.txt
RUN pip3 install -r requirements_dev.txt

FROM base as prod

COPY . .
