# Импорт библиотеки pyodbc для работы с базами данных
import pyodbc

# Функция для выполнения SQL запроса
def execute_sql(sqlquery, connectionString):

    # Создание соединения с базой данных
    connection = pyodbc.connect(connectionString)
    # Установка таймаута одной минуты
    connection.timeout = 60

    # Создание объекта курсора, с помощью которого осуществляется работа с БД
    cursor = connection.cursor()

    # Выполнение SQL-запроса
    cursor.execute(sqlquery)

    # Получение описаний колонок
    columns = cursor.description

    # Генерация результата в виде списка словарей, где каждый словарь представляет отдельную строку,
    # а ключи соответствуют названиям колонок
    result = [
        {columns[index][0]: column for index, column in enumerate(value)}
        for value in cursor.fetchall()
    ]

    # Закрытие курсора
    cursor.close()

    # Удаление объекта курсора
    del cursor

    # Закрытие соединения с БД
    connection.close()

    # Возвращение результата
    return result

