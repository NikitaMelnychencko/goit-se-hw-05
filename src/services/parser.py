class ExchangeRateParser:
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
                'USD': usd.get('saleRateNB'),
                'EUR': eur.get('saleRateNB'),
                'USD_BUY': usd.get('purchaseRateNB'),
                'EUR_BUY': eur.get('purchaseRateNB'),
            }
        }


def data_to_parse(data: dict) -> dict:
    return ExchangeRateParser().parse(data)
