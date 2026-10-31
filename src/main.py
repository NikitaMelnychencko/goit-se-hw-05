from services.parser import ExchangeRateParser
from services.rates import InvalidDaysError, load_rates, parse_days
from services.view import ConsoleTableView
import logging
import asyncio
import sys


async def main(days, parser=None, view=None):
    parser = parser or ExchangeRateParser()
    view = view or ConsoleTableView()
    data = await load_rates(days, parser)
    print(view.render(data))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    raw = sys.argv[1] if sys.argv[1:] else 1
    try:
        days = parse_days(raw)
    except InvalidDaysError as error:
        print(error)
        sys.exit(1)
    try:
        asyncio.run(main(days))
    except Exception as error:
        print(error)
