FROM mariadb:5.5.64-trusty
ENV MYSQL_ROOT_PASSWORD=my-secret-pw
ENV MYSQL_DATABASE=av_preservation
ENV MYSQL_USER=avuser
ENV MYSQL_PASSWORD=avpsw
COPY av_preservation.sql /docker-entrypoint-initdb.d/