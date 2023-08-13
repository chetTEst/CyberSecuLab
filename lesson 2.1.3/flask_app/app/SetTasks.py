import random
import base64
from .models import db, Tasks
from . import app

random.seed()


def setTasks():
    if Tasks.query.count() == 0:
        dataTasks = [{
                         'text': '<p>Напишите запрос, который <b>ВЫБЕРЕТ</b> записи 2022 года.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 1,
                         'reference': 'SELECT * FROM Trees WHERE year = 2022;', 'chek_reference': None},
                     {
                         'text': '<p>Напишите запрос, который <b>ВЫБЕРЕТ</b> записи 2021 года.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 1,
                         'reference': 'SELECT * FROM Trees WHERE year = 2021;', 'chek_reference': None},
                     {
                         'text': '<p>Напишите запрос, который <b>ВЫБЕРЕТ</b> записи 2020 года.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 1,
                         'reference': 'SELECT * FROM Trees WHERE year = 2020;', 'chek_reference': None},
                     {
                         'text': '<p>Напишите запрос, который <b>ВЫБЕРЕТ</b> записи 2019 года.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 1,
                         'reference': 'SELECT * FROM Trees WHERE year = 2019;', 'chek_reference': None},
                     {
                         'text': '<p>Напишите запрос, который <b>ВЫБЕРЕТ</b> записи со сбором урожая больше 1700 кг.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 2,
                         'reference': 'SELECT * FROM Trees WHERE harvest > 1700;', 'chek_reference': None},
                     {
                         'text': '<p>Напишите запрос, который <b>ВЫБЕРЕТ</b> записи со сбором урожая меньше 1500 кг.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 2,
                         'reference': 'SELECT * FROM Trees WHERE harvest < 1500;', 'chek_reference': None},
                     {
                         'text': '<p>Напишите запрос, который <b>УДАЛИТ</b> все записи по дереву Вишня.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 3,
                         'reference': "DELETE FROM Trees WHERE type = 'Вишня';", 'chek_reference': 'SELECT * FROM Trees'},
                     {
                         'text': '<p>Напишите запрос, который <b>УДАЛИТ</b> все записи по дереву Яблоня.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие;</p>',
                         'number': 3,
                         'reference': "DELETE FROM Trees WHERE type = 'Яблоня';", 'chek_reference': 'SELECT * FROM Trees'},
                     {
                         'text': '<p><b>ОБНОВИТЕ</b> значение плода Березы <b>УСТАНОВИв</b> его в значение Орешек.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ Хранилище ЧТОСДЕЛАТЬ Поле=что_положить Условие;</p>',
                         'number': 4,
                         'reference': "UPDATE Trees SET fruit = 'Орешек' WHERE type = 'Береза';",
                         'chek_reference': "SELECT * FROM Trees WHERE fruit = 'Орешек'"},
                     {
                         'text': '<p><b>ОБНОВИТЕ</b> значение плода Тополя <b>УСТАНОВИв</b> его в значение Коробочка.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ Хранилище ЧТОСДЕЛАТЬ Поле=что_положить Условие;</p>',
                         'number': 4,
                         'reference': "UPDATE Trees SET fruit = 'Коробочка' WHERE type = 'Тополь';",
                         'chek_reference': "SELECT * FROM Trees WHERE fruit = 'Коробочка'"},
                     {
                         'text': '<p><b>Положите В</b> в таблицу новую запись: Черешня Съедобное Ипуть собрано 1222 кг за 2020 год.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ Хранилище (ИмяПоля, ИмяПоля...) ЗНАЧЕНИЕ (\'текст\', число);</p>',
                         'number': 5,
                         'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Ипуть', 1222, 2020);",
                         'chek_reference': "SELECT type, fruitful, fruit, harvest, year FROM Trees WHERE fruit = 'Ипуть'"},
                     {
                         'text': '<p><b>Положите В</b> в таблицу новую запись: Черешня Съедобное Фатеж собрано 1322 кг за 2020 год.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ Хранилище (ИмяПоля, ИмяПоля...) ЗНАЧЕНИЕ (\'текст\', число);</p>',
                         'number': 5,
                         'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Фатеж', 1322, 2020);",
                         'chek_reference': "SELECT type, fruitful, fruit, harvest, year FROM Trees WHERE fruit = 'Фатеж'"},
                     {
                         'text': '<p><b>Положите В</b> в таблицу новую запись: Черешня Съедобное Черемашная собрано 1000 кг за 2021 год.<br/>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ Хранилище (ИмяПоля, ИмяПоля...) ЗНАЧЕНИЕ (\'текст\', число);</p>',
                         'number': 5,
                         'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Черемашная', 1000, 2021);",
                         'chek_reference': "SELECT type, fruitful, fruit, harvest, year FROM Trees WHERE fruit = 'Черемашная'"},
                     {
                         'text': '<p>У вас есть поле ввода, для поиска по типу деревьев в нашей базе данных. Ниже вы видите запрос к БД. Используя поле поискового запроса, осуществите SQL иньекцию для получения всех записей БД для полей: <i>Тип, Съедобное, Плод, Урожай, Год</i></p><p><i>Запрос создан, он заблокирован. Изменить его сейчас нельзя. Можно редактировать только поле поискгового запроса.</i>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие = \'[ЗДЕСЬ_БУДЕТ_ВАШ_Поисковый_ЗАПРОС_КАК_ЕСТЬ]\';</p>',
                         'number': 6,
                         'reference': "SELECT type, fruitful, fruit, harvest, year FROM Trees WHERE type = [ТЕКСТ_ЗАПРОСА];",
                         'chek_reference': "SELECT type, fruitful, fruit, harvest, year FROM Trees"},
                    {
                        'text': '<p>У вас есть поле ввода, для поиска по типу деревьев в нашей базе данных, в котором уже указана SQL иньекция. Исправьте запрос к БД так, чтобы иньекция не удалась, для этого создайте из текущего простого запроса - параметрический запрос. Каждый параметр указывается не как есть, а в виде знака <u><b>?</b></u></p><p><i>Запрос к БД разблокирован. Теперь изменить поисковый запрос, в котором указана SQL иньекция, нельзя. Можно редактировать только запрос к базе данных.</i>Структура запроса:</p><p class="font-weight-light text-monospace">ЧТОСДЕЛАТЬ для_каких_полей ИЗ_какого_Хранилища Условие = Знак_вопроса;</p>',
                        'number': 7,
                        'reference': 'SELECT type, fruitful, fruit, harvest, year FROM Trees WHERE type = "\';SELECT type, fruitful, fruit, harvest, year FROM Trees; --\'"',
                        'chek_reference': 'SELECT type, fruitful, fruit, harvest, year FROM Trees WHERE type = "\';SELECT type, fruitful, fruit, harvest, year FROM Trees; --\'"'}


                     ]
        with app.app_context():
            for task in dataTasks:
                question = Tasks(number=task['number'], text=task['text'], reference=task['reference'],
                                 chek_reference=task['chek_reference'])
                db.session.add(question)

setTasks()
