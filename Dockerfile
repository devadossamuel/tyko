FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-client mariadb-dev libressl-dev

RUN pip install -U setuptools wheel sqlalchemy tox mypy flake8 mysqlclient pytest pytest-bdd