from decorators.loger import async_loger
import aiohttp
from datetime import datetime, timedelta

def get_date(date_diff: int|None = None):
    date = datetime.now().strftime('%d.%m.%Y')
    if date_diff:
        date = (datetime.now() - timedelta(days=date_diff)).strftime('%d.%m.%Y')
    return date

@async_loger
async def get_exchange_rate(date_diff: int|None = None):
    async with aiohttp.ClientSession() as session:
        date = get_date(date_diff)
        response = await session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}')
        return await response.json()
