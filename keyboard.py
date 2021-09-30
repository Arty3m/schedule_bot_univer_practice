from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_monday = KeyboardButton('Понедельник')
btn_tuesday = KeyboardButton('Вторник')
btn_wednesday = KeyboardButton('Среда')
btn_thursday = KeyboardButton('Четверг')
btn_friday = KeyboardButton('Пятница')
btn_saturday = KeyboardButton('Суббота')

choosing_day = ReplyKeyboardMarkup(resize_keyboard=True).add(btn_monday).add(btn_tuesday).add(btn_wednesday).add(
    btn_thursday).add(btn_friday).add(btn_saturday)
