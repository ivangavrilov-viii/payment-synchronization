from loguru import logger
import datetime
import settings
import os


def create_logger():
    """ Create new file for loguru logging or return existing log file """

    path = os.path.dirname(os.path.abspath(__file__))
    logs_path = os.path.join(path, settings.LOGS_URL)
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    today = datetime.datetime.now()
    file_path = os.path.join(logs_path, f'log_{today.day}_{today.month}_{today.year}.log')

    if not os.path.exists(file_path):
        logger.add(
            sink=file_path,
            level='DEBUG',
            format="{time} | {level} | {message}",
            encoding='utf-8',
            mode='a+',
            # compression="zip"
        )

        # Remove default handler that write logs in command line
        logger.remove(0)
    else:
        logger.configure(
            handlers=[
                dict(
                    sink=file_path,
                    level='DEBUG',
                    format="{time} | {level} | {message}",
                    encoding='utf-8',
                    mode='a+',
                    # compression="zip"
                )
            ]
        )

    return logger


def logging(text, log_type):
    logger_file = create_logger()

    if log_type == 'error':
        logger_file.error(text)
    elif log_type == 'warning':
        logger_file.warning(text)
    elif log_type == 'critical':
        logger_file.critical(text)
    elif log_type == 'info':
        logger_file.info(text)
    elif log_type == 'debug':
        logger_file.debug(text)
    elif log_type == 'success':
        logger_file.success(text)
    else:
        logger_file.info(text)
