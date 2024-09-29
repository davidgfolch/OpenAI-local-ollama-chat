import logging
import logging.config
import re

class CustomFormatter(logging.Formatter):
    green = "\x1b[32;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s %(levelname)s %(name)s "
    FORMATS = {
        logging.DEBUG: grey + fmt + reset + "%(message)s",
        logging.INFO: green + fmt + reset + "%(message)s",
        logging.WARNING: yellow + fmt + reset + "%(message)s",
        logging.ERROR: red + fmt + reset + "%(message)s",
        logging.CRITICAL: bold_red + fmt + reset + "%(message)s"
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# Configure logger to print into console
def initLog(file:str):
    name = file.split("/").pop()
    if (name=="" or name is None): name=file
    logger =  logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = CustomFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

# def initLog(file:str):
#     logging.config.fileConfig('logging.conf')
#     sh = logging.StreamHandler()
#     sh.setFormatter(CustomFormatter())
#     logger =  logging.getLogger(re.sub(r'(.*\/)(^.)+\.py', r'\1',file))
#     logger.addHandler(sh);
#     return logger
