#!/bin/bash

set -e

# Настройка логирования
LOG_FILE="/var/log/wait-for-db.sh.log"
exec > >(tee -a $LOG_FILE)
exec 2>&1

echo "$(date): Запуск скрипта инициализации..." | tee -a $LOG_FILE

# Переменные окружения
DB_HOST="${DB_HOST:-db_test_uts}"
DB_PORT="${DB_PORT:-3306}"
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"

echo "$(date): Ожидание подключения к базе данных $DB_HOST:$DB_PORT..."

# Ожидание MySQL
until nc -z -v -w30 $DB_HOST $DB_PORT; do
echo "$(date): Ожидание $DB_HOST:$DB_PORT..."
sleep 5
done

echo "$(date): База данных доступна!" | tee -a $LOG_FILE

# Ожидание Redis
echo "$(date): Ожидание подключения к Redis $REDIS_HOST:$REDIS_PORT..."
until nc -z -v -w30 $REDIS_HOST $REDIS_PORT; do
echo "$(date): Ожидание Redis подключения..."
sleep 5
done

echo "$(date): Redis доступен!" | tee -a $LOG_FILE

# Инициализируем базу данных (только один раз)
echo "$(date): Инициализируем базу данных" | tee -a $LOG_FILE
cd /app && python CreateDb.py | tee -a $LOG_FILE

echo "$(date): База данных, инициализирована!" | tee -a $LOG_FILE

# Запуск supervisor для управления процессами
echo "$(date): Запуск supervisor..."

# Проверяем конфигурацию supervisor
if [ -f /etc/supervisor/conf.d/supervisord.conf ]; then
  echo "$(date): Найдена конфигурация supervisor"
  supervisord -n -c /etc/supervisor/conf.d/supervisord.conf
else
  echo "$(date): Конфигурация supervisor не найдена, запуск с базовой конфигурацией"
  supervisord -n
fi