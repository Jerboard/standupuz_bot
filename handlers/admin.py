from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import logging

from create_bot import dp, bot
from functions.data_func import get_send_users, get_hello_text, update_hello_text
from keyboards.inline_kb import get_send_message_kb, get_admin_kb, get_10_last_event_kb, get_edit_hello_text_kb
from functions.google_api import google_update


# Войти как пользователь
@dp.callback_query_handler(text_startswith='back_admin_start', state='*')
async def as_user(cb: CallbackQuery):
    text = '<b>Действия администратора:</b>'
    await cb.message.edit_text(text, reply_markup=get_admin_kb(), parse_mode='html')


# список ивентов для изменения
@dp.callback_query_handler(text_startswith='edit_event_list', state='*')
async def send_message_1(cb: CallbackQuery, state: FSMContext):
    text = '<b>Изменить ивент</b>'

    await cb.message.edit_text(text, reply_markup=get_10_last_event_kb(), parse_mode='html')


# Отправить сообщение
@dp.callback_query_handler(text_startswith='send_message_1', state='*')
async def send_message_1(cb: CallbackQuery, state: FSMContext):
    await state.set_state('send_message')
    await state.update_data(data={'choice_list': [], 'everyone': False})
    await cb.answer('Отправьте сообщение для рассылки', show_alert=True)


# команда старт
@dp.message_handler(content_types=['any'], state='send_message')
async def send_message_2(msg: Message, state: FSMContext):
    await msg.delete()
    data = await state.get_data()
    if msg.content_type == 'text':
        await msg.answer(msg.text, entities=msg.entities, reply_markup=get_send_message_kb(data))
    elif msg.content_type == 'photo':
        await msg.answer_photo(photo=msg.photo[-1].file_id,
                               caption=msg.caption,
                               caption_entities=msg.caption_entities,
                               reply_markup=get_send_message_kb(data))
    elif msg.content_type == 'video':
        await msg.answer_video(video=msg.video.file_id,
                               caption=msg.caption,
                               caption_entities=msg.caption_entities,
                               reply_markup=get_send_message_kb(data))
    elif msg.content_type == 'animation':
        await msg.answer_animation(animation=msg.animation.file_id,
                                   caption=msg.caption,
                                   caption_entities=msg.caption_entities,
                                   reply_markup=get_send_message_kb(data))


# удалить сообщение
@dp.callback_query_handler(text_startswith='send_message_2', state='*')
async def send_message_2(cb: CallbackQuery, state: FSMContext):
    await cb.message.delete()
    await state.finish()


# Сменить клавиатуру
@dp.callback_query_handler(text_startswith='send_message_3', state='*')
async def send_message_3(cb: CallbackQuery, state: FSMContext):
    cb_data = cb.data.split(':')
    data = await state.get_data()

    if cb_data[1] == 'everyone':
        everyone = True if data['everyone'] is False else False
        await state.update_data(data={'everyone': everyone})
    else:
        choice_id = int(cb_data[1])
        choice_list = data['choice_list']
        if choice_id in choice_list:
            choice_list.remove(choice_id)
        else:
            choice_list.append(choice_id)

        await state.update_data(data={'choice_list': choice_list, 'everyone': False})

    data = await state.get_data()
    await cb.message.edit_reply_markup(reply_markup=get_send_message_kb(data))


# Рассылка
@dp.callback_query_handler(text_startswith='send_message_4', state='*')
async def send_message_3(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data == {}:
        await cb.answer('❕Данные устарели')
    else:
        await state.finish()
        await cb.answer('⏳ Рассылка сообщений, может уйти некоторое время')
        sent = await cb.message.answer('⏳')
        users = get_send_users(data['everyone'], data['choice_list'])
        counter = 0
        for user in users:
            try:
                user_id = user if type(user) == str else user[0]
                if cb.message.content_type == 'text':
                    await bot.send_message(chat_id=user_id,
                                           text=cb.message.text,
                                           entities=cb.message.entities)
                elif cb.message.content_type == 'photo':
                    await bot.send_photo(chat_id=user_id,
                                         photo=cb.message.photo[-1].file_id,
                                         caption=cb.message.caption,
                                         caption_entities=cb.message.caption_entities)
                elif cb.message.content_type == 'video':
                    await bot.send_video(chat_id=user_id,
                                         video=cb.message.video.file_id,
                                         caption=cb.message.caption,
                                         caption_entities=cb.message.caption_entities)
                elif cb.message.content_type == 'animation':
                    await bot.send_animation(chat_id=user_id,
                                             animation=cb.message.animation.file_id,
                                             caption=cb.message.caption,
                                             caption_entities=cb.message.caption_entities)
                counter += 1
            except Exception as ex:
                logging.warning(f'send message user {user} {ex}')

        await sent.edit_text(f'⌛️ Отправлено {counter} сообщений')


# =====================================================================
# текст приветствия

# показывает текст, предлагает поменять
@dp.callback_query_handler(text_startswith='edit_hello_text_1', state='*')
async def edit_hello_text_1(cb: CallbackQuery, state: FSMContext):
    hello_text = get_hello_text()

    await state.set_state('edit_hello_text')
    sent = await cb.message.answer(hello_text['text'],
                                   entities=hello_text['entities'],
                                   reply_markup=get_edit_hello_text_kb())
    await state.update_data(data={'chat_id': sent.chat.id, 'message_id': sent.message_id})


# команда старт
@dp.message_handler(state='edit_hello_text')
async def edit_hello_text_2(msg: Message, state: FSMContext):
    await msg.delete()

    data = await state.get_data()
    await bot.edit_message_text(text=msg.text,
                                chat_id=data['chat_id'],
                                message_id=data['message_id'],
                                entities=msg.entities,
                                reply_markup=get_edit_hello_text_kb())


# показывает текст, предлагает поменять
@dp.callback_query_handler(text_startswith='edit_hello_text_3', state='*')
async def edit_hello_text_3(cb: CallbackQuery, state: FSMContext):
    await state.finish()

    update_hello_text(cb.message.text, cb.message.entities)
    await cb.message.edit_reply_markup(reply_markup=None)
    await cb.answer('✅ Текст успешно обновлён')


# Обновляет таблицу
@dp.callback_query_handler(text_startswith='update_google_table', state='*')
async def update_google_table(cb: CallbackQuery, state: FSMContext):
    sent = await cb.message.answer('⏳')

    error_text = google_update()
    if len(error_text) == 0:
        text = '✅ База обновлена'
    else:
        text = (f'‼️ База обновлена некорректно.\n'
                f'Ошибки:\n'
                f'{error_text}')

    await sent.edit_text(text=text[:2000])


