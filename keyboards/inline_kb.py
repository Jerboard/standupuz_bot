from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from functions.utilits import get_weekend_date_list
from functions.data_func import get_popular_time_list, get_popular_place_list, get_active_events_list, \
    get_events_options, get_last_10_events


# первая админская клавиатура
def get_admin_kb():
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton ('🔄 Обновить таблицу', callback_data='update_google_table'),
        InlineKeyboardButton ('➕ Создать ивент', callback_data='new_event:new'),
        InlineKeyboardButton ('🖍 Изменить ивент', callback_data='edit_event_list'),
        InlineKeyboardButton ('📲 Сделать рассылку', callback_data='send_message_1'),
        InlineKeyboardButton ('🙋‍♂️ Текст приветствия', callback_data='edit_hello_text_1'),
        InlineKeyboardButton ('🚶 Войти как пользователь', callback_data='back_com_start'),
    )


# Отправка сообщений
def get_send_message_kb(data: dict):
    events = get_last_10_events()
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('🔙 Назад', callback_data='send_message_2')
    caption = '✔️ Всем пользователям' if data['everyone'] is True else 'Всем пользователям'
    bt2 = InlineKeyboardButton(caption, callback_data=f'send_message_3:everyone')
    kb.add(bt1, bt2)
    for event in events:
        if data['everyone'] is False and event["id"] in data['choice_list']:
            caption = f'✔️ {event["title"]} ({event["event_date"]})'
        else:
            caption = f'{event["title"]} ({event["event_date"]})'
        bt = InlineKeyboardButton(caption, callback_data=f'send_message_3:{event["id"]}')
        kb.insert(bt)
    bt4 = InlineKeyboardButton('📲 Отправить', callback_data=f'send_message_4')
    kb.add(bt4)
    return kb


# список ивентов
def get_events_list_kb():
    events = get_active_events_list()
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('Узнать о Standup.uz', callback_data='social_medias')
    kb.add(bt1)
    if events is not None:
        for event in events:
            if event['title'] is None:
                button_name = f'{event["date"]} {event["place"]}'
                bt = InlineKeyboardButton(button_name, callback_data=f'view_event:{event["id"]}')
            else:
                bt = InlineKeyboardButton(event['title'], callback_data=f'view_event:{event["id"]}')
            kb.add(bt)
    return kb


# ссылки на соцсети
def get_social_medias_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('Instagram', url='https://instagram.com/standup.uz?igshid=ZDdkNTZiNTM=')
    bt2 = InlineKeyboardButton('Telegram', url='https://t.me/StandUp_UZB')
    bt3 = InlineKeyboardButton('YouTube', url='https://www.youtube.com/channel/UCtDA0xLMJ76jg0vmdk7FZdw')
    bt4 = InlineKeyboardButton('🔙 Назад', callback_data='back_com_start')
    kb.add(bt1, bt2, bt3, bt4)
    return kb


# забронировать места
def get_book_kb(event_id):
    options = get_events_options(event_id)
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('🔙 Назад', callback_data='book_2:back')
    kb.add(bt1)
    for option in options:
        if option["empty_place"] > 0:
            caption = f'{option["name"]} ({option["empty_place"]})'
            bt = InlineKeyboardButton(caption, callback_data=f'book_1:{event_id}:{option["id"]}')
        else:
            caption = f'{option["name"]} (Мест нет)'
            bt = InlineKeyboardButton(caption, callback_data=f'book_1:not')

        kb.add(bt)
    return kb


# выбор свободных мест
def get_alert_1_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('Принял, далее', callback_data='book_2:1')
    bt2 = InlineKeyboardButton('🔙 Назад', callback_data='book_2:back')
    kb.add(bt1, bt2)
    return kb


# выбор свободных мест
def get_alert_2_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('Принял, далее', callback_data='book_3')
    bt2 = InlineKeyboardButton('🔙 Назад', callback_data='book_1:back')
    kb.add(bt1, bt2)
    return kb


# выбор свободных мест
def get_chioce_count_place_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    bt1 = InlineKeyboardButton('1', callback_data='book_4:1')
    bt2 = InlineKeyboardButton('2', callback_data='book_4:2')
    bt3 = InlineKeyboardButton('3', callback_data='book_4:3')
    bt4 = InlineKeyboardButton('4', callback_data='book_4:4')
    kb.row(bt1, bt2, bt3, bt4)
    return kb


# подсказка в отправке телефона
def get_sent_phone_kb(phone):
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton(f'{phone}', callback_data=f'book_5:{phone}')
    bt2 = InlineKeyboardButton('🔙 Назад', callback_data='book_3')
    if phone is not None:
        kb.add(bt1, bt2)
    else:
        kb.add(bt2)
    return kb


# подсказка в отправке имени
def get_sent_name_kb(name):
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton(f'{name[:24]}', callback_data=f'book_6:{name[:24]}')
    bt2 = InlineKeyboardButton('🔙 Назад', callback_data='book_4:back')
    kb.add(bt1, bt2)
    return kb


# подтвердить/отменить выбор мест
def get_accept_chioce_place_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('✅ Принять', callback_data=f'book_3:accept')
    bt2 = InlineKeyboardButton('☎️ Изменить номер', callback_data='book_change_number')
    bt3 = InlineKeyboardButton('❌ Отмена', callback_data='book_3:close')
    kb.add(bt1, bt2, bt3)
    return kb


# назад к подтверждению брони
def get_back_check_book_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('🔙Назад', callback_data='back_check_book')
    kb.add(bt1)
    return kb


# ============================================================
# изменение ивента
def get_edit_event_kb(type_event):
    kb = InlineKeyboardMarkup(row_width=2)
    bt1 = InlineKeyboardButton('🖍 Название', callback_data='edit_event_step_1:title')
    bt2 = InlineKeyboardButton('📅 Дата', callback_data='edit_event_step_1:date')
    bt3 = InlineKeyboardButton('⏰ Время', callback_data='edit_event_step_1:time')
    bt5 = InlineKeyboardButton('🫰 Места и опции', callback_data='edit_event_step_1:price')
    bt7 = InlineKeyboardButton('✅ Создать', callback_data='edit_event_accept')
    if type_event == 'new':
        kb.row(bt1).add(bt2, bt3, bt5).row(bt7)
    else:
        bt7 = InlineKeyboardButton('✅ Подтвердить', callback_data='edit_event_accept')
        kb.add(bt7)
    return kb


# предлагает выбрать время
def get_choisce_date_kb():
    date_list = get_weekend_date_list()
    kb = InlineKeyboardMarkup(row_width=2)
    for date in date_list:
        bt = InlineKeyboardButton(f'{date}', callback_data=f'edit_date:{date}')
        kb.insert(bt)
    bt_back = InlineKeyboardButton('🔙Назад', callback_data='back_edit_event')
    kb.add(bt_back)
    return kb


# предлагает выбрать время
def get_choisce_time_kb():
    times = get_popular_time_list()
    kb = InlineKeyboardMarkup(row_width=2)
    for time in times:
        bt = InlineKeyboardButton(f'{time[0]}', callback_data=f'edit_time {time[0]}')
        kb.insert(bt)
    bt_back = InlineKeyboardButton('🔙Назад', callback_data='back_edit_event')
    kb.add(bt_back)
    return kb


# предлагает выбрать место
# def get_choisce_place_kb():
#     places = get_popular_place_list()
#     kb = InlineKeyboardMarkup(row_width=1)
#     for place in places:
#         bt = InlineKeyboardButton(f'{place["name"]}', callback_data=f'edit_place:{place["id"]}')
#         kb.insert(bt)
#     bt_back = InlineKeyboardButton('🔙Назад', callback_data='back_edit_event')
#     kb.add(bt_back)
#     return kb


# предлагает выбрать время
def get_choisce_tariff_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    bt_back = InlineKeyboardButton('🔙Назад', callback_data='back_edit_event')
    kb.add(bt_back)
    return kb


# 10 последних ивентов
def get_10_last_event_kb():
    events = get_last_10_events()
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('🔙Назад', callback_data='back_admin_start')
    kb.add(bt1)
    for event in events:
        is_active = 'актив.' if event['is_active'] == 1 else 'не актив.'
        bt = InlineKeyboardButton(f'{event["title"]} ({is_active})', callback_data=f'new_event:edit:{event["id"]}')
        kb.insert(bt)
    return kb


# переключение активный неактивный ивент
def update_is_active_event_kb(is_active, event_id):
    kb = InlineKeyboardMarkup(row_width=1)
    if is_active == '0':
        bt1 = InlineKeyboardButton('❌Неактивный', callback_data=f'event_active_status:1:{event_id}')
    else:
        bt1 = InlineKeyboardButton('✅Активный', callback_data=f'event_active_status:0:{event_id}')
    kb.add(bt1)
    return kb


# измеение приветственного текста
def get_edit_hello_text_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    bt1 = InlineKeyboardButton('🔙 Назад', callback_data='send_message_2')
    bt2 = InlineKeyboardButton('✅ Подтвердить', callback_data='edit_hello_text_3')
    kb.add(bt1, bt2)
    return kb
