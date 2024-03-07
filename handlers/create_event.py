from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.dispatcher import FSMContext
import re

from asyncio import sleep

from create_bot import dp, bot

from keyboards.inline_kb import get_edit_event_kb, get_choisce_date_kb, get_choisce_time_kb, update_is_active_event_kb,\
     get_choisce_tariff_kb
from functions.utilits import hand_date, hand_time, add_scheduler_del_event
from functions.data_func import add_new_event, update_event_status, get_event_info, get_entities, update_event_cover
from functions.google_api import create_new_page


# основная функция изменений
async def edit_event(state: FSMContext, chat_id=None):
    await state.set_state('create_event')
    data = await state.get_data()
    first = True
    tariff_text = ''
    for tariff in data['tariffs']:
        if first is True:
            tariff_text = f'{tariff[0]} - {tariff[1]}\n'
            first = False
        else:
            tariff_text = f'{tariff_text}{tariff[0]} - {tariff[1]}\n'

    if data['type'] == 'new':

        text = f'{data["text"]}\n\n' \
               f'==============\n' \
               f'Название: {data["title"]}\n' \
               f'📅 Дата: {data["date"]}\n' \
               f'⏰ Время: {data["time"]}\n' \
               f'🫰 Места:\n{tariff_text}'

    else:
        text = data["text"]

    if data['is_first']:
        sent = await bot.send_photo(chat_id=chat_id,
                                    photo=data['photo_id'],
                                    caption=text,
                                    caption_entities=data['entities'],
                                    reply_markup=get_edit_event_kb(data['type']))

        await state.update_data(data={'is_first': False, 'chat_id': sent.chat.id, 'message_id': sent.message_id})
    else:
        photo = InputMediaPhoto(data['photo_id'],
                                caption=text,
                                caption_entities=data['entities'])
        await bot.edit_message_media(media=photo,
                                     chat_id=data['chat_id'],
                                     message_id=data['message_id'],
                                     reply_markup=get_edit_event_kb(data['type']))


# возвращает к
@dp.callback_query_handler(text_startswith='back_edit_event', state='*')
async def create_new_event(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await cb.message.edit_reply_markup(reply_markup=get_edit_event_kb(data['type']))


# начало создания
@dp.callback_query_handler(text_startswith='new_event', state='*')
async def create_new_event(cb: CallbackQuery, state: FSMContext):
    await state.finish()
    cb_data = cb.data.split(':')
    if cb_data[1] == 'new':
        # text
        # photo_id = 'AgACAgIAAxkBAAIk0GS33TlFAAHiL3zjexrnj0gkFiF7RwACNMoxGx-iwEnWhZJ-wyQWyQEAAwIAA20AAy8E'
        # work
        photo_id = 'AgACAgIAAxkBAAMDZJLz5wR0skvRu9z8XLdrFaYsz80AAvzOMRuk6phIPY914z_9bZoBAAMCAANtAAMvBA'
        await state.update_data(data={
            'is_first': True,
            'photo_id': photo_id,
            'text': 'Добавьте текст',
            'title': '',
            'entities': [],
            'date': '',
            'time': '',
            'tariffs': [],
            'type': 'new'
        })

    elif cb_data[1] == 'edit':
        event_info = get_event_info(cb_data[2])
        entities = get_entities(event_info['id'])
        await state.update_data(data={
            'is_first': True,
            'photo_id': event_info['photo_id'],
            'text': event_info['text'],
            'title': '',
            'entities': entities,
            'date': '',
            'time': '',
            'tariffs': [],
            'type': 'edit',
            'event_id': cb_data[2],
            'is_active': event_info['is_active']
        })

    await edit_event(state, chat_id=cb.message.chat.id)


# принимает дату текстом
@dp.message_handler(content_types=['text', 'photo'], state='create_event')
async def edit_text(msg: Message, state: FSMContext):
    await msg.delete()

    if msg.content_type == 'photo':
        if msg.caption is None:
            await state.update_data(data={
                'photo_id': msg.photo[-1].file_id
            })
        else:
            await state.update_data(data={
                'photo_id': msg.photo[-1].file_id,
                'text': msg.caption,
                'entities': msg.caption_entities
            })
    elif msg.content_type == 'text':
        await state.update_data(data={
            'text': msg.text,
            'entities': msg.entities
        })

    await edit_event(state)


# ==================================================================
# распределяет изменения, даёт статусы
@dp.callback_query_handler(text_startswith='edit_event_step_1', state='*')
async def create_new_event(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    if cb_data[1] == 'title':
        await state.set_state('edit_title')
        await cb.answer('🖍Изменить название')

    elif cb_data[1] == 'date':
        await state.set_state('edit_date')
        await cb.answer('🖍Изменить дату')
        await cb.message.edit_reply_markup(reply_markup=get_choisce_date_kb())

    elif cb_data[1] == 'time':
        await state.set_state('edit_time')
        await cb.answer('🖍Изменить время')
        await cb.message.edit_reply_markup(reply_markup=get_choisce_time_kb())

    elif cb_data[1] == 'price':
        await state.set_state('edit_price')
        await cb.answer('🖍Места и опции')
        await cb.message.edit_reply_markup(reply_markup=get_choisce_tariff_kb())


# принимает текст сообщения
@dp.message_handler(state='edit_title')
async def edit_text(msg: Message, state: FSMContext):
    await msg.delete()
    await state.update_data(data={'title': msg.text})

    await edit_event(state)


# принимает колбек с датой
@dp.callback_query_handler(text_startswith='edit_date', state='*')
async def create_new_event(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    date = hand_date(cb_data[1])
    await state.update_data(data={'date': date['date']})

    await edit_event(state)


# принимает дату текстом
@dp.message_handler(state='edit_date')
async def edit_text(msg: Message, state: FSMContext):
    await msg.delete()
    date = hand_date(msg.text)
    if date == 'error':
        sent = await msg.answer('❌ Некорректный формат даты')
        await sleep(3)
        await sent.delete()

    else:
        await state.update_data(data={'date': date['date']})
        await edit_event(state)


# принимает колбек с временем
@dp.callback_query_handler(text_startswith='edit_time', state='*')
async def create_new_event(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(' ')  # есть двоеточие во времени
    await state.update_data(data={'time': cb_data[1]})

    await edit_event(state)


# принимает время текстом
@dp.message_handler(state='edit_time')
async def edit_text(msg: Message, state: FSMContext):
    await msg.delete()
    time = hand_time(msg.text)
    if time == 'error':
        sent = await msg.answer('❌ Некорректный формат времени')
        await sleep(3)
        await sent.delete()

    else:
        await state.update_data(data={'time': time})
        await edit_event(state)


# принимает список свободных мест
@dp.message_handler(state='edit_price')
async def edit_text(msg: Message, state: FSMContext):
    await msg.delete()
    tariffs = []
    tariff_list = msg.text.split(',')
    for tariff in tariff_list:
        digits = re.findall(r'\d+', tariff)
        if len(digits) == 0:
            digit = 0
        else:
            digit = int(digits[0])
        text = re.sub(r'\d+', '', tariff).strip().capitalize()
        tariffs.append([text, digit])

    await state.update_data(data={'tariffs': tariffs})
    await edit_event(state)


@dp.callback_query_handler(text_startswith='edit_event_accept', state='*')
async def create_new_event(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # for i in data.items():
    #     print(i)

    if data['type'] == 'new':

        if data['title'] == '':
            await cb.answer('❗️Ошибка. Добавьте название', show_alert=True)

        elif not data['tariffs']:
            await cb.answer('❗️Ошибка. Добавьте опции', show_alert=True)

        else:
            page_id = create_new_page(data['date'], data['time'], data['tariffs'], data['title'])
            if page_id == 'APIError':
                await cb.answer(
                    '❗️Ошибка. Вкладка с таким названием уже существует. Удалите старую вкладку или переименуйте '
                    'ивент', show_alert=True)
            else:
                await state.finish()
                data['page_id'] = page_id
                event_id = add_new_event(data)

                await cb.message.edit_reply_markup(reply_markup=update_is_active_event_kb('1', event_id))

    else:
        # for k, v in data.items():
        #     print(k, v)
        update_event_cover(data)
        await cb.message.edit_reply_markup(
            reply_markup=update_is_active_event_kb(str(data['is_active']), data['event_id']))


# изменить статус ивента
@dp.callback_query_handler(text_startswith='event_active_status', state='*')
async def event_active_status(cb: CallbackQuery):
    cb_data = cb.data.split(':')
    update_event_status(cb_data[1], cb_data[2])
    await cb.message.edit_reply_markup(reply_markup=update_is_active_event_kb(cb_data[1], cb_data[2]))
