from aiogram.types import Message

import sqlite3
from config_data.config import Config, load_config
import logging


config: Config = load_config()
db = sqlite3.connect('database.db', check_same_thread=False, isolation_level='EXCLUSIVE')
# sql = db.cursor()


# СОЗДАНИЕ ТАБЛИЦ
def create_table_users() -> None:
    """
    Создание таблицы верифицированных пользователей
    :return: None
    """
    logging.info("table_users")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            token_auth TEXT,
            telegram_id INTEGER,
            username TEXT,
            is_admin INTEGER,
            operator INTEGER
        )""")
        db.commit()


# ПОЛЬЗОВАТЕЛЬ - верификация токена и добавление пользователя
def check_token(message: Message) -> bool:
    logging.info("check_token")
    with db:
        sql = db.cursor()
        # Выполнение запроса для получения token_auth
        sql.execute('SELECT token_auth, telegram_id  FROM users')
        list_token = [row for row in sql.fetchall()]
        # Извлечение результатов запроса и сохранение их в список
        print('check_token', list_token)
        for row in list_token:
            token = row[0]
            telegram_id = row[1]
            if token == message.text and telegram_id == 'telegram_id':
                if message.from_user.username:
                    sql.execute('UPDATE users SET telegram_id = ?, username = ? WHERE token_auth = ?',
                                (message.chat.id, message.from_user.username, message.text))
                    db.commit()
                    return True
                else:
                    sql.execute('UPDATE users SET telegram_id = ?, username = ? WHERE token_auth = ?',
                                (message.chat.id, 'anonimus', message.text))
                    db.commit()
                    return True

        db.commit()
        return False


def add_token(token_new) -> None:
    logging.info(f'add_token: {token_new}')
    with db:
        sql = db.cursor()
        sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, operator) '
                    f'VALUES ("{token_new}", "telegram_id", "username", 0, 0)')
        db.commit()


def add_super_admin(id_admin, user_name) -> None:
    """
    Добавление суперадмина в таблицу пользователей
    :param id_admin:
    :param user:
    :return:
    """
    logging.info(f'add_super_admin')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id FROM users')
        list_user = [row[0] for row in sql.fetchall()]

        if int(id_admin) not in list_user:
            sql.execute(f'INSERT INTO users (token_auth, telegram_id, username, is_admin, operator) '
                        f'VALUES ("SUPERADMIN", {id_admin}, "{user_name}", 1, 0)')
            db.commit()


def get_list_users() -> list:
    """
    ПОЛЬЗОВАТЕЛЬ - список пользователей верифицированных в боте
    :return:
    """
    logging.info(f'get_list_users')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users WHERE NOT username = ? ORDER BY id', ('username',))
        list_username = [row for row in sql.fetchall()]
        return list_username


def get_user(telegram_id):
    """
    ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
    :param telegram_id:
    :return:
    """
    logging.info(f'get_user')
    with db:
        sql = db.cursor()
        return sql.execute('SELECT username FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()


def delete_user(telegram_id):
    """
    ПОЛЬЗОВАТЕЛЬ - удалить пользователя
    :param telegram_id:
    :return:
    """
    logging.info(f'delete_user')
    with db:
        sql = db.cursor()
        sql.execute('DELETE FROM users WHERE telegram_id = ?', (telegram_id,))
        db.commit()


def get_list_notadmins() -> list:
    logging.info(f'get_list_notadmins')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (0, 'username'))
        list_notadmins = [row for row in sql.fetchall()]
        return list_notadmins


# АДМИНИСТРАТОРЫ - назначить пользователя администратором
def set_admins(telegram_id):
    logging.info(f'set_admins')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (1, telegram_id))
        db.commit()


# АДМИНИСТРАТОРЫ - список администраторов
def get_list_admins() -> list:
    logging.info(f'get_list_admins')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id, username FROM users WHERE is_admin = ? AND NOT username = ?', (1, 'username'))
        list_admins = [row for row in sql.fetchall()]
        return list_admins


# АДМИНИСТРАТОРЫ - разжаловать пользователя из администраторов
def set_notadmins(telegram_id):
    logging.info(f'set_notadmins')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET is_admin = ? WHERE telegram_id = ?', (0, telegram_id))
        db.commit()


def set_start_workday(telegram_id: int) -> None:
    logging.info(f'set_start_workday')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET operator = ? WHERE telegram_id = ?', (1, telegram_id,))
        db.commit()


def set_start_workday_all() -> None:
    logging.info(f'set_start_workday_all')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE users SET operator = ?', (0,))
        db.commit()


def get_start_workday(telegram_id: int) -> bool:
    logging.info(f'get_start_workday')
    with db:
        sql = db.cursor()
        list_workday = sql.execute('SELECT operator FROM users WHERE telegram_id = ?', (telegram_id,)).fetchone()
        return bool(list_workday[0])

if __name__ == '__main__':
    db = sqlite3.connect('/Users/antonponomarev/PycharmProjects/PRO_SOFT/database.db', check_same_thread=False, isolation_level='EXCLUSIVE')
    sql = db.cursor()
    list_user = get_list_users()
    print(list_user)