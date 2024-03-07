import os
from dotenv import load_dotenv

load_dotenv ()

DEBUG = bool(int(os.getenv('DEBUG')))
TOKEN = os.getenv('TOKEN')
# TOKEN = '7181274585:AAEPJ_CXjhKFR3CiLhV8W9AS_8KmHej7JmI'
google_table_id = os.getenv('GOOGLE_TABLE_ID')
bot_id = int(os.getenv('BOT_ID'))

tzone = 'Asia/Tashkent'

admin_group_id = int(os.getenv('ADMIN_GROUP_ID'))

date_format = '%d.%m'
time_format = '%H:%M'

google_key_path = os.path.join('data', 'google_key.json')
db_path = os.path.join('data', 'data.db')

months_map = {
    'Jan': 'января',
    'Feb': 'февраля',
    'Mar': 'марта',
    'Apr': 'апреля',
    'May': 'мая',
    'Jun': 'июня',
    'Jul': 'июля',
    'Aug': 'августа',
    'Sep': 'сентября',
    'Oct': 'октября',
    'Nov': 'ноября',
    'Dec': 'декабря'
}

number_month_map = {'января': '01',
                    'февраля': '02',
                    'марта': '03',
                    'апреля': '04',
                    'мая': '05',
                    'июня': '06',
                    'июля': '07',
                    'августа': '08',
                    'сентября': '09',
                    'октября': '10',
                    'ноября': '11',
                    'декабря': '12'}


place_map = {'1': 'место',
             '2': 'места',
             '3': 'места',
             '4': 'места',
             '5': 'мест',
             '6': 'мест',
             '7': 'мест'}


table_map = {'1': 'столик',
             '2': 'столика',
             '3': 'столика',
             '4': 'столика',
             '5': 'стоиков',
             '6': 'стоиков',
             '7': 'стоиков'}
