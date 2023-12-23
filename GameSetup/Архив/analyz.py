import pandas as pd

# Загрузка данных из файла
log_df = pd.read_csv('log1.log', sep='|', header=0, skipinitialspace=False)

# Преобразование столбцов с суммами и номерами счетов в соответствующий формат
log_df['Amount'] = log_df['Amount'].astype(float)
log_df['SourceAccount'] = log_df['SourceAccount'].astype(int)
log_df['DestinationAccount'] = log_df['DestinationAccount'].astype(int)

# Создание первой таблицы с группировкой по SourceAccount и DestinationAccount
total_transfers_source_destination = log_df.groupby(['SourceAccount', 'DestinationAccount'])['Amount'].sum().reset_index()

# Переименование столбца для ясности
total_transfers_source_destination.rename(columns={'Amount': 'TotalTransferred'}, inplace=True)

# Создание второй таблицы с группировкой по DestinationAccount
total_transfers_destination = log_df.groupby('DestinationAccount')['Amount'].sum().reset_index()

# Переименование столбца для ясности
total_transfers_destination.rename(columns={'Amount': 'TotalReceived'}, inplace=True)

# Вывод первой таблицы
print("Первая таблица:")
print(total_transfers_source_destination)

# Вывод второй таблицы
print("\nВторая таблица:")
print(total_transfers_destination)
