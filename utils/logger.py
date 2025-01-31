import sys

from aiologger import Logger
from aiologger.formatters.base import Formatter
from aiologger.handlers.files import AsyncFileHandler
from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel

logger = None


async def setup_logger():
    global logger
    # Create logger instance
    logger = Logger(name="api_logger")

    # Create formatter
    formatter = Formatter(
        fmt="{asctime} | {levelname} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    file_handler = AsyncFileHandler(
        filename="logs/api.log",
        mode="a",
        encoding="utf-8",
    )
    stream_handler = AsyncStreamHandler(stream=sys.stdout)
    file_handler.formatter = formatter
    stream_handler.formatter = formatter
    logger.add_handler(file_handler)
    logger.add_handler(stream_handler)

    logger.level = LogLevel.INFO

    return logger


async def log_info(message: str):
    if logger is not None: await logger.info(message)

async def log_error(message: str):
    if logger is not None: await logger.error(message)