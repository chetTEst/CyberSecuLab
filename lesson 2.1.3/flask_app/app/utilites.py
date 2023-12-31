def restore_sql_query(query_string, injection=False):
    translation = {
        "положитьв": "INSERT INTO",
        "ПоложитьВ": "INSERT INTO",
        "ПОЛОЖИТЬВ": "INSERT INTO",
        "значение": "VALUES",
        "ЗНАЧЕНИЕ": "VALUES",
        "ВЫБРАТЬ": "SELECT",
        "выбрать": "SELECT",
        "ИзХранилища": "FROM",
        "изхранилища": "FROM",
        "где": "WHERE",
        "ГДЕ": "WHERE",
        "ОБНОВИТЬ": "UPDATE",
        "обновить": "UPDATE",
        "установить": "SET",
        "УСТАНОВИТЬ": "SET",
        "УДАЛИТЬ": "DELETE",
        "Удалить": "DELETE",
        "Запись": "id",
        "Тип": "type",
        "Съедобное": "fruitful",
        "Плод": "fruit",
        "Урожай": "harvest",
        "Год": "year",
        "Да": "1",
        "Нет": "0",
        "Деревья": "Trees",
        # Дополните словарь для других команд
    }
    if injection:
        query_string = query_string.replace('[ТЕКСТ_ЗАПРОСА]', injection)
    for key, value in translation.items():
        query_string = query_string.replace(key, value)
    return query_string