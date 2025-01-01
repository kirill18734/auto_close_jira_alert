# import time
#
# import keyboard
# from threading import Event
# import subprocess
# import pyautogui
# from send_to_telegram_email.send_to_TG_email import send_to_telegram
#
# def wait_for_keypress(timeout=30):
#     # Событие для синхронизации
#     sync_event = Event()
#
#     # Переменная для хранения состояния нажатия клавиши
#     key_pressed = [False]
#
#     def on_key_press(e):
#         # Обновляем состояние нажатия клавиши и устанавливаем событие
#         key_pressed[0] = True
#         sync_event.set()
#
#     # Регистрируем обработчик нажатия клавиши
#     keyboard.on_press(on_key_press)
#
#     # Ждем события или тайм-аута
#     sync_event.wait(timeout)
#
#     # Отменяем регистрацию обработчика
#     keyboard.unhook_all()
#
#     return key_pressed[0]
# def result_pressed_keywoard():
#     # Пример использования функции
#     if wait_for_keypress(30):
#         return True
#     else:
#         return False
# result_key= result_pressed_keywoard()
# def mouse_activity_check(timeout=20):
#     initial_x, initial_y = pyautogui.position()
#     start_time = time.time()
#
#     while True:
#         current_x, current_y = pyautogui.position()
#
#         if (current_x, current_y) != (initial_x, initial_y):
#             return True
#
#         if time.time() - start_time > timeout:
#             return False
#
#         time.sleep(0.1)
# #
# #
#
# def position_mouse():
#     # Инициализация начальных значений
#     prev_x, prev_y = pyautogui.position()
#     last_movement_time = time.time()
#
#     result = False
#     while True:
#         x, y = pyautogui.position()
#         current_time = time.time()
#
#         if (x, y) != (prev_x, prev_y):
#
#             positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
#             print(positionStr)
#             prev_x, prev_y = x, y
#             last_movement_time = current_time
#
#         elif current_time - last_movement_time > 2:
#             positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
#             print(positionStr + ' (Мышь не двигается)')
#             last_movement_time = current_time
#
#         # Проверка активности мыши за последние 10 секунд
#         if not mouse_activity_check(10):
#             break
#
#         else:
#             result = True
#             break
#
#         time.sleep(0.1)
#     return result
#
# result_mouse  = position_mouse()
#
#
# script_path = r'''
# $activeUsers = quser
# if ($activeUsers -match "fokinkv" -and $activeUsers -match "Активно") {
#     $result = "True"
# } else {
#     $result = "False"
# }
# Write-Output $result
# '''
#
# # Выполнение PowerShell скрипта
# completed_process = subprocess.run(['powershell', '-Command', script_path],
#                                    capture_output=True, text=True, encoding='utf-8')
#
# # Вывод результата
# result = completed_process.stdout.strip()
# def result_acitve():
#     if result and result_key and result_mouse:
#         return True
#     else:
#         return False
# # send_to_telegram(f'Активность на пк: {result}\nНажатие клавиш: {result_key}\nМышка: {result_mouse}')