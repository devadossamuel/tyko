FROM python:3.7-alpine as builder
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-client mariadb-dev libressl-dev libxml2-dev libxslt-dev

RUN python -m pip install pip --upgrade
RUN pip install gunicorn mysqlclient lxml flask sqlalchemy
COPY ["requirements.txt", "setup.py", "setup.cfg", "/build/"]
COPY tyko/ /build/tyko/
WORKDIR /build
RUN pip wheel --wheel-dir /build/wheels gunicorn mysqlclient
RUN pip wheel --wheel-dir /build/wheels -r /build/requirements.txt
RUN python setup.py bdist_wheel

FROM python:3.7-alpine as app
ARG TYKO_USERNAME
ARG TYKO_PASSWORD
ARG DB_URI

COPY requirements.txt ./requirements.txt
COPY --from=builder /build/wheels/*.whl ./wheel/
COPY --from=builder /build/dist/*.whl ./dist/

RUN apk update && apk add --no-cache mariadb-client mariadb-dev \
    && pip install --no-index --find-links=./wheel dist/tyko-*.whl gunicorn mysqlclient -r requirements.txt


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
