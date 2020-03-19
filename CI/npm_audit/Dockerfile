FROM node
ARG USER_ID=1001
ARG GROUP_ID=1001

RUN groupadd -g $GROUP_ID user && \
    useradd -u $USER_ID -s /bin/sh -m -d /home/user  -g user user
COPY package.json package-lock.json /home/user/
RUN chown user /home/user/package.json
RUN chown user /home/user/package-lock.json
USER user
RUN cd /home/user && npm ci
