FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers mariadb-client mariadb-dev libressl-dev
COPY requirements.txt .
COPY setup.py /app/
COPY setup.cfg /app/
COPY avforms /app/avforms
RUN python -m pip install pip --upgrade
RUN pip install wheel -r requirements.txt
RUN pip install gunicorn
WORKDIR /app
VOLUME /database
