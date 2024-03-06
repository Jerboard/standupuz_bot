from aiogram.utils import executor
from aiogram import Dispatcher
from create_bot import scheduler
from handlers import dp

import logging
import sys

from functions.google_api import google_update
from functions.utilits import add_start_schedulers
from functions.data_func import daily_event_check
from config import DEBUG


async def start_schedulers():
    # scheduler.add_job(check_google_update, 'interval', minutes=1)
    scheduler.add_job(daily_event_check, 'cron', hour=21)
    # add_start_schedulers()
    scheduler.start()


async def on_startup(dp_: Dispatcher):
    # await start_schedulers()
    logging.warning('start polling')


if __name__ == '__main__':
    if DEBUG:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    else:
        logging.basicConfig (level=logging.WARNING, filename='log.log', format="%(asctime)s %(levelname)s %(message)s")
    executor.start_polling(dp, on_startup=on_startup)
