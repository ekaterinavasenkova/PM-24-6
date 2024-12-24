import csv

def load_table_from_csv(filename):
    table = {}
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for key, value in row.items():
                if key not in table:
                    table[key] = []
                table[key].append(value)
    return table
def save_table_to_csv(table, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=table.keys())
        writer.writeheader()
        for i in range(len(list(table.values())[0])):
            writer.writerow({key: table[key][i] for key in table})
import pickle

def load_table_from_pickle(filename):
    with open(filename, 'rb') as file:
        table = pickle.load(file)
    return table
def save_table_to_pickle(table, filename):
    if not isinstance(table, dict):
        raise ValueError("Входные данные должны быть словарем")   
    with open(filename, 'wb') as file:
        pickle.dump(table, file)
def save_table_to_text_file(table, filename):
    """Сохраняет таблицу в текстовом файле в удобочитаемом формате."""
    if not isinstance(table, dict):
        raise ValueError("Входные данные должны быть словарем.")
    
    with open(filename, 'w', encoding='utf-8') as file:
        for key in table:
            file.write(f"{key}: {', '.join(table[key])}\n")


class Table:
    def __init__(self, data):
        """Конструктор, принимающий данные в виде словаря столбцов: [значения]"""
        if not data:
            raise ValueError("Таблица не может быть пустой.")
        self.table = data
        self.column_types = {col: str for col in data}  # По умолчанию все столбцы типа str

    def _check_column(self, column):
        """Проверка, существует ли столбец по индексу или имени"""
        if isinstance(column, int):  # Проверка по номеру столбца
            if column < 0 or column >= len(self.table):
                raise IndexError("Неверный индекс столбца.")
            column_name = list(self.table.keys())[column]
        elif isinstance(column, str):  # Проверка по имени столбца
            if column not in self.table:
                raise KeyError(f"Столбца с именем {column} не существует.")
            column_name = column
        else:
            raise TypeError("Столбец должен быть либо числом, либо строкой.")
        return column_name

    def get_rows_by_number(self, start, stop=None, copy_table=False):
        """Получение строк по номеру, можно указать диапазон (start, stop)."""
        if stop is None:
            stop = start + 1
        
        # Проверка на корректность индексов
        if start < 0 or stop > len(next(iter(self.table.values()))):
            raise IndexError("Некорректные номера строк.")
        
        # Получаем подтаблицу по номеру строк
        rows = {col: values[start:stop] for col, values in self.table.items()}
        
        if copy_table:
            return Table(rows)  # Возвращаем копию таблицы
        else:
            return rows  # Возвращаем представление, работающее с исходными данными

    def get_rows_by_index(self, *vals, copy_table=False):
        """Получение строк, где первый столбец совпадает с переданными значениями."""
        if not vals:
            raise ValueError("Не переданы значения для поиска.")
        
        # Получаем значения первого столбца
        first_column = next(iter(self.table.values()))  # Предполагаем, что первый столбец — это столбец с индексами
        matching_rows = {col: [] for col in self.table}
        
        # Ищем строки, где значение первого столбца совпадает с переданными значениями
        for i, value in enumerate(first_column):
            if value in vals:
                for col in self.table:
                    matching_rows[col].append(self.table[col][i])
        
        if not matching_rows[next(iter(self.table))]:
            raise ValueError(f"Не найдены строки с указанными значениями {vals}.")

        if copy_table:
            return Table(matching_rows)
        else:
            return matching_rows

    def get_column_types(self, by_number=True):
        """Возвращает типы значений в столбцах."""
        if by_number:
            return {i: self.column_types[col] for i, col in enumerate(self.table)}
        else:
            return self.column_types

    def set_column_types(self, types_dict, by_number=True):
        """Устанавливает типы данных для столбцов."""
        if not isinstance(types_dict, dict):
            raise TypeError("types_dict должен быть словарем.")
        
        for col, t in types_dict.items():
            if not isinstance(col, (str, int)):
                raise TypeError("Ключи словаря должны быть либо строками, либо числами.")
            if t not in (int, float, bool, str):
                raise ValueError(f"Неверный тип данных: {t}. Допустимые типы: int, float, bool, str.")
            column_name = self._check_column(col)
            self.column_types[column_name] = t

    def get_values(self, column=0):
        """Получение значений столбца по номеру или имени."""
        column_name = self._check_column(column)
        values = self.table[column_name]
        return [self._convert_value(val, column_name) for val in values]

    def get_value(self, column=0):
        """Получение одного значения из столбца (представление таблицы с одной строкой)."""
        column_name = self._check_column(column)
        values = self.table[column_name]
        if not values:
            raise ValueError("Столбец пуст.")
        return self._convert_value(values[0], column_name)

    def set_values(self, values, column=0):
        """Установка значений для столбца (список значений)."""
        column_name = self._check_column(column)
        if len(values) != len(self.table[column_name]):
            raise ValueError("Количество значений не соответствует количеству строк.")
        self.table[column_name] = [self._convert_value(val, column_name) for val in values]

    def set_value(self, value, column=0):
        """Установка одного значения для столбца (представление таблицы с одной строкой)."""
        column_name = self._check_column(column)
        self.table[column_name][0] = self._convert_value(value, column_name)

    def _convert_value(self, value, column_name):
        """Конвертирует значение в нужный тип данных столбца."""
        column_type = self.column_types[column_name]
        if column_type == int:
            return int(value)
        elif column_type == float:
            return float(value)
        elif column_type == bool:
            return bool(value)
        elif column_type == str:
            return str(value)
        else:
            return value  # если тип не задан, возвращаем как есть

    def print_table(self):
        """Вывод таблицы в консоль."""
        headers = list(self.table.keys())
        print(" | ".join(headers))
        num_rows = len(next(iter(self.table.values())))
        for i in range(num_rows):
            row = [str(self.table[col][i]) for col in headers]
            print(" | ".join(row))
# Дополнительное задание 3
def concat(table1, table2):
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")

    combined_table = {}
    for key in table1.keys():
        combined_table[key] = table1[key] + table2[key]  # Склеиваем списки значений

    return combined_table


def split(table, row_number):
    if row_number < 0 or row_number > len(list(table.values())[0]):
        raise ValueError("Номер строки должен быть в пределах от 0 до длины таблицы.")

    first_part = {}
    second_part = {}

    for key in table.keys():
        first_part[key] = table[key][:row_number]  # Первая часть
        second_part[key] = table[key][row_number:]  # Вторая часть

    return first_part, second_part
# Дополнительное задание 7    
def eq(table1, table2):
    """Сравнивает значения двух таблиц на равенство."""
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")
    bool_list = []
    for i in range(len(list(table1.values())[0])):
        row_eq = all(table1[key][i] == table2[key][i] for key in table1.keys())
        bool_list.append(row_eq)
    return bool_list

def gr(table1, table2):
    """Сравнивает значения в первой таблице с значениями во второй на больше."""
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")
    bool_list = []
    for i in range(len(list(table1.values())[0])):
        row_gr = all(table1[key][i] > table2[key][i] for key in table1.keys())
        bool_list.append(row_gr)
    return bool_list

def ls(table1, table2):
    """Сравнивает значения в первой таблице с значениями во второй на меньше."""
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")
    bool_list = []
    for i in range(len(list(table1.values())[0])):
        row_ls = all(table1[key][i] < table2[key][i] for key in table1.keys())
        bool_list.append(row_ls)
    return bool_list

def ge(table1, table2):
    """Сравнивает значения в первой таблице с значениями во второй на больше или равно."""
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")
    bool_list = []
    for i in range(len(list(table1.values())[0])):
        row_ge = all(table1[key][i] >= table2[key][i] for key in table1.keys())
        bool_list.append(row_ge)
    return bool_list

def le(table1, table2):
    """Сравнивает значения в первой таблице с значениями во второй на меньше или равно."""
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")
    bool_list = []
    for i in range(len(list(table1.values())[0])):
        row_le = all(table1[key][i] <= table2[key][i] for key in table1.keys())
        bool_list.append(row_le)
    return bool_list

def ne(table1, table2):
    """Сравнивает значения в первой таблице с значениями во второй на не равно."""
    if table1.keys() != table2.keys():
        raise ValueError("Таблицы должны иметь одинаковые ключи (названия столбцов).")
    bool_list = []
    for i in range(len(list(table1.values())[0])):
        row_ne = all(table1[key][i] != table2[key][i] for key in table1.keys())
        bool_list.append(row_ne)
    return bool_list

def filter_rows(bool_list, table, copy_table=False):
    """Фильтрует строки таблицы на основе булевого списка."""
    if len(bool_list) != len(list(table.values())[0]):
        raise ValueError("Длина bool_list должна соответствовать количеству строк в таблице.")
    
    filtered_table = {key: [] for key in table.keys()}
    for i in range(len(bool_list)):
        if bool_list[i]:
            for key in table.keys():
                filtered_table[key].append(table[key][i])
    
    return filtered_table if copy_table else {key: table[key][:] for key in table.keys()}
# Дополнительное задание 6
class Table:
    def __init__(self, data=None):
        self.data = data if data else {}


    def add(self, column1, column2, result_column):
        """Сложение значений из двух столбцов и сохранение результата в новый столбец."""
        self._binary_operation(column1, column2, result_column, lambda x, y: x + y)

    def sub(self, column1, column2, result_column):
        """Вычитание значений из двух столбцов и сохранение результата в новый столбец."""
        self._binary_operation(column1, column2, result_column, lambda x, y: x - y)

    def mul(self, column1, column2, result_column):
        """Умножение значений из двух столбцов и сохранение результата в новый столбец."""
        self._binary_operation(column1, column2, result_column, lambda x, y: x * y)

    def div(self, column1, column2, result_column):
        """Деление значений из двух столбцов и сохранение результата в новый столбец."""
        self._binary_operation(column1, column2, result_column, lambda x, y: x / y if y != 0 else float('nan'))

    def _binary_operation(self, column1, column2, result_column, operation):
        """Общая функция для выполнения бинарных операций."""
        if column1 not in self.data or column2 not in self.data:
            raise ValueError("Один из указанных столбцов не существует.")

        # Проверка целостности значений в столбцах
        values1 = self.get_values(column1)
        values2 = self.get_values(column2)

        if len(values1) != len(values2):
            raise ValueError("Длина столбцов не совпадает.")

        # Выполняем операцию для каждой строки
        result = []
        for val1, val2 in zip(values1, values2):
            if val1 is None or val2 is None:
                result.append(None)  # Результат будет None, если одно из значений пустое
            elif not isinstance(val1, (int, float, bool)) or not isinstance(val2, (int, float, bool)):
                raise TypeError("Недопустимый тип данных. Ожидаются int, float или bool.")
            else:
                result.append(operation(val1, val2))

        self.set_values(result, result_column)
