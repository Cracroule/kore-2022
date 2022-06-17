import os

from datetime import datetime
# import logging

FILE = "game.log"
IS_KAGGLE = os.path.exists("/kaggle_simulations")


class Logger(object):
    def __init__(self, log_file=FILE):
        if not IS_KAGGLE:
            if os.path.exists(log_file):
                os.remove(log_file)

            with open(log_file, "a") as file_object:
                file_object.write(str(datetime.now().time()) + ": " + "init logger" + "\n")

            self.log_file = log_file

    def info(self, msg):
        if not IS_KAGGLE:
            with open(self.log_file, "a") as file_object:
                file_object.write(str(datetime.now().time()) + " [info]: " + msg + "\n")

    def debug(self, msg):
        if not IS_KAGGLE:
            with open(self.log_file, "a") as file_object:
                file_object.write(str(datetime.now().time()) + " [debug]: " + msg + "\n")


def init_logger(logger):
    if not IS_KAGGLE:
        print("init_logger")
        if os.path.exists(logger.log_file):
            os.remove(logger.log_file)

    with open(logger.log_file, "a") as file_object:
        file_object.write(str(datetime.now().time()) + ": " + "init_logger" + "\n")


logger = Logger()



# LEVEL = logging.DEBUG if not IS_KAGGLE else logging.INFO
# LOGGING_ENABLED = True
#
#
# class _FileHandler(logging.FileHandler):
#     def emit(self, record):
#         if not LOGGING_ENABLED:
#             return
#
#         if IS_KAGGLE:
#             print(self.format(record))
#         else:
#             super().emit(record)
#
#
# def init_logger(_logger):
#     if not IS_KAGGLE:
#         if os.path.exists(FILE):
#             os.remove(FILE)
#
#     while _logger.hasHandlers():
#         _logger.removeHandler(_logger.handlers[0])
#
#     _logger.setLevel(LEVEL)
#     ch = _FileHandler(FILE)
#     ch.setLevel(LEVEL)
#     formatter = logging.Formatter(
#         "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H-%M-%S"
#     )
#     ch.setFormatter(formatter)
#     _logger.addHandler(ch)
#
#
# logger = logging.getLogger()


