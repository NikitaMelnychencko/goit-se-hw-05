from functools import wraps
import aiofiles
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
def async_loger(func):
    @wraps(func)
    async def inner(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            os.makedirs('logs', exist_ok=True)
            async with aiofiles.open('logs/logs.txt', mode='a') as f:
                await f.write(
                    f"{datetime.now()} - Calling {func.__name__} with args: {args} and kwargs: {kwargs}\n"
                )
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{e}")
            raise
    return inner