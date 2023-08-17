#!/bin/bash

mysql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST -P $DB_PORT -e "DELETE FROM \`$DB_DATABASE\`.users"

