from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import re
from asyncio import sleep

from config import DEBUG
from create_bot import dp, bot
from functions.data_func import get_event_info, add_user, update_user_phone, get_user_info, get_hello_text, \
    get_entities, get_info, get_option_info
from functions.acync_utilits import is_admin, end_book
from functions.utilits import is_digit
from keyboards.inline_kb import get_admin_kb, get_events_list_kb, get_book_kb, get_chioce_count_place_kb, \
     get_social_medias_kb, get_alert_1_kb, get_alert_2_kb, get_sent_phone_kb, get_sent_name_kb


# команда старт
@dp.message_handler(commands=['start'], state='*')
async def com_start(msg: Message, state: FSMContext):
    await state.finish()
    add_user(msg.from_user.id, msg.from_user.full_name, msg.from_user.username)
    admin_status = await is_admin(msg.from_user.id)
    # admin_status = True if msg.from_user.id == 524275902 else False
    if admin_status:
        text = '<b>Действия администратора:</b>'
        await msg.answer(text, reply_markup=get_admin_kb(), parse_mode='html')
    else:
        hello_text = get_hello_text()
        await msg.answer(hello_text['text'], entities=hello_text['entities'], reply_markup=get_events_list_kb())


# Вернуть первый экран
@dp.callback_query_handler(text_startswith='back_com_start', state='*')
async def back_com_start(cb: CallbackQuery):
    hello_text = get_hello_text()
    await cb.message.edit_text(hello_text['text'], entities=hello_text['entities'], reply_markup=get_events_list_kb())


# Ссылки на соцсети
@dp.callback_query_handler(text_startswith='social_medias', state='*')
async def social_medias(cb: CallbackQuery):
    text = f'Наши соцсети'
    await cb.message.edit_text(text, reply_markup=get_social_medias_kb())


# показывает ивент
@dp.callback_query_handler(text_startswith='view_event', state='*')
async def view_event(cb: CallbackQuery):
    _, event_id_str = cb.data.split(':')
    event_id = int(event_id_str)

    event_info = get_event_info(event_id)
    entities = get_entities(event_info['id'])

    photo_id = event_info ['photo_id']
    if DEBUG:
        photo_id = 'AgACAgIAAxkBAAMGZecrNFZ3ctI1jBQlYNCIneaND5IAAkTaMRuSRDhLC7cywGea_iYBAAMCAAN5AAM0BA'
    await cb.message.answer_photo(photo=photo_id,
                                  caption=event_info['text'],
                                  caption_entities=entities,
                                  reply_markup=get_book_kb(event_id))


# показывает ивент
@dp.callback_query_handler(text_startswith='book_1', state='*')
async def book_1(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split (':')

    if cb_data[1] == 'not':
        await cb.answer('Свободные места закончились', show_alert=True)
    else:
        info = get_info()
        if cb_data[1] == 'back':
            data = await state.get_data()
            event_info = get_event_info(data['event_id'])
            text = event_info['text_1'] if event_info['text_1'] is not None else info['text_1']
            await cb.message.edit_text(text, reply_markup=get_alert_1_kb())
        else:
            event_id = int (cb_data[1])
            option_id = int (cb_data[2])
            event_info = get_event_info(event_id)

            await state.finish()
            await state.set_state('choice_count_place')

            text = event_info['text_1'] if event_info['text_1'] is not None else info['text_1']
            sent = await cb.message.answer(text,  reply_markup=get_alert_1_kb())
            await state.update_data(data={'chat_id': sent.chat.id,
                                          'message_id': sent.message_id,
                                          'event_id': event_id,
                                          'option_id': option_id,
                                          'user_id': cb.from_user.id,
                                          'username': cb.from_user.username,
                                          'page_id': event_info['page_id'],
                                          'event_title': event_info['title']})


# второй текст предупреждение
@dp.callback_query_handler(text_startswith='book_2', state='*')
async def book_2(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    if cb_data[1] == 'back':
        await cb.message.delete()
        await state.finish()
    else:
        info = get_info()
        data = await state.get_data()
        event_info = get_event_info(data['event_id'])
        text = event_info['text_2'] if event_info['text_2'] is not None else info['text_2']
        await cb.message.edit_text(text, reply_markup=get_alert_2_kb())


# количество мест
@dp.callback_query_handler(text_startswith='book_3', state='*')
async def book_3(cb: CallbackQuery, state: FSMContext):
    text = 'Укажите количество мест (или введите число)'
    await state.set_state('choice_count_place')
    await cb.message.edit_text(text, reply_markup=get_chioce_count_place_kb())


# принимает количество мест цифрой
@dp.message_handler(state='choice_count_place')
async def book_4_text(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()

    count_free_place = re.sub(r"[^\d,]", "", msg.text)
    if count_free_place == '':
        count_free_place = 0
    option_info = get_option_info(data['option_id'])

    if option_info['empty_place'] < int(count_free_place):
        sent = await msg.answer(f'Осталось только {option_info["empty_place"]} мест')
        await sleep(5)
        await sent.delete()

    else:
        await state.update_data(data={'count_place': int(count_free_place)})

        user_info = get_user_info(msg.from_user.id)
        await state.set_state('send_contact')
        await bot.edit_message_text(text='Укажите контактный телефон',
                                    reply_markup=get_sent_phone_kb(user_info['phone']),
                                    chat_id=data['chat_id'],
                                    message_id=data['message_id'])


# принимает количество мест колбеком
@dp.callback_query_handler(text_startswith='book_4', state='*')
async def book_4(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    if cb_data[1] != 'back':
        count_free_place = int(cb_data[1])
        await state.update_data(data={'count_place': int(count_free_place)})

        data = await state.get_data()
        option_info = get_option_info(data['option_id'])
        if option_info['empty_place'] < int(count_free_place):
            sent = await cb.message.answer(f'Осталось только {option_info["empty_place"]} мест')
            await sleep(5)
            await sent.delete()
            return

    user_info = get_user_info(cb.from_user.id)
    await state.set_state('send_contact')
    await cb.message.edit_text('Укажите контактный телефон', reply_markup=get_sent_phone_kb(user_info['phone']))


# принимает телефон цифрой
@dp.message_handler(content_types=['text', 'contact'], state='send_contact')
async def book_5_text(msg: Message, state: FSMContext):
    await msg.delete()
    if msg.content_type == 'contact':
        phone = msg.contact.phone_number
        update_user_phone(msg.from_user.id, phone)

    else:
        phone = msg.text.replace(' ', '').replace('+', '')
        if is_digit(phone):
            update_user_phone(msg.from_user.id, phone)
        else:
            sent = await msg.answer('❗️ Некорректный номер')
            await sleep(3)
            await sent.delete()
            return

    await state.update_data(data={'phone': phone})
    data = await state.get_data()
    await state.set_state('send_name')
    await bot.edit_message_text(text='Укажите имя',
                                reply_markup=get_sent_name_kb(msg.from_user.first_name),
                                chat_id=data['chat_id'],
                                message_id=data['message_id'])


# принимает телефон калбеком
@dp.callback_query_handler(text_startswith='book_5', state='*')
async def book_5(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    await state.update_data(data={'phone': cb_data[1]})
    await state.set_state('send_name')
    await cb.message.edit_text('Укажите имя', reply_markup=get_sent_name_kb(cb.from_user.first_name))


# Принимает имя текстом
@dp.message_handler(state='send_name')
async def book_6_text(msg: Message, state: FSMContext):
    await msg.delete()
    await state.update_data(data={'name': msg.text.capitalize()})
    data = await state.get_data()
    await state.finish()
    text = 'Спасибо! Администратор свяжется с Вами для завершения бронирования и оплаты с 14:00 до 22:00 по будням, ' \
           'с 16:00 до 23:00 вых'
    await bot.edit_message_text(text=text,
                                chat_id=data['chat_id'],
                                message_id=data['message_id'])
    await end_book(data)


# принимает телефон калбеком
@dp.callback_query_handler(text_startswith='book_6', state='*')
async def book_6(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    await state.update_data(data={'name': cb_data[1]})

    data = await state.get_data()
    await state.finish()

    info = get_info()
    event_info = get_event_info(data['event_id'])
    text = event_info['text_3'] if event_info['text_3'] is not None else info['text_3']
    await cb.message.edit_text(text)
    await end_book(data)


# в разработке
@dp.callback_query_handler(text_startswith='in_dev')
async def in_dev(cb: CallbackQuery):
    await cb.answer('🛠 В разработке')


# Принимает имя текстом
# @dp.message_handler(content_types=['any'])
# async def book_6_text(msg: Message, state: FSMContext):
#     print(msg.chat)
#     print(msg.photo[-1].file_id)
