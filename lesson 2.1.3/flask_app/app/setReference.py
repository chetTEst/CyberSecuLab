from runsql import JobeRunExtended, JobeRun

from os.path import join

JOBE_SERVER_URL = "coderunner.new.school1409.ru"
X_API_KEY = '2AAA7A5415B4A9B394B54BF1D2E9D'
path = 'C:\\Users\\1\\PycharmProjects\\CyberSecuLab\\lesson 2.1.3\\flask_app'

data = [{'text': 'Удалите все записи по дереву Вишня', 'number': 3,
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
      'reference': "INSERT INTO Trees (type, fruitful, fruit, harvest, year) Values ('Черешня', 1, 'Черемашная', 1000, 2021);"}]

jobe_extended = JobeRunExtended(X_API_KEY, JOBE_SERVER_URL)
file_id = None
for d in data:
    check_file = jobe_extended.upload_file(join(path, 'tmp', 'base.sqlite3'))
    results = jobe_extended.execute_sql(join(path, 'tmp', 'base.sqlite3'), d['reference'], db_file_id=check_file)
    results = jobe_extended.execute_sql(join(path, 'tmp', 'base.sqlite3'), 'SELECT * FROM Trees', db_file_id=check_file)
    print(results)