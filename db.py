import pymysql.cursors
import re
import requests
import json
from datetime import datetime

# Подключение к серверу MySQL на localhost с помощью PyMySQL DBAPI.
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123',
                             database='tg_bot_users',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def find_user_by_phone(phone):
    try:
        with connection.cursor() as cursor:

            sql = "SELECT `user_telegram_id`,`is_active`,`expiration_date` FROM `user_expiration_dates` WHERE `phone`=%s"
            cursor.execute(sql, (phone,))
            result = cursor.fetchone()

            return result

    except Exception as e:
        print(e)
        connection.close()
        connection.connect()
        return False

def find_user_by_telegram(telegram_id):
    try:
        with connection.cursor() as cursor:

            sql = "SELECT `user_telegram_id`,`is_active`,`expiration_date` FROM `user_expiration_dates` WHERE `user_telegram_id`=%s"
            cursor.execute(sql, (telegram_id,))
            result = cursor.fetchone()

            return result

    except Exception as e:
        print(e)
        connection.close()
        connection.connect()
        return False

# return False,'Error connection'

def check_and_insert(phone, user_telegram_id):
    phone = (re.sub("[^0-9]", "", phone))

    if len(phone) == 0 or len(phone) < 7 or len(phone) > 15:
        return None

    elif len(phone) == 11 and phone[0] == '7':
        phone = "8" + phone[1:]
    elif len(phone) == 10:
        phone = "8" + phone

    user_info = find_user_by_phone(phone)

    if user_info is None:
        response = send_check_request(phone)

        if response is None or not response['is_active']:
            return None
        elif not response['expiration_date'] is None:
            expiration_date = datetime.strptime(response['expiration_date'], '%Y-%m-%d %H:%M:%S')
            now_date = datetime.now()
            if now_date > expiration_date:
                return None

        return insert_user(phone, user_telegram_id, True, response['expiration_date'])
    else:
        now_date = datetime.now()
        if (user_info['expiration_date'] is None or now_date <= user_info['expiration_date']) and user_info['is_active'] and user_info['user_telegram_id']==user_telegram_id:
            return True
        else:
            return False


def send_check_request(phone):
    response = requests.get('https://api.nutritionscience.pro/api/v1/users/tgbot?phone=' + phone)

    if response.status_code != 200:
        return None

    user_info = json.loads(response.text)
    if not user_info['user']:
        return None

    return user_info


def insert_user(phone, user_telegram_id, is_active, expiration_date):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO user_expiration_dates (`phone`, `user_telegram_id`, `is_active`, `expiration_date`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (phone, user_telegram_id, is_active, expiration_date))
            connection.commit()

            return True

    except Exception as e:
        connection.close()
        connection.connect()
        return False

def check_by_telegram_id(telegram_id):
    result = find_user_by_telegram(telegram_id)

    now_date = datetime.now()

    if result is None or result == False:
        return False
    elif (result['expiration_date'] is None or now_date <= result['expiration_date']) and result['is_active'] and \
            result['user_telegram_id'] == str(telegram_id):
        return True
    else:
        return False

response = check_by_telegram_id(405968842)
print(response)

