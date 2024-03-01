from config_data.config import load_config, Config
from module.data_base import get_list_admins
import logging

config: Config = load_config()


def chek_admin(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('chek_manager')
    list_superadmin = config.tg_bot.admin_ids.split(',')
    print("list_superadmin", list_superadmin, str(telegram_id) in list_superadmin)
    return str(telegram_id) in list_superadmin

def chek_admin_1(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('chek_manager')
    list_admin = [admin[0] for admin in get_list_admins()]
    print("list_admin", list_admin, telegram_id in list_admin)
    return telegram_id in list_admin



