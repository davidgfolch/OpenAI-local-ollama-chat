import logging
import logging.config

green = "\x1b[32;20m"
grey = "\x1b[38;20m"
blue = "\x1b[34;20m"
yellow = "\x1b[33;20m"
red = "\x1b[31;20m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"
fmt = "%(asctime)s %(levelname)s %(name)s "


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: blue + fmt + reset + "%(message)s",
        logging.INFO: green + fmt + reset + "%(message)s",
        logging.WARNING: yellow + fmt + reset + "%(message)s",
        logging.ERROR: red + fmt + reset + "%(message)s",
        logging.CRITICAL: bold_red + fmt + reset + "%(message)s",
        logging.NOTSET: fmt + "%(message)s"
    }

    def format(self, record):
        try:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)
        except Exception:
            fmt = "%(asctime)s %(levelname)s %(name)s %(message)s"
            return logging.Formatter(fmt).format(record)


# Configure logger to print into console
def initLog(file: str, level=logging.INFO):
    name = file.split("/").pop()
    if (name == "" or name is None):
        name = file
    logger = logging.getLogger(name)
    logger.setLevel(level)
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
