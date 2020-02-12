FROM node:lts-stretch

RUN apt-get update -yqq && \
    apt-get install -yqq --no-install-recommends openjdk-8-jre-headless git && \
    rm -rf /var/lib/apt/lists/*



ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user  -g user user

RUN npm config set unsafe-perm true && \
    npm install -g sonarqube-scanner && \
    sonar-scanner --version

RUN mkdir /.sonar

VOLUME /home/user/.sonar
RUN chown user /home/user/.sonar
RUN chown user /usr/local/lib/node_modules/sonarqube-scanner