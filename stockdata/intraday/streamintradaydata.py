import pandas as pd
import arrow
from glob import glob
from itertools import repeat
from concurrent.futures import ThreadPoolExecutor

from stockdata.intraday.getintradaydata import IntraDayDataDict
from stockdata.config import Config
from stockdata.sqlite import SqLite
from stockdata.utils import Utility


class IntraDayData(IntraDayDataDict, Config):

    def __init__(self):
        Config.__init__(self)

    @SqLite.connector
    def getsymbols(self, exchange, n_symbols):
        if exchange == 'NSE': query = f"select symbol || '.NS' as symbol from symbols where innse = 1 "
        if exchange == 'BSE': query = f"select symbol || '.BO' as symbol from symbols where inbse = 1 "
        if n_symbols > 0: query += f'limit {n_symbols}'
        df = pd.read_sql(query, SqLite.conn)
        return list(df.symbol)

    def processdf(self, df):
        df['symbol'] = df['symbol'].apply(lambda x: x.split('.')[0].replace('^', ''))
        df = Utility.addtimefeatures(df)
        return df

    @Utility.timer
    def download(self, exchange, date, n_symbols):
        symbols = self.getsymbols(exchange, n_symbols)
        print(f'Downloading intraday prices from yahoo finance for {date} {exchange.upper()} {len(symbols)} symbols', end='...', flush=True)
        nthreads = min(len(symbols), int(self.maxthreads))
        with ThreadPoolExecutor(max_workers=nthreads) as executor:
            results = executor.map(self.getintradaydata, symbols, repeat(date))
        values = list(results)
        dfs = [pd.DataFrame(d) for d in values]
        df = pd.concat(dfs, ignore_index=True).dropna()
        if df.empty:
            print('No data !')
            return None
        df = self.processdf(df)
        df = df.astype({'volume': int})
        print('Completed!')
        return df

x = IntraDayData()
df = x.download('NSE', '2020-07-20', 200)