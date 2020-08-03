# import pyautogui
# import pydirectinput
#
# import time
#
# PressTime = 0.5
#
# keys_list = [
#     'a','b','x','y','q','w','e','s','4','8','6','2','l','k','r','t','u','d','p',
#     '1', '3', '7', '9'
# ]
#
# def press_key(keys):
#     if len(keys) > 10:
#         return
#     for key in keys:
#         if key in keys_list:
#             if key in ['1','2','3','4','6','7','8','9',]:
#                 if key in ['1', '3', '7', '9']:
#                     if key == '1':
#                         key1 = '4'
#                         key2 = '2'
#                     elif key == '3':
#                         key1 = '2'
#                         key2 = '6'
#                     elif key == '7':
#                         key1 = '4'
#                         key2 = '8'
#                     else:  # key == '9':
#                         key1 = '8'
#                         key2 = '6'
#                     pydirectinput.keyDown(key1)
#                     pydirectinput.keyDown(key2)
#                     time.sleep(PressTime)
#                     pydirectinput.keyUp(key1)
#                     pydirectinput.keyUp(key2)
#                 else:
#                     pydirectinput.keyDown(key)
#                     time.sleep(PressTime)
#                     pydirectinput.keyUp(key)
#             else:
#                 pydirectinput.press(key)
#                 time.sleep(0.2)
#             # print(key)
#
# if __name__ == '__main__':
#     while(1):
#         keys = input()
#         press_key(keys)