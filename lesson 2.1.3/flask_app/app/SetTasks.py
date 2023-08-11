import random
import base64
from .models import db, Tasks
from . import app


random.seed()

def setTasks():
    dataTasks = [{'text': 'Напишите запрос, который вернет записи 2022 года', 'number': 1,
                  'reference': 'SELECT * FROM Trees WHERE year = 2022;'},
                 {'text': 'Напишите запрос, который вернет записи 2021 года', 'number': 1,
                  'reference': 'SELECT * FROM Trees WHERE year = 2021;'},
                 {'text': 'Напишите запрос, который вернет записи 2020 года', 'number': 1,
                  'reference': 'SELECT * FROM Trees WHERE year = 2020;'},
                 {'text': 'Напишите запрос, который вернет записи 2019 года', 'number': 1,
                  'reference': 'SELECT * FROM Trees WHERE year = 2019;'},
                 {'text': 'Напишите запрос, который вернет записи со сбором урожая больше 1700 кг', 'number': 2,
                  'reference': 'SELECT * FROM Trees WHERE harvest > 1700;'},
                 {'text': 'Напишите запрос, который вернет записи со сбором урожая меньше 1500 кг', 'number': 2,
                  'reference': 'SELECT * FROM Trees WHERE harvest < 1500;'},
                 {'text': 'Удалите все записи по дереву Вишня', 'number': 3,
                  'reference': "DELETE FROM Trees WHERE type = 'Вишня';"},
                 {'text': 'Удалите все записи по дереву Яблоня', 'number': 3,
                  'reference': "DELETE FROM Trees WHERE type = 'Яблоня';"},
                 {'text': 'Задайте значение Орешек для плода Березы', 'number': 4,
                  'reference': "UPDATE Trees SET fruit = 'Орешек' WHERE type = 'Береза';"},
                 {'text': 'Задайте значение Коробочка для плода Тополя', 'number': 4,
                  'reference': "UPDATE Trees SET fruit = 'Орешек' WHERE type = 'Береза';"},
                 {'text': 'Добавьте новую запись Черешня Съедобное Ипуть собрано 1222 кг за 2020 год', 'number': 5,
                  'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Ипуть', 1222, 2020);"},
                 {'text': 'Добавьте новую запись Черешня Съедобное Фатеж собрано 1322 кг за 2020 год', 'number': 5,
                  'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Фатеж', 1322, 2020);"},
                 {'text': 'Добавьте новую запись Черешня Съедобное Черемашная собрано 1000 кг за 2021 год', 'number': 5,
                  'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Черемашная', 1000, 2021);"}
    ]
    with app.app_context():
        if Tasks.query.count() == 0:
            for task in dataTasks:
                question = Tasks(number=task['number'], text=task['text'], reference=task['reference'])
                db.session.add(question)
            db.session.commit()


setTasks()
