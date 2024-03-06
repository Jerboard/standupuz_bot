import logging

import gspread
from gspread.exceptions import WorksheetNotFound
from gspread.exceptions import APIError
from time import sleep

from config import google_table_id, google_key_path
from functions import data_func as db


# добавляет данные в таблицу
def create_new_page(date, time, tariffs, title):
    gc = gspread.service_account(filename=google_key_path)
    table = gc.open_by_key(google_table_id)
    # проверка таблицы
    try:
        page = table.add_worksheet(title=title, cols=20, rows=200)
    except APIError as ex:
        logging.warning(f'google_api 30 {ex}')
        return 'APIError'

    # Настройки
    setting_list = [['Активна', ''],
                    ['Название', title],
                    ['Дата', date],
                    ['Время', time]]

    option_row = 5
    for tariff in tariffs:
        formula = f'={tariff[1]}-SUMIFS(D:D; E:E; A{option_row})'
        setting_list.append([tariff[0], formula])
        option_row += 1
    page.update(f'a1:b10', setting_list, raw=False)

    # тексты
    info = db.get_info()
    page.merge_cells('E1:J3')
    page.update('D1:1', [['Текст 1', info['text_1']]])
    sleep(1)
    page.merge_cells('E4:J6')
    page.update('D4:E4', [['Текст 2', info['text_2']]])
    sleep(1)
    page.merge_cells('E7:J9')
    page.update('D7:E7', [['Финальный текст', info['text_3']]])
    sleep(1)

    # таблица гостей
    head_list = [['ID', 'Мест', 'Опции', 'Имя', 'Username', 'Телефон', 'Ссылка', 'Оплатил', 'Примечание', 'Откуда']]
    for i in range(0, 190):
        head_list.append(['', '', '-', '', '', '', '', '', '', ''])
    cells = f'c10:l200'
    page.update(cells, head_list)
    sleep(1)
    # триггер активности
    page.update('C1', 'S')

    return page.id


def google_update() -> str:
    error_text = ''
    gc = gspread.service_account (filename=google_key_path)
    tables = gc.open_by_key (google_table_id)

    # обновляем настройки
    try:
        base_text_1 = tables.sheet1.acell('E3').value
        base_text_2 = tables.sheet1.acell('E7').value
        base_text_3 = tables.sheet1.acell('E11').value

        db.update_info_texts (text_1=base_text_1, text_2=base_text_2, text_3=base_text_3)
    except Exception as ex:
        error_text = f'{error_text}\n❌ Не удалось обновить базовые тексты:\n{ex}'

    active_events = db.get_active_events_list()
    active_page_ids = [event['page_id'] for event in active_events]
    # active_page_ids = [706229500, ]
    for table in tables:
        if table.id in active_page_ids:
            event = db.get_event_info(event_id=table.id, on_page_id=True)
            # проверить тексты
            try:
                text_1 = table.acell('E1').value
                text_2 = table.acell('E4').value
                text_3 = table.acell('E7').value

                db.update_info_texts(text_1=text_1, text_2=text_2, text_3=text_3, page_id=table.id)
            except Exception as ex:
                error_text = f'{error_text}\n❌ Не удалось обновить тексты {table.title}:\n{ex}'

            # проверить опции
            try:
                is_active = True if table.acell('B1').value == 'TRUE' else False
                title = table.acell ('B2').value
                event_date_str = table.acell ('B3').value
                event_time_str = table.acell ('B4').value

                db.update_event (
                    is_active=is_active,
                    title=title,
                    date=event_date_str,
                    time=event_time_str,
                    page_id=table.id)

            except Exception as ex:
                error_text = f'{error_text}\n❌ Не удалось обновить опции {table.title}:\n{ex}'

            # опции мест. Сначала удаляем все старые, записываем новые
            options = table.get_values ('A5:B9')

            db.del_all_event_option(event['id'])
            row_num = 5
            for option in options:
                try:
                    option_title = option[0]
                    empty_place = int(option[1])
                    cell = f'B{row_num}'
                    cell_f = table.acell (cell, value_render_option='FORMULA').value
                    all_place = int(cell_f.split('-')[0][1:])
                    row_num += 1

                    db.add_option(
                        event_id=event['id'],
                        title=option_title,
                        empty_place=empty_place,
                        all_place=all_place,
                        cell=cell)
                except Exception as ex:
                    error_text = f'{error_text}\n❌ Не удалось обновить места {table.title} {option[0]}:\n{ex}'

            # проверить места
            places = table.get_values('C11:M200')

            for place in places:
                if place[2] != '-':
                    try:
                        order_id = int(place[0])
                        book_count = int(place[1])
                        book_option = place[2]
                        phone = place[5]

                        db.add_new_order(
                            user_id=order_id,
                            phone=phone,
                            event_id=event['id'],
                            option=book_option,
                            count_place=book_count,
                            page_id=table.id
                        )
                    except Exception as ex:
                        error_text = (f'{error_text}\n❌ Не удалось обновить бронь {table.title} '
                                      f'{place[2]} {place[1]} тел. {place[5]}:\n{ex}')

    return error_text


# проверка обновлений
def add_new_order_in_table(count_place, option, name, phone, page_id, empty_place, option_count_cell, order_id, username):
    gc = gspread.service_account(filename=google_key_path)
    table = gc.open_by_key(google_table_id)
    page = table.get_worksheet_by_id(page_id)
    client_table = page.get(f'C11:C200')

    empty_row_index = len(client_table) + 11
    for i, row in enumerate(client_table):
        if row == ['-'] or row == []:
            empty_row_index = i + 11  # Прибавляем 10, чтобы получить номер строки в таблице
            break

    if not username:
        username = ''
        link = f'https://t.me/+{phone}'
    else:
        link = f'https://t.me/{username}'
        username = f'@{username}'

    row = [[order_id, count_place, option, name, username, phone, link]]
    cell = f'C{empty_row_index}:I{empty_row_index}'
    sleep(1)
    page.update(cell, row)
    # вернуть если формула будет криво работать
    # sleep(1)
    # page.update(option_count_cell, empty_place)
