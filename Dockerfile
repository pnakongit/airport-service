FROM python:3.10.11-slim
LABEL maintainer="p.nakonechnyi@gmail.com"

ENV PYTHONUNBUFFERED=1

WORKDIR app/

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN mkdir ./media

RUN adduser \
    --disabled-password \
    --no-create-home \
    airport_service_user

RUN chown -R airport_service_user ./media
RUN chmod -R 755 ./media

USER airport_service_user
