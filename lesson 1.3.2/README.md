### Практическая учебная тренировка на отработку понимания принципов работы Брандмауэров и Антивирусов

Работает на базе flask и bootstrap

Позволяет провести тренировку по следующим принципам:
1. Провенрка hash файла на VirusTotal
2. Изучение потенциальной опасности открытых портов


Приложение для каждой запрошенной сессии создает логины и пароли в необходимом для учителя кол-ве.
Для каждого логина отображается выполнено ли задание теста. На каждую часть отводится по 8 вопросов.
Сценарии урока будут доступны на сайте проекта ИТ-вертикаль (проект Московского образования)

**Demo:** [https://lesson132.kasperstudent.ru/](https://lesson1312.kasperstudent.ru/)

Вид страницы сесии для учителя:

~~![Вид страницы сесии для учителя](https://forai.school1409.ru/_media/1320.png)~~

Система бновлена до websocket, теперь вид главной страницы иной

Страница ученика:

![Страница ученика](https://forai.school1409.ru/_media/1321.png)

Страница ученика:

![Страница ученика](https://forai.school1409.ru/_media/1322.png)


в файле [docker-compose.yml](docker-compose.yml) необходимо указать требуемые вам настройки работы с базой данных

```
    environment:
      MYSQL_ROOT_PASSWORD: lesson132
      MYSQL_DATABASE: lesson132
      MYSQL_USER: lesson132
      MYSQL_PASSWORD: lesson132
      ....
        environment:
      DB_HOST: db_lesson132
      DB_PORT: 3306
      DB_ROOT_PASSWORD: lesson132
      DB_DATABASE: lesson132
      DB_USER: lesson132
      DB_PASSWORD: lesson132
```

Для запуска приложения на своем сервере вы можете использовать контейнеры:

```commandline
docker-compose up -d
```

После запуска контейнера lesson132 запускается с задержкой опрашивая каждый 5 секунд базу данных. Это связано с тем, что контейнер базы данных
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
