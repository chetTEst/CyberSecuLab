def restore_sql_query(query_string):
    translation = {
        "положив": "INSERT INTO",
        "ПоложиВ": "INSERT INTO",
        "значение": "VALUES",
        "ЗНАЧЕНИЕ": "VALUES",
        "ВЫБЕРИ": "SELECT",
        "выбери": "SELECT",
        "ИзХранилища": "FROM",
        "изхранилища": "FROM",
        "Где": "WHERE",
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

    for key, value in translation.items():
        query_string = query_string.replace(key, value)

    return query_string