import logging
import settings


logger_cache = {}

def get_blockme_logger():
    """
    Utility to obtain a standardized logger.
    """
    if logger_cache.get(__name__) is None:
        # initialize and setup logging system
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logger_formatter)
        logger.addHandler(console_handler)

        if settings.LOGFILE is not None:
            file_handler = logging.FileHandler(settings.LOGFILE)
            file_handler.setFormatter(logger_formatter)
            logger.addHandler(file_handler)

        logger_cache[__name__] = logger
        return logger

    else:
        return logger_cache[__name__]
