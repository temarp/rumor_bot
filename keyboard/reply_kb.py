from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reply_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мои мероприятия'), KeyboardButton(text='Изменить дорогу/подразделение')],
        [KeyboardButton(text='Прошедшие мероприятия'), KeyboardButton(text='Будущие мероприятия')]
    ], resize_keyboard=True
)

