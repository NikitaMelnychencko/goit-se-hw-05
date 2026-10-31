from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    def parse(self, data: dict) -> dict:
        pass

class ExchangeRateParser(Parser):
    CURRENCIES = ('USD', 'EUR')

    def parse(self, data: dict) -> dict:
        by_currency = {
            item['currency']: item
            for item in data['exchangeRate']
            if item.get('currency') in self.CURRENCIES
        }
        usd = by_currency.get('USD', {})
        eur = by_currency.get('EUR', {})
        return {
            data['date']: {
                'USD': usd.get('saleRate'),
                'EUR': eur.get('saleRate'),
                'USD_BUY': usd.get('purchaseRate'),
                'EUR_BUY': eur.get('purchaseRate'),
            }
        }


def data_to_parse(data: dict) -> dict:
    return ExchangeRateParser().parse(data)
