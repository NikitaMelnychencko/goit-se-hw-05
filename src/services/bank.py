from decorators.loger import async_loger
import aiohttp
import asyncio
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
        try:
            response = await session.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}')
            response.raise_for_status()
            return await response.json()
        except Exception as error:
            if error.status == 400:
                print('Некоректно переданні данні')
            elif error.status == 404:
                print('Вибачте але данні не знайдені')
            elif error.status == 500:
                print('Упс здається банк не выдповыдає. Спробуйте пізніше.')
            else:
                print(error)
            return None

async def get_exchange_rates(days: int) -> list:
    raw = await asyncio.gather(*(get_exchange_rate(i) for i in range(days)))
    return [item for item in raw if item is not None]
