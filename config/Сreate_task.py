import subprocess
from auto_search_dir import data_config, path_to_main, path_to_python_exe, \
    project_folder_name
from datetime import datetime
import os
import socket
import win32security
import getpass

# получем текущего пользователя на сервере
username = getpass.getuser()
# получаем id текущего пользователя на сервере
user_sid = win32security.LookupAccountName(None, username)[0]
sid_string = win32security.ConvertSidToStringSid(user_sid)

# Получение имени пользователя
username = os.getlogin()
# Получение имени хоста (сервера)
hostname = socket.gethostname()

# текущая дата
current_datetime = datetime.now()
# дополнительные парметры для нужного отоброжения
formatted_datetime_1 = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")
# дополнительные парметры для нужного отоброжения
formatted_datetime_2 = current_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")


def repeat_days():
    days = []
    # ежедневное задание
    if data_config['Task_Scheduler']['Triggers']['daily'] != 'False':
        return f'-Daily'
    # еженедельное задание
    elif data_config['Task_Scheduler']['Triggers']['weekly'] != 'False':
        for day, value in data_config['Task_Scheduler']['Triggers'][
            'weekly_'].items():
            if value == "True":
                days.append(day)

    else:
        return ''
    # Используем "-DaysOfWeek", а не "-Days", и перечисляем дни недели без запятых
    # Названия дней недели должны быть на английском языке и с большой буквы
    return f"-DaysOfWeek {','.join(days)} -Weekly"


def repeat():
    # почесовое повторение задания
    if data_config['Task_Scheduler']['Triggers']['Repetion']['Hours'] != 0:
        return f'''Hours {data_config['Task_Scheduler']['Triggers']['Repetion']['Hours']}'''
    # поменутное повторение
    elif data_config['Task_Scheduler']['Triggers']['Repetion']['Minutes'] != 0:
        return f'''Minutes {data_config['Task_Scheduler']['Triggers']['Repetion']['Minutes']}'''


# основной скрипт для запуска задания
script_path = fr'''\\
# Создаем триггер задания, который устанавливает повторение задания, начиная с 01:00 (начальное время), и повторяет это каждый интервал времени, возвращаемый функцией repeat(). Задание повторяется на протяжении максимального значения TimeSpan. 
$t2 = New-ScheduledTaskTrigger -Once -At 01:00 `
        -RepetitionInterval (New-TimeSpan -{repeat()}) ` 
        -RepetitionDuration (([TimeSpan]::MaxValue))
# Создаем новый триггер с заданным временем, представленным переменной formatted_datetime_1, и днями повторения, которые определяет функция repeat_days(). Время повторения устанавливается на значение триггера $t2.
$Time = New-ScheduledTaskTrigger -At "{formatted_datetime_1}" {repeat_days()} 
$Time.Repetition = $t2.Repetition
# Определяем пользователя задачи, который будет "СИСТЕМА".
$User = "SYSTEM"
# Определяем действие задания, которое представляет выполнение скрипта PowerShell, запускающего Python скрипт, определенный переменной path_to_main.
$PS = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "& '{path_to_python_exe}' '{path_to_main}'"
# Определяем описание задания, используя данные из конфигурации.
$Description  = '{data_config['ServiceMode']['AlertName']}                                                                                                                                                                                                                                                        
{data_config['ServiceMode']['url_monitoring']}'
# Устанавливаем некоторые параметры настроек задания: задание будет запускаться, только если система простаивает, ожидание перед запуском при простое составляет 2 минуты, истечение ожидания - 2,5 минуты, задание разрешено запускать на батарейках, задание не останавливается при окончании простоя и другие.
$Stset = New-ScheduledTaskSettingsSet -RunOnlyIfIdle -IdleDuration 00:02:00 -IdleWaitTimeout 02:30:00 -AllowStartIfOnBatteries -DontStopOnIdleEnd -RestartInterval 00:02:00 -RestartCount 2 -StartWhenAvailable
# Задание не останавливается, если переходит на батарейное питание.
$Stset.StopIfGoingOnBatteries = $False
# Регистрируем задание с указанным именем проекта, описанием, триггером, пользователем, действием, настройками и другими параметрами.
Register-ScheduledTask -TaskName "{project_folder_name}" -Description $Description -Trigger $Time -User $User -Action $PS -RunLevel Highest -Settings $Stset -TaskPath "{data_config['Task_Scheduler']['path_task']}"
'''

# Запуск скрипта PowerShell
# Если используется PowerShell Core, замените 'powershell' на 'pwsh'
completed_process = subprocess.run(['powershell', script_path],
                                   capture_output=True)

# Вывод результатов
print('STDOUT:', completed_process.stdout)
print('STDERR:', completed_process.stderr)
# успешное создание , пример, если в самом верху вывода есть начало строки :
# STDOUT: b'\r\nTaskPath                                       TaskName                          State     \r\n--------                                       --------                          -----     \r\n\\GSA\\

# значит задача успешно создана
