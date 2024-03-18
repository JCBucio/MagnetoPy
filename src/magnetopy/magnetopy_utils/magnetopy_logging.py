#!/usr/bin/env python3
import logging


class MagnetopyLogging(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.__green: str = "\x1b[32m"
        self.__white: str = "\x1b[97m"
        self.__yellow: str = "\x1b[33m"
        self.__red: str = "\x1b[31m"
        self.__bold_red: str = "\x1b[31;1m"
        self.__reset: str = "\x1b[0m"
        self.__format: str = "%(asctime)s - %(name)s (%(filename)s:%(lineno)d) - %(levelname)s: %(message)s"

        self.FORMATS: dict = {
            logging.DEBUG: self.__green + self.__format + self.__reset,
            logging.INFO: self.__white + self.__format + self.__reset,
            logging.WARNING: self.__yellow + self.__format + self.__reset,
            logging.ERROR: self.__red + self.__format + self.__reset,
            logging.CRITICAL: self.__bold_red + self.__format + self.__reset
        }

        self.magnetopy_logging = None

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the specified record as text.

        :param record: Represents an event being logged.
        :type record: logging.LogRecord
        :return: String format
        :rtype: str
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
        
    @staticmethod
    def create_magnetopy_logging(logger: str) -> logging.getLogger:
        """
        Create a Logger or get one if it already exists. Return the Logger.

        :param logger: Logger name
        :type logger: str
        :return: Logger
        :rtype: logging.getLogger
        """

        if logger in logging.root.manager.loggerDict:
            return logging.getLogger(logger)
        else:
            magnetopy_logging = logging.getLogger(logger)
            magnetopy_logging.propagate = False
            magnetopy_logging.setLevel(logging.DEBUG)

            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)

            ch.setFormatter(MagnetopyLogging())

            magnetopy_logging.addHandler(ch)
            return magnetopy_logging