from aiogram.types import Message

import sqlite3
from config_data.config import Config, load_config
import logging


config: Config = load_config()
db = sqlite3.connect('database.db', check_same_thread=False, isolation_level='EXCLUSIVE')
# sql = db.cursor()

# <editor-fold desc = "СЕКЦИЯ (ТАБЛИЦА ПОЛЬЗОВАТЕЛЬ)">
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
    :return: list(telegram_id:int, username:str)
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


def get_user_id(id):
    """
    ПОЛЬЗОВАТЕЛЬ - имя пользователя по его id
    :param id:
    :return:
    """
    logging.info(f'get_user_id')
    with db:
        sql = db.cursor()
        return sql.execute('SELECT username FROM users WHERE id = ?', (id,)).fetchone()


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
# </editor-fold>


# <editor-fold desc = "СЕКЦИЯ (ТАБЛИЦА ОТПУСКА и СМЕНЫ)">
# СПИСОК СМЕН и ОТПУСК
def create_table_workday_leave() -> None:
    """
    Создание таблицы верифицированных пользователей
    :return: None
    """
    logging.info("table_users")
    with db:
        sql = db.cursor()
        sql.execute("""CREATE TABLE IF NOT EXISTS work_leave(
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER,
            username TEXT,
            current TEXT,
            forward TEXT,
            leave TEXT
        )""")
        db.commit()


def add_manager(telegram_id: int, username: str) -> None:
    logging.info(f'add_manager')
    with db:
        sql = db.cursor()
        sql.execute('SELECT telegram_id FROM work_leave')
        list_user = [row[0] for row in sql.fetchall()]
        if int(telegram_id) not in list_user:
            sql.execute(f'INSERT INTO work_leave (telegram_id, username, current, forward, leave) '
                        f'VALUES ({telegram_id}, "{username}", "0", "0", "0")')
            db.commit()


def get_list_workday(telegram_id: int, month_work: int):
    logging.info(f'get_start_workday')
    with db:
        sql = db.cursor()
        if month_work == 1:
            list_workday = sql.execute('SELECT forward FROM work_leave WHERE telegram_id = ?',
                                       (telegram_id,)).fetchone()
        else:
            list_workday = sql.execute('SELECT current FROM work_leave WHERE telegram_id = ?',
                                       (telegram_id,)).fetchone()
        if list_workday is None:
            return None
        return list_workday[0].split(',')


def get_list_workday_all(month_work: int):
    logging.info(f'get_start_workday')
    with db:
        sql = db.cursor()
        if month_work == 1:
            list_workday = sql.execute('SELECT forward FROM work_leave',).fetchall()
        else:
            list_workday = sql.execute('SELECT current FROM work_leave',).fetchall()
    return list_workday


def get_list_workday_all_manager(month_work: int):
    logging.info(f'get_start_workday')
    with db:
        sql = db.cursor()
        if month_work == 1:
            list_workday = sql.execute('SELECT telegram_id, forward FROM work_leave',).fetchall()
        else:
            list_workday = sql.execute('SELECT telegram_id, current FROM work_leave',).fetchall()
    return list_workday


def get_list_workday_all_alert(month_work: int):
    logging.info(f'get_start_workday')
    with db:
        sql = db.cursor()
        if month_work == 1:
            list_workday = sql.execute('SELECT telegram_id, forward FROM work_leave').fetchall()
        else:
            list_workday = sql.execute('SELECT telegram_id, current FROM work_leave').fetchall()
    return list_workday

def set_list_workday(list_workday: str, month_work: int, telegram_id: int):
    logging.info(f'set_list_workday')
    with db:
        sql = db.cursor()
        if month_work == 1:
            sql.execute('UPDATE work_leave SET forward = ? WHERE telegram_id = ?', (list_workday, telegram_id))
        else:
            sql.execute('UPDATE work_leave SET current = ? WHERE telegram_id = ?', (list_workday, telegram_id))
        db.commit()

def change_column():
    logging.info(f'set_list_workday')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE work_leave SET current = forward')
        db.commit()


def update_forward():
    logging.info(f'set_list_workday')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE work_leave SET forward = ?', ('0',))
        db.commit()


def update_leave(leave, telegram_id):
    logging.info(f'set_list_workday')
    with db:
        sql = db.cursor()
        sql.execute('UPDATE work_leave SET leave = ? WHERE telegram_id = ?', (leave, telegram_id, ))
        db.commit()


def get_leave():
    logging.info(f'get_leave')
    with db:
        sql = db.cursor()
        list_leave = sql.execute('SELECT telegram_id, leave FROM work_leave').fetchall()
        return list_leave
# </editor-fold>


if __name__ == '__main__':
    db = sqlite3.connect('/Users/antonponomarev/PycharmProjects/PRO_SOFT/database.db', check_same_thread=False, isolation_level='EXCLUSIVE')
    sql = db.cursor()
    list_user = get_list_users()
    print(list_user)