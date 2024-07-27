import plotly.express as px # Инструмент для работы с интерактивными графиками
import pandas as pd # Библиотека для работы с данными
def read_file(file_path): # Функция read_file_content считает содержимое файла по указанному пути file_path
    with open(file_path, 'rb') as file:
        return file.read() # вернет резуьтат, содержимое файла


def binary_to_features(binary_data): # Функция преобразования бинарных сигнатур в числовой
    return [int.from_bytes(b, byteorder='big') for b in binary_data]


def count_bits_in_file(data_from_list): # Функция подсчета бит = 1 и бит = 1 идущих подряд с конца файла и подряд идущих 0 с начала файла
    total_ones = sum(sum((byte >> i) & 1 for i in range(8)) for byte in data_from_list)
    # Подсчет количества подряд идущих единиц с конца файла
    ones_at_end = 0
    for byte in reversed(data_from_list):
        for i in range(8):
            if (byte >> i) & 1:
                ones_at_end += 1
            else:
                break
    zero_at_start = 0
    byte = data_from_list[0]
    for i in range(8):
        if not (byte << i) & 128:
            zero_at_start += 1
        else:
            break
    return [total_ones, ones_at_end, zero_at_start]


def data_for_analysis(list_data):
    return [count_bits_in_file(data) for data in list_data]

class MakeScatter:
    def __init__(self, data, labels):
        # Подготовка DataFrame
        self.data = pd.DataFrame(data, columns=['Total Ones', 'End Ones', 'Start Zeros'])
        self.data['Label'] = ['Вирус' if label == 1 else ('Подозрительный' if label == 2 else 'Нормальный') for label in labels]
        self.data['Start Zeros'] = self.data['Start Zeros'] + 2

    def show(self):
        # Создание графика
        fig = px.scatter(self.data, x='Total Ones', y='End Ones', size='Start Zeros', color='Label',
                         title='Визуализация Двоичных Данных (Интерактивно)',
                         labels={'Total Ones': 'Общее количество единиц', 'End Ones': 'Количество единиц в конце', 'Start Zeros': 'Условное значение нулей'},
                         color_discrete_map={'Нормальный':'green', 'Вирус':'red', 'Подозрительный':'blue'})
        # Отображение графика
        fig.show()

