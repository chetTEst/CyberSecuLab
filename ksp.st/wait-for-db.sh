#!/bin/bash

set -e > /var/log/wait-for-db.sh.log 2>&1

host="${DB_HOST:-db_kasperstudentru}"
port="${DB_PORT:-3306}"

until nc -z -v -w30 $host $port; do
  echo "Waiting for $host:$port..." >> /var/log/wait-for-db.sh.log 2>&1
  echo "Waiting for $host:$port..."
  sleep 5
done

/start.sh  #>> /var/log/Flask-app.log 2>&1 &
echo "Flask sart ..."

# Ожидаем завершения всех фоновых процессов
wait
