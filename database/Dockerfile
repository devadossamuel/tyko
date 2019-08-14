FROM bitnami/mariadb:latest
#RUN mkdir /var/lib/mysql/data && chown mysql:mysql  /var/lib/mysql/data
#RUN ls -la  /var/lib/mysql
#USER mysql
COPY database/init/*.sql  /docker-entrypoint-initdb.d/
#COPY sample_data/*.sql /docker-entrypoint-initdb.d/