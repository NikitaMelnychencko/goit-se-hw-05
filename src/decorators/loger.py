from functools import wraps
from pathlib import Path
import aiofiles
import logging
from datetime import datetime
import os

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_FILE = LOG_DIR / "logs.txt"

logging.basicConfig(level=logging.INFO)
def async_loger(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            os.makedirs(LOG_DIR, exist_ok=True)
            async with aiofiles.open(LOG_FILE, mode='a') as f:
                await f.write(
                    f"{datetime.now()} - Calling {func.__name__} with args: {args} and kwargs: {kwargs}\n"
                )
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{e}")
            raise
    return inner