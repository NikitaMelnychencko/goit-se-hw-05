import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import html
import json
from services.bank import get_exchange_rates
from services.parser import ExchangeRateParser
from services.rates import InvalidDaysError, parse_days
from services.view import HtmlTableView, TableView
logging.basicConfig(level=logging.INFO)


class Server:
    clients = set()

    def __init__(self, parser: ExchangeRateParser | None = None, view: TableView | None = None):
        self.parser = parser or ExchangeRateParser()
        self.view = view or HtmlTableView()

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
                raw = split_message[1] if len(split_message) > 1 else 1
                try:
                    print(raw)
                    days = parse_days(raw)
                except InvalidDaysError as error:
                    await self.send_to_clients(f"{ws.name}: {error}")
                    continue
                raw_rates = await get_exchange_rates(days)
                data = [self.parser.parse(item) for item in raw_rates]
                table = self.view.render(data)
                await self.send_to_clients(f"<!--rates-->{html.escape(ws.name)}:<br>{table}")
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
