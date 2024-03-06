import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from create_bot import tz, scheduler
from config import date_format
from functions.data_func import make_event_inactive_by_id, get_active_events_list


# проверка на цифру
def is_digit(text):
    try:
        float(text)
        return True
    except:
        return False


# ===============================================================
# возвращает даты ближайших выходных
def get_weekend_date_list():
    date_list = []
    today = datetime.now(tz).date()
    today_number = today.weekday()

    if today_number <= 4:
        add_day = 4 - today_number
    else:
        add_day = 6 if today_number == 5 else 5

    for i in range(0, 3):
        date = today + timedelta(days=add_day + i)
        date_list.append(date.strftime(date_format))
    for i in range(7, 10):
        date = today + timedelta(days=add_day + i)
        date_list.append(date.strftime(date_format))

    return date_list


# возвращает корректный формат даты
def hand_date(text: str):
    date = text.replace(' ', '.')
    date_list = text.split('.')

    if len(date_list) == 1:
        today = datetime.now(tz)
        if int(date_list[0]) > today.day:
            date = f'{date_list[0]}.{today.month}'
        else:
            month = today + relativedelta(months=1)
            date = f'{date_list[0]}.{month.month}'

    return {'date': date}


# возвращает корректный формат времени
def hand_time(text: str):
    time = text.replace('.', ':').replace(' ', ':')
    time_list = text.split(':')

    if len(time_list) == 1:
        time = f'{time_list[0]}:00'

    try:
        datetime.strptime(time, "%H:%M").time()
        return time
    except Exception as ex:
        print(ex)
        return 'error'


# обрабатывает стоимость
def hand_price(text: str):
    price = text.replace(',', '.')
    price = float(price)
    return price


# добавить шадулер на удаление
def add_scheduler_del_event(event_id, date: str, time: str):
    try:
        date = date.replace('?', '0') if len(date) > 0 else '00.00'
        time = time.replace('?', '0') if len(time) > 0 else '00:00'
        now = datetime.now(tz)
        day = int(date.split('.')[0])
        month = int(date.split('.')[1])
        hour = int(time.split(':')[0])
        minute = int(time.split(':')[1])
        year = now.year
        current_month = now.month
        if month < current_month:
            year += 1

        date = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        scheduler.add_job(make_event_inactive_by_id, 'date', run_date=date, args=[event_id])

    except Exception as ex:
        logging.warning(f'Установка шадулера на удаление utilits 103 date: {date} time: {time}\n{ex}')


# шадулер при старте на все активные ивенты
def add_start_schedulers():
    events = get_active_events_list()
    if events is not None:
        for event in events:
            add_scheduler_del_event(event['id'], event['event_date'], event['event_time'])
