#!/bin/bash

# Загрузка переменных окружения
source /proc/1/environ | xargs -0 -I '{}' echo 'export {}' > /tmp/environment
source /tmp/environment

# Установка PATH
PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin


mysql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST -P $DB_PORT -e "DELETE FROM \`$DB_DATABASE\`.session"
