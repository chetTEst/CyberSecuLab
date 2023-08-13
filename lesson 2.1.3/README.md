### Практическая учебная тренировка на отработку понимания принципов запросов к базе данных на языке SQL

Работает на базе flask и bootstrap, ACE editor, Jobe server

В качестве языка запросов используется выдуманный язык «Запросик»:
* **ПоложитьВ** /* Положить что-то в… */ 
* **ЗНАЧЕНИЕ** /* Вещи, которые вы хотите разместить */ 
* **ВЫБЕРИ** /* Что именно выбирать в хранилище. */ 
* **ИзХранилища** /* От куда брать или куда класть. */ 
* **ГДЕ** /* Специальный сравнитель полки хранилища. */ 
* **ОБНОВИТЬ** /*  Обновить данные. */ 
* **УСТАНОВИТЬ** /* Задать значение в хранилище. */ 
* **УДАЛИТ**Ь /*  Удалить запись из хранилища. */ 
* **--** Начало комментария (все что написано после – не команда)

Тренировка содержит в себе 7 задач:
1. Выбрать данные по условию
2. Выбрать данные по условию
3. Удалить данные из базы данных
4. Обновить значение в базе данных
5. Добавить данные в базу данных
6. Выполнение SQL иньекции
7. Защита от SQL иньекции

Приложение для каждой запрошенной сессии создает логины и пароли в необходимом для учителя кол-ве.
Для каждого логина отображается выполнено ли задание теста. Каждому учащемуся выдается 7 из 15 задач, по 2-3 варианта на задачу.
Сценарии урока будут доступны на сайте проекта ИТ-вертикаль (проект Московского образования)

**Demo:** [https://lesson213.kasperstudent.ru/](https://lesson213.kasperstudent.ru/)

Вид страницы сессии для учителя:

![Вид страницы сесии для учителя](https://forai.school1409.ru/_media/2131.png)

Страница ученика 1:

![Страница ученика](https://forai.school1409.ru/_media/2132.png)

Страница ученика 2:

![Страница ученика](https://forai.school1409.ru/_media/2133.png)

Страница ученика 3:

![Страница ученика](https://forai.school1409.ru/_media/2134.png)

Для запуска приложения на своем сервере вы можете использовать контейнеры:

```commandline
docker-compose up -d
```

После запуска контейнера должен "вылететь" контейнер приложения. Это связано с тем, что контейнер базы данных
запускается медленнее. Через 5-10 секунд, а может и больше запустите контейнер приложения вновь:

```commandline
docker start lesson213_lesson213_1
```

в файле [__init__.py](flask_app%2Fapp%2F__init__.py) необходимо указать адрес вашего сервера для работы с базой данных

```
mysql+pymysql://lesson213:lesson213@<адрес>:33062/lesson213
```

А так же указать необходимые логины, пароли и имена базы данных в [docker-compose.yml](docker-compose.yml)

Либо вы можете использовать SQLite:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + pjoin(path, 'tmp', 'lesson.db')
```