FROM python:3.9-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./req.txt /req.txt

RUN python -m pip install --upgrade pip

RUN python -m pip install -r /req.txt

COPY ./pos_system/ /app/

WORKDIR /app/
