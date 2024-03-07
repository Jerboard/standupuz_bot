import sqlite3
import logging

from datetime import datetime
from aiogram.types import MessageEntity

from config import db_path
from create_bot import tz


# создаёт список словарей
def hand_query_result(columns, result):
    if len(result) > 0:
        results = []
        for row in result:
            results.append(dict(zip(columns, row)))
        return results
    else:
        return None


# добавляет мероприятие
def add_new_event(data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = 'insert into ' \
            'events(add_time, title, event_date, event_time, text, photo_id, is_active, page_id) ' \
            'values(?, ?, ?, ?, ?, ?, ?, ?)'
    add_time = datetime.now(tz).strftime('%Y-%m-%d %H:%M')
    items = (add_time, data['title'], data['date'], data['time'], data['text'],  data['photo_id'], 1, data['page_id'])
    cur.execute(query, items)
    conn.commit()
    event_id = cur.lastrowid
    row_number = 5
    for tariff in data['tariffs']:
        cell = f'B{row_number}'
        row_number += 1
        items = (event_id, tariff[0], tariff[1], tariff[1], cell)
        cur.execute('insert into events_options(event_id, name, empty_place, all_place, cell) '
                    'values(?, ?, ?, ?, ?)', items)
        conn.commit()

    for entity in data['entities']:
        if entity['type'] == 'custom_emoji':
            items = (event_id, entity['type'], entity['offset'], entity['length'], entity['custom_emoji_id'])
        else:
            items = (event_id, entity['type'], entity['offset'], entity['length'], entity['url'])
        cur.execute('insert into entities(event_id, type, offset, length, url) values(?, ?, ?, ?, ?)', items)
        conn.commit()
    cur.close()
    return event_id


# обновить медиа мероприятия
def update_event_cover(data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = 'update events set text = ?, photo_id = ? where id = ?'
    items = (data['text'],  data['photo_id'], data['event_id'])
    cur.execute(query, items)
    conn.commit()

    cur.execute('delete from entities where event_id = ?', (data['event_id'], ))
    conn.commit()

    for entity in data['entities']:
        items = (data['event_id'], entity['type'], entity['offset'], entity['length'], entity['url'])
        cur.execute('insert into entities(event_id, type, offset, length, url) values(?, ?, ?, ?, ?)', items)
        conn.commit()
    cur.close()


# обновляет мероприятие
def update_event(is_active: bool, title: str, date: str, time: str, page_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = 'update events set is_active = ?, title = ?, event_date = ?, event_time = ? where page_id = ?'
    items = (is_active, title, date, time, page_id)
    cur.execute(query, items)
    conn.commit()


# удаляет все опции ивента
def del_all_event_option(event_id: int):
    conn = sqlite3.connect (db_path)
    cur = conn.cursor ()
    cur.execute('delete from events_options where event_id = ?', (event_id,))
    conn.commit()
    cur.close ()


# добавляет опцию
def add_option(event_id: int, title: str, empty_place: int, all_place: int, cell: str):
    conn = sqlite3.connect (db_path)
    cur = conn.cursor ()
    items = (event_id, title, empty_place, all_place, cell)
    cur.execute(
        'insert into events_options(event_id, name, empty_place,all_place, cell) values(?, ?, ?, ?, ?)', items)
    conn.commit()
    cur.close()


# список активных ивентов
def get_active_events_list():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = 'select * from events where is_active = 1'
    result_list = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]
    cur.close()
    results = hand_query_result(columns, result_list)
    return results


# 10 последних ивентов
def get_last_10_events():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = 'select * from events order by id desc limit 10'
    result_list = cur.execute(query).fetchall()

    columns = [column[0] for column in cur.description]
    cur.close()
    results = hand_query_result(columns, result_list)
    return results


# данные по ивенту
def get_event_info(event_id: int, on_page_id: bool = False) -> dict:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    if on_page_id:
        query = 'select * from events where page_id = ?'
    else:
        query = 'select * from events where id = ?'

    result = cur.execute(query, (event_id,)).fetchone()
    columns = [column[0] for column in cur.description]
    result_dict = dict(zip(columns, result))
    cur.close()
    return result_dict


# вложения ивента
def get_entities(event_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    results = cur.execute('select type, offset, length, url from entities where event_id = ? ',
                          (event_id,)).fetchall()
    cur.close()
    entities = []
    for result in results:
        if result[0] == 'custom_emoji':
            entity = MessageEntity(type=result[0], offset=result[1], length=result[2], custom_emoji_id=result[3])
        else:
            entity = MessageEntity(type=result[0], offset=result[1], length=result[2], url=result[3])
        entities.append(entity)

    return entities


# список опций на мероприятие
def get_events_options(event_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    result_list = cur.execute('select * from events_options where event_id = ? ', (event_id,)).fetchall()
    columns = [column[0] for column in cur.description]
    cur.close()
    results = hand_query_result(columns, result_list)
    return results


# список опций на мероприятие
def get_option_info(option_id: int, event_id: int, option_name: str):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    result = cur.execute('select * from events_options where id = ?', (option_id,)).fetchone()
    if not result:
        result = cur.execute (
            'select * from events_options where event_id = ? and name = ?', (option_id,)).fetchone ()

    if result:
        columns = [column[0] for column in cur.description]
        result_dict = dict(zip(columns, result))
    else:
        result_dict = {}
    cur.close()
    return result_dict


# возвращает инфо
def get_info():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    result = cur.execute('select * from info').fetchone()
    columns = [column[0] for column in cur.description]
    result_dict = dict(zip(columns, result)) if result is not None else None
    cur.close()
    return result_dict


# добавляет пользователя
def add_user(user_id, full_name, username):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    user = cur.execute('select * from users where user_id = ?', (user_id,)).fetchone()
    if user is None:
        query = 'insert into users(user_id, full_name, username, first_visit) values(?, ?, ?, ?)'
        now = datetime.now(tz).date()
        items = (user_id, full_name, username, now)
        cur.execute(query, items)
        conn.commit()
    cur.close()


# добавляет пользователя
def get_user_info(user_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    user = cur.execute('select * from users where user_id = ?', (user_id,)).fetchone()
    columns = [column[0] for column in cur.description]
    result_dict = dict(zip(columns, user)) if user is not None else None
    cur.close()
    return result_dict


# обновляет номер телефона
def update_user_phone(user_id, phone):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('update users set phone = ? where user_id = ?', (phone, user_id))
    conn.commit()
    cur.close()


# добавляет заказ
def add_new_order(user_id, phone, event_id, option, count_place, page_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    date = datetime.now(tz).date()
    query = 'insert into orders(date, user_id, phone, event_id, option, count_place, page_id) ' \
            'values(?, ?, ?, ?, ?, ?, ?)'
    items = (date, user_id, phone, event_id, option, count_place, page_id)
    cur.execute(query, items)
    order_id = cur.lastrowid
    conn.commit()
    cur.close()
    return order_id


# добавляет заказ
def update_count_option(option_id, count_place: int):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    items = (count_place, option_id)
    cur.execute('update events_options set empty_place = empty_place - ? where id = ?', items)
    conn.commit()

    result = cur.execute('select * from events_options where id = ?', (option_id,)).fetchone()
    columns = [column[0] for column in cur.description]
    result_dict = dict(zip(columns, result))
    cur.close()
    return result_dict


# отмечает заказ как записаный
def make_order_in_table(order_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('update orders set in_table = 1 where id = ?', (order_id,))
    conn.commit()
    cur.close()


# отмечает заказ как неактивный
def make_event_inactive_by_id(event_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('update events set is_active = 0 where event_id = ?', (event_id,))
    conn.commit()
    cur.close()


# Список получателей сообщения
def get_send_users(everyone, choice_list):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    users = set()
    if everyone is True:
        result = cur.execute('select user_id from users').fetchall()
        for user in result:
            users.add(user[0])
    else:
        for event_id in choice_list:
            result = cur.execute('select distinct user_id from orders where event_id = ?', (str(event_id),))
            for user in result:
                users.add(user)
    cur.close()

    return users


# ===========================================================================================
# выбирает 6 популярных вариантов времени
def get_popular_time_list():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    results = cur.execute('select event_time, count(id) from events group by 1 order by count(id) limit 6').fetchall()
    cur.close()
    return results


# выбирает 6 популярных вариантов времени
def get_popular_place_list():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    results = cur.execute('select place, count(id) from events group by 1 order by count(id) limit 6').fetchall()
    places = []
    for result in results:
        place_id = cur.execute('select id from events where place = ? limit 1', (result[0],)).fetchone()
        places.append({'name': result[0], 'id': place_id[0]})
    cur.close()
    return places


# меняет стандартные тексты
def update_info_texts(text_1: str, text_2: str, text_3: str, page_id: int = None):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    if page_id is None:
        cur.execute('update info set text_1 = ?, text_2 = ?, text_3 = ?', (text_1, text_2, text_3))
        conn.commit()
    else:
        cur.execute('update events set text_1 = ?, text_2 = ?, text_3 = ? where page_id = ?',
                    (text_1, text_2, text_3, page_id))
        conn.commit()
    cur.close()


# изменяет статус ивента активный/неактивный
def update_event_status(status, event_id):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('update events set is_active = ? where id = ?', (status, event_id))
    conn.commit()
    cur.close()


# возвращает текст и сущнности
def get_hello_text():
    hello_text = get_info()['hello_text']
    entities = get_entities('hello_text')
    return {'text': hello_text, 'entities': entities}


# обновляет приветственный текст
def update_hello_text(text, entities):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('update info set hello_text = ?', (text,))
    conn.commit()

    cur.execute('delete from entities where event_id = "hello_text"')
    conn.commit()

    for entity in entities:
        items = ('hello_text', entity['type'], entity['offset'], entity['length'], entity['url'])
        cur.execute('insert into entities(event_id, type, offset, length, url) values(?, ?, ?, ?, ?)', items)
        conn.commit()

    cur.close()


def check_active_worksheets(worksheets: list):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    active_events = cur.execute('select page_id from events where is_active = 1').fetchall()
    active_events_pages = [event_id[0] for event_id in active_events]
    # if len(active_events) > len(worksheets):
    for event in worksheets:
        if event.id in active_events_pages:
            active_events_pages.remove(event.id)

    for page_id in active_events_pages:
        cur.execute('update events set is_active = 0 where page_id = ?', (page_id,))
        conn.commit()
    cur.close()


# закрывает старые заказы
def daily_event_check():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    query = 'select id, event_date from events where is_active = 1'
    events = cur.execute(query).fetchall()
    today = datetime.now().date()
    for event in events:
        try:
            date_string = f'{event[1]}.{today.year}'
            date = datetime.strptime(date_string, "%d.%m.%Y").date()
            if date <= today:
                cur.execute('update events set is_active = 0 where id = ?', (event[0],))
                conn.commit()
        except Exception as ex:
            logging.warning(f'Не закрыл ивент {ex}')

    cur.close()
