FROM node:lts-stretch

WORKDIR /code

RUN apt-get update -yqq && \
    apt-get install -yqq --no-install-recommends openjdk-8-jre-headless && \
    rm -rf /var/lib/apt/lists/*

RUN npm config set unsafe-perm true && \
    npm install -g sonarqube-scanner && \
    sonar-scanner --version

ENTRYPOINT ["sonar-scanner"]