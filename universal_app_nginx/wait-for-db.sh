#!/bin/bash

set -e > /var/log/wait-for-db.sh.log 2>&1

host="${DB_HOST:-db_test_uts}"
port="${DB_PORT:-3306}"

until nc -z -v -w30 $host $port; do
  echo "Waiting for $host:$port..." >> /var/log/wait-for-db.sh.log 2>&1
  echo "Waiting for $host:$port..."
  sleep 5
done

until nc -z -v -w30 redis 6379; do
  echo "Waiting for Redis connection..."
  sleep 5
done
echo "Redis is up and running!"


cron -f >> /var/log/cron-app.log 2>&1 &
echo "cron sart ..."
/start.sh  >> /var/log/Flask-app.log 2>&1 &
echo "Flask sart ..."

# Ожидаем завершения всех фоновых процессов
wait
