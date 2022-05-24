from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

btn_monday = KeyboardButton('/Понедельник')
btn_tuesday = KeyboardButton('/Вторник')
btn_wednesday = KeyboardButton('/Среда')
btn_thursday = KeyboardButton('/Четверг')
btn_friday = KeyboardButton('/Пятница')
btn_saturday = KeyboardButton('/Суббота')

choosing_day = ReplyKeyboardMarkup(resize_keyboard=True)
choosing_day.row(btn_monday, btn_tuesday)
choosing_day.row(btn_wednesday, btn_thursday)
choosing_day.row(btn_friday, btn_saturday)
