# syntax = docker/dockerfile:experimental
FROM python:3.7-alpine as builder
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-client mariadb-dev libressl-dev libxml2-dev libxslt-dev

RUN python -m pip install pip --upgrade
RUN pip install gunicorn mysqlclient lxml flask sqlalchemy
COPY ["requirements.txt", "setup.py", "setup.cfg", "/build/"]
COPY tyko/ /build/tyko/
WORKDIR /build
RUN python setup.py bdist_wheel

FROM python:3.7-alpine as app
ARG TYKO_USERNAME
ARG TYKO_PASSWORD
ARG DB_URI

COPY requirements.txt ./requirements.txt
COPY --from=builder /build/dist/*.whl ./dist/
RUN --mount=type=cache,target=/root/.cache/pip apk update && apk add --no-cache mariadb-client mariadb-dev \
    && pip install gunicorn mysqlclient dist/tyko-*.whl -r requirements.txt

WORKDIR /app
VOLUME /database
# Create a config file
RUN echo "SQLALCHEMY_DATABASE_URI = '${DB_URI}'" > /app/config.cfg \
  && echo "SQLALCHEMY_TRACK_MODIFICATIONS = False" >> /app/config.cfg \
  && echo "USERNAME = '${TYKO_USERNAME}'" >> /app/config.cfg \
  && echo "PASSWORD = '${TYKO_PASSWORD}'" >> /app/config.cfg

COPY deploy/start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENV TYKO_SETTINGS=/app/config.cfg
