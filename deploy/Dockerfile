FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-client mariadb-dev libressl-dev
ARG TYKO_USERNAME
ARG TYKO_PASSWORD
ARG DB_URI=sqlite:///:memory:

COPY dist/*.whl /dist/
RUN python -m pip install pip --upgrade
RUN pip install gunicorn mysqlclient && \
    pip install dist/tyko-*.whl
WORKDIR /app
VOLUME /database

# Create a config file

RUN echo "DB_ENGINE = '${DB_URI}'" > /app/config.cfg \
  && echo "USERNAME = '${TYKO_USERNAME}'" >> /app/config.cfg \
  && echo "PASSWORD = '${TYKO_PASSWORD}'" >> /app/config.cfg

ENV TYKO_SETTINGS=/app/config.cfg
