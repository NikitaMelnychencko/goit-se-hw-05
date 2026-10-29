import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import html
import json
from services.bank import get_exchange_rate
from services.parser import ExchangeRateParser
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
                date_diff = None
                try:
                    if len(split_message) == 1:
                        date_diff = None
                    else:
                        date_diff = int(split_message[1])
                except ValueError:
                    return await self.send_to_clients(f"{ws.name}: Invalid command")
                if date_diff and date_diff > 10:
                    return await self.send_to_clients(f"{ws.name}: Invalid command. Date difference must be less than 10.")
                tasks = []
                for i in range(date_diff):
                    tasks.append(get_exchange_rate(i))
                exchange_rate = await asyncio.gather(*tasks)
                data = [self.parser.parse(item) for item in exchange_rate]
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
