### Практическая учебная тренировка на отработку понимания принципов работы DDoS фильтрации трафика

Работает на базе flask и bootstrap

Позволяет провести тренировку по следующим принципам:
1. Обнаружить трафик
2. Проверить трафик на работу из Ботнета путем включения CAPTCHA
3. Разрешить или заблокировать трафик с определенного Ip адреса


Приложение для каждой запрошенной сессии создает логины и пароли в необходимом для учителя кол-ве.
Для каждого логина отображается выполнено ли задание теста. Каждому учащемуся выдается 10 из 40 ip адресов в случайном порядке.
Сценарии урока будут доступны на сайте проекта ИТ-вертикаль (проект Московского образования)

**Demo:** [https://lesson212.kasperstudent.ru/](https://lesson212.kasperstudent.ru/)

Вид страницы сессии для учителя:

![Вид страницы сесии для учителя](https://forai.school1409.ru/_media/2125.png)

Страница ученика:

![Страница ученика](https://forai.school1409.ru/_media/2124.png)

Дв файле [docker-compose.yml](docker-compose.yml) необходимо указать требуемые вам настройки работы с базой данных

```
    environment:
      MYSQL_ROOT_PASSWORD: lesson212
      MYSQL_DATABASE: lesson212
      MYSQL_USER: lesson212
      MYSQL_PASSWORD: lesson212
      ....
        environment:
      DB_HOST: db_lesson212
      DB_PORT: 3306
      DB_ROOT_PASSWORD: lesson212
      DB_DATABASE: lesson212
      DB_USER: lesson212
      DB_PASSWORD: lesson212
```

Для запуска приложения на своем сервере вы можете использовать контейнеры:

```commandline
docker-compose up -d
```

После запуска контейнера lesson212 запускается с задержкой опрашивая каждый 5 секунд базу данных. Это связано с тем, что контейнер базы данных
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
