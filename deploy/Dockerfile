FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-client mariadb-dev libressl-dev libxml2-dev libxslt-dev
ARG TYKO_USERNAME
ARG TYKO_PASSWORD
ARG DB_URI

RUN python -m pip install pip --upgrade
RUN pip install gunicorn mysqlclient lxml flask sqlalchemy

COPY dist/*.whl /dist/
RUN pip install dist/tyko-*.whl

WORKDIR /app
VOLUME /database

# Create a config file

RUN echo "SQLALCHEMY_DATABASE_URI = '${DB_URI}'" > /app/config.cfg \
  && echo "USERNAME = '${TYKO_USERNAME}'" >> /app/config.cfg \
  && echo "PASSWORD = '${TYKO_PASSWORD}'" >> /app/config.cfg

ENV TYKO_SETTINGS=/app/config.cfg
