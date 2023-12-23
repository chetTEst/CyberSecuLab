### Задание для CTF. Настройка условного Firewall для доступа к сайту

Работает на базе flask и pyotp

в файле [docker-compose.yml](docker-compose.yml) необходимо указать требуемые вам настройки работы с базой данных

```
    environment:
      MYSQL_ROOT_PASSWORD: baseTask1
      MYSQL_DATABASE: baseTask1
      MYSQL_USER: baseTask1
      MYSQL_PASSWORD: baseTask1
      ....
        environment:
      DB_HOST: db_baseTask1
      DB_PORT: 3306
      DB_ROOT_PASSWORD: baseTask1
      DB_DATABASE: baseTask1
      DB_USER: baseTask1
      DB_PASSWORD: baseTask1
```

Для запуска приложения на своем сервере вы можете использовать контейнеры:

```commandline
docker-compose up -d
```

После запуска контейнера baseTask1 запускается с задержкой опрашивая каждый 5 секунд базу данных. Это связано с тем, что контейнер базы данных
запускается медленнее. Через 5-10 секунд, а может и больше приложение стартанёт


Вы можете использовать и SQLite [__init__.py](flask_app%2Fapp%2F__init__.py), но это только на этапе отладки. Через
переменные окружения определяется как был осуществлен запуск, в контейнере или через run:

```python
    if environ.get('FLASK_ENV') == 'production':
        # Запущено через wsgi
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
    else:
        # Запущено через run.py
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'lesson.db')
```