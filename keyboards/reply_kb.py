from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# кнопка отправить контакт
def get_send_contact_button():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    bt = KeyboardButton('📱 Отправить контакт', request_contact=True)
    kb.add(bt)
    return kb
