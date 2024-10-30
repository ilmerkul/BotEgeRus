from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


kb_admin = ReplyKeyboardMarkup()
b1 = KeyboardButton('Добавить')
b2 = KeyboardButton('Удалить')
b3 = KeyboardButton('Изменить')
kb_admin.add(b1, b2, b3)