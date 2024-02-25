from config_data.config import load_config, Config
import logging

config: Config = load_config()


def chek_admin(telegram_id: int) -> bool:
    """
    Проверка на администратора
    :param telegram_id: id пользователя телеграм
    :return: true если пользователь администратор, false в противном случае
    """
    logging.info('chek_manager')
    list_manager = config.tg_bot.admin_ids.split(',')
    print(list_manager)
    return str(telegram_id) in list_manager





