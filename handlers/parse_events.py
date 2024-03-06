from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

from create_bot import dp, bot
from config import number_month_map
# from functions.acync_utilits import is_anons
from functions.data_func import add_new_event
from functions.google_api import create_new_page

import re

# собирает данные об ивенте
# @dp.channel_post_handler(lambda msg: is_anons(msg.caption_entities), content_types=['any'])
# async def pars_event(msg: Message):
#     msg.caption_entities
#     if msg.content_type == 'photo':
#         file_id = msg.photo[-1].file_id
#     elif msg.content_type == 'video':
#         file_id = msg.video.file_id
#     elif msg.content_type == 'animation':
#         file_id = msg.animation.file_id
#     else:
#         file_id = 'error'
#
#     if msg.caption is not None:
#         text = msg.caption
#         if len(text.split('📌')) > 1:
#             place = text.split('📌')[1].split('\n')[0]
#         elif len(text.split('📍')) > 1:
#             place = text.split('📍')[1].split('\n')[0]
#         else:
#             place = '???'
#
#         try:
#             datetime_string = text.split('⏰')[1].split('\n')[0]
#             time_split = datetime_string.split(':')
#             if len(time_split) > 1:
#                 time = f'{time_split[-2][-2:]}:{time_split[-1][:2]}'
#             else:
#                 time = '??:??'
#
#             datetime_string_word_list = datetime_string.strip().split(' ')
#             day = datetime_string_word_list[0]
#
#             if len(day.split('.')) > 1:
#                 date = date_string = day.replace(',', '')
#             else:
#                 day = datetime_string_word_list[0]
#                 month = datetime_string_word_list[1].replace(',', '')
#                 # date_string = f'{day} {month}'
#                 month_digit = number_month_map.get(month) if number_month_map.get(month) is not None else '??'
#                 date = f'{day} {month_digit}'
#         except:
#             date = date_string = '??.??'
#             time = '??:??'
#
#         if len(text.split('🫰')) > 1:
#             price_string = text.split('🫰')[1].split('\n')
#             price = re.sub(r"[^\d,]", "", price_string[0])
#         else:
#             price = '??'
#
#         type_media = msg.content_type if msg.media_group_id is None else 'media_group'
#         media_id = file_id #if msg.media_group_id is None else msg.media_group_id
#         page_id = create_new_page(date, time, price, place)
#
#         add_new_event(date, time, text, place.strip(), price, type_media, media_id, msg.chat.id, msg.message_id, page_id)
#
#     # add_new_media(msg.media_group_id, msg.content_type, file_id, msg.chat.id, msg.message_id)
#
