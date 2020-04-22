FROM ubuntu:18.04
RUN apt update -y && apt install -y curl
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
RUN apt update -y && apt install -y nodejs


ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user  -g user user

COPY package.json package-lock.json /home/user/

RUN chown user /home/user/package.json
RUN chown user /home/user/package-lock.json
RUN echo 'export PATH=$PATH:/home/user/node_modules/.bin' >> /home/user/.bashrc
USER user
RUN cd /home/user && npm install -y
