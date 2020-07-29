import json
import requests
import arrow
from requests.adapters import HTTPAdapter

class CurrentPriceDict():

    def getquotes(self, data):
        try:
            quotes = data.get('indicators').get('quote')[0]
            if quotes == {}: return {}
            hist = {}
            hist['timestamp'] = data.get('timestamp')
            hist['symbol'] = data.get('meta').get('symbol')
            hist['open'] = quotes.get('open')
            hist['low'] = quotes.get('low')
            hist['high'] = quotes.get('high')
            hist['close'] = quotes.get('close')
            hist['volume'] = quotes.get('volume')
            return hist
        except:
            return {}

    def getchartresult(self, symbol):
        try:
            params = {}
            params['interval'] = '1d'
            params['range']   = '1d'
            url = f'{self.yfqueryurl}/{symbol}'
            with requests.Session() as session:
                session.mount(url, HTTPAdapter(max_retries=self.request_max_retries))
                response = session.get(url, params=params)
            chartdata = json.loads(response.text).get('chart').get('result')[0]
            return chartdata
        except:
            return None

    def getintradaydata(self, symbol):
        quotes = []
        symbol = symbol.upper()
        data = self.getchartresult(symbol)
        quotes = self.getquotes(data)
        return quotes