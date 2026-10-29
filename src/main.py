from services.bank import get_exchange_rate
from services.parser import ExchangeRateParser
from services.view import ConsoleTableView
import logging
import asyncio

def parse_input(user_input):
    print(user_input)
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def validation_command(command):
  if command.isdigit() and int(command) <= 10:
    return True
  else:
    return False

async def main(command, args, parser=None, view=None):
  parser = parser or ExchangeRateParser()
  view = view or ConsoleTableView()
  tasks = []
  try:
    for i in range(int(command)):
      tasks.append(get_exchange_rate(i))
    exchange_rate = await asyncio.gather(*tasks)
    data = [parser.parse(item) for item in exchange_rate]
    print(view.render(data))
  except Exception as error:
    print(error)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    user_input = input("Enter a command: ")
    try:
        command, *args = parse_input(user_input)
        if validation_command(command):
          asyncio.run(main(command, args))
        else:
          print("Invalid command.")
    except Exception:
        print("Invalid command.")
