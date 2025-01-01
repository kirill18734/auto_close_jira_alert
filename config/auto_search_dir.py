import json
import os


# Объединенная функция для автоматического поиска файла
def find_file_in_project(filename, search_path):
    for root_dir, dirs, files in os.walk(search_path):
        for cur_file in files:
            if cur_file == filename or (
                    cur_file.lower() == filename.lower() and
                    cur_file[0].istitle()):  # два пробела перед символом '#'
                return os.path.join(root_dir, cur_file)


# Путь до текущей папки
path_to_current_folder = os.path.dirname(os.path.realpath(__file__))

# Путь до папки проекта
path_to_project_folder = os.path.dirname(path_to_current_folder)
# Название папки проекта
project_folder_name = os.path.basename(path_to_project_folder)

# находим основной запускающий файл
path_to_main = find_file_in_project(f'{project_folder_name}.py',
                                    path_to_project_folder)

# Ищем файл query.txt и получаем его путь
path_to_query_txt = find_file_in_project('query.sql',
                                         path_to_project_folder)
# Ищем файл python.exe
path_to_python_exe = find_file_in_project('python.exe',
                                          path_to_project_folder)
# Читаем содержимое файла
with open(path_to_query_txt, 'r', encoding='utf-8') as file:
    connectionString = file.read()

# Ищем файл config.json и получаем его путь
path_to_config_json = find_file_in_project('config.json',
                                           path_to_project_folder)
# Преобразуем содержимое файла
with open(path_to_config_json, 'r', encoding='utf-8') as file:
    data_config = json.load(file)
