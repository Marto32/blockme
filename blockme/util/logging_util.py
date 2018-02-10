import logging
import settings


console_logger_cache = {}
file_logger_cache = {}
insertion_error_logger_cache = {}

def get_blockme_console_logger():
    """
    Utility to obtain a standardized logger.
    """
    logger_name = f'console_{__name__}'
    if console_logger_cache.get(logger_name) is None:
        # initialize and setup logging system
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logger_formatter)
        logger.addHandler(console_handler)

        console_logger_cache[logger_name] = logger
        return logger

    else:
        return console_logger_cache[logger_name]


def get_blockme_file_logger():
    """
    Utility to obtain a standardized logger.
    """
    logger_name = f'file_{__name__}'
    if file_logger_cache.get(logger_name) is None:
        # initialize and setup logging system
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(settings.LOGFILE)
        file_handler.setFormatter(logger_formatter)
        logger.addHandler(file_handler)

        file_logger_cache[logger_name] = logger
        return logger

    else:
        return file_logger_cache[logger_name]


def get_insertion_error_file_logger():
    """
    Utility to obtain a standardized logger.
    """
    logger_name = f'insertion_errors_{__name__}'
    if insertion_error_logger_cache.get(logger_name) is None:
        # initialize and setup logging system
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler = logging.FileHandler(settings.INSERTION_ERROR_FILE)
        file_handler.setFormatter(logger_formatter)
        logger.addHandler(file_handler)

        insertion_error_logger_cache[logger_name] = logger
        return logger

    else:
        return insertion_error_logger_cache[logger_name]
