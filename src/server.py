import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import html
import httpx
import json
from datetime import datetime, timedelta
from decorators.loger import async_loger

logging.basicConfig(level=logging.INFO)


def _cell(value):
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def format_rates_table(payload: dict) -> str:
    date = html.escape(str(payload.get("date", "—")))
    base = html.escape(str(payload.get("baseCurrencyLit", "UAH")))
    headers = ("Валюта", "НБУ продаж", "НБУ купівля", "Продаж", "Купівля")
    head = "".join(f"<th>{html.escape(header)}</th>" for header in headers)

    rows = []
    for item in payload.get("exchangeRate") or []:
        currency = item.get("currency")
        if not currency:
            continue
        cells = (
            currency,
            _cell(item.get("saleRateNB")),
            _cell(item.get("purchaseRateNB")),
            _cell(item.get("saleRate")),
            _cell(item.get("purchaseRate")),
        )
        rows.append("<tr>" + "".join(f"<td>{html.escape(cell)}</td>" for cell in cells) + "</tr>")

    body = "".join(rows) or '<tr><td colspan="5">немає курсів за цю дату</td></tr>'
    return (
        f'<p class="rates-caption">Дата: {date} &nbsp; База: {base}</p>'
        f'<table class="rates"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'
    )


@async_loger
async def get_exchange_rate(date_diff: int|None = None):
    async with httpx.AsyncClient() as client:
        date = datetime.now().strftime('%d.%m.%Y')
        if date_diff:
            date = (datetime.now() - timedelta(days=date_diff)).strftime('%d.%m.%Y')
        response = await client.get(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}')
        return response.json()

class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            split_message = message.split(' ')
            if split_message[0] == 'exchange':
                date_diff = None
                try:
                    if len(split_message) == 1:
                        date_diff = None
                    else:
                        date_diff = int(split_message[1])
                except ValueError:
                    return await self.send_to_clients(f"{ws.name}: Invalid command")
                payload = await get_exchange_rate(date_diff)
                logging.info(
                    "Exchange rate:\n%s",
                    json.dumps(payload, indent=4, ensure_ascii=False),
                )
                table = format_rates_table(payload)
                await self.send_to_clients(
                    f"<!--rates-->{html.escape(ws.name)}:<br>{table}"
                )
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
