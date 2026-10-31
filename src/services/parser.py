from abc import ABC, abstractmethod

class Parser(ABC):
    @abstractmethod
    def parse(self, data: dict) -> dict:
        pass

class ExchangeRateParser(Parser):
    CURRENCIES = ('USD', 'EUR')
    EMPTY_RATES = {
        'USD': None,
        'EUR': None,
        'USD_BUY': None,
        'EUR_BUY': None,
    }

    def parse(self, data: dict) -> dict:
        exchange_rate = data.get('exchangeRate') or []
        if not exchange_rate:
            return {data['date']: dict(self.EMPTY_RATES)}

        by_currency = {
            item['currency']: item
            for item in exchange_rate
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
