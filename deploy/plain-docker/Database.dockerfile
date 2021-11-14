FROM postgres:14-alpine

COPY ../config/postgresql.conf /etc/postgresql/postgresql.conf

ENTRYPOINT ["docker-entrypoint.sh"]