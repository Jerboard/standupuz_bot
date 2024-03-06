import logging
from asyncio import sleep

from config import admin_group_id
from create_bot import bot

from functions.data_func import add_new_order, make_order_in_table, update_count_option
from functions.google_api import add_new_order_in_table


# проверка на админа
async def is_admin(user_id):
    user = await bot.get_chat_member(admin_group_id, user_id)
    if user.status == 'creator' or user.status == 'administrator':
        return True
    else:
        return False


# добавляет пользователя в таблицу
async def end_book(data: dict):
    # запись в таблицу, запись в базу, оповещение
    option_update_info = update_count_option(data['option_id'], data['count_place'])
    order_id = add_new_order(
        user_id=data['user_id'],
        phone=data['phone'],
        event_id=data['event_id'],
        option=option_update_info['name'],
        count_place=data['count_place'],
        page_id=data['page_id'])

    in_table = False
    i = 0
    while in_table is False:
        try:
            add_new_order_in_table(count_place=data['count_place'],
                                   option=option_update_info['name'],
                                   name=data['name'],
                                   phone=data['phone'],
                                   page_id=data['page_id'],
                                   empty_place=option_update_info['empty_place'],
                                   option_count_cell=option_update_info['cell'],
                                   order_id=order_id,
                                   username=data['username'])
            in_table = True
            make_order_in_table(order_id)
            text = f'Новая бронь:\n' \
                   f'{option_update_info["name"]} - {data["count_place"]}\n' \
                   f'{data["event_title"]}\n' \
                   f'{data["name"]}\n' \
                   f'{data["phone"]}\n'

            await bot.send_message(admin_group_id, text)

        except Exception as ex:
            i += 1
            if i > 30:
                in_table = 'error'
                logging.warning(f'end try add row {i} {ex}')
                text = f'‼️ ОШИБКА! Ваша бронь не была добавлена. Попробуйте ещё раз. Если ошибка будет повторяться, ' \
                       f'обратитесь в поддержку'
                await bot.send_message(data['user_id'], text)
            else:
                logging.warning(f'try add row {i} {ex}')
                await sleep(5)
