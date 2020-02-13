FROM node:lts-stretch

RUN apt-get update -yqq && \
    apt-get install -yqq --no-install-recommends openjdk-8-jre-headless git && \
    rm -rf /var/lib/apt/lists/*



ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user  -g user user

RUN mkdir /.sonar
USER user

RUN npm config set prefix "${HOME}/.npm-packages"

RUN npm config set unsafe-perm true && \
    npm install -g sonarqube-scanner && \
    sonar-scanner --version
