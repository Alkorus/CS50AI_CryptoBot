#!/usr/bin/env python3

import aiohttp
import asyncio
import time
import requests
from datetime import datetime

import concurrent.futures



STABLE_COIN_REFERENCE = 'USDT'

class BiAPIGeneral:

    API_URL = 'https://api.binance.com/api/v3'
    LOWEST_PRICE = 1
    HIGHEST_PRICE = 300
    BASE_INTERVAL = '1m'

    def __init__(self):
        print("init API class")
        

    
    def get_all_symbols(self, ref, lowest_price = LOWEST_PRICE, highest_price = HIGHEST_PRICE):
        route_url = '/ticker/24hr'
        #url = self.API_URL + route_url
        url = f'{self.API_URL}{route_url}'
        cryptos = []
        print(url)
        response = requests.get(url)
        if(response.status_code == requests.codes.ok):
            for crypto in response.json():
                symbol = crypto['symbol']
                price = float(crypto['lastPrice'])
                if(symbol.endswith(ref) and price > lowest_price and price < highest_price):
                    #print(price)
                    symbol = symbol[:-len(ref)]
                    if not symbol.endswith("DOWN"):
                        cryptos.append(symbol)
            return cryptos
        # async with session.get(url) as response:
        #     if(response.status != 200):
        #         return await response.text()
        #     else:
        #         for crypto in await response.json():
        #             symbol = crypto['symbol']
        #             price = float(crypto['price'])
        #             if(symbol.endswith(ref) and price > 1 and price < 500):
        #                 #print(price)
        #                 symbol = symbol[:-len(ref)]
        #                 cryptos.append(symbol)
        #         return cryptos
    

    def get_klines(self, symbol, ref, **kwargs):
        route_url = '/klines'
        start = kwargs['start'] if 'start' in kwargs else ''
        end = kwargs['end'] if 'end' in kwargs else ''
        symbol = f'{symbol}{ref}'
        base_url = f'{self.API_URL}{route_url}?symbol={symbol}&interval={self.BASE_INTERVAL}'
        # print(url)

        klines = []
        #print(url)
        if start != '' or end != '':
            # when the looked period is bound, do as many calls is necessary to get all the klines
            endPeriod = start
            while endPeriod < end:
                #print(f'start: {self.convert_time_bi_to_py(endPeriod)}')
                #print(f'end: {self.convert_time_bi_to_py(end)}')
                url = f'{base_url}&startTime={endPeriod}'
                url = f'{url}&endTime={end}'
                response = requests.get(url)
                if(response.status_code == requests.codes.ok):
                    for k in response.json():
                        #print(k)
                        kline = dict(openTime = k[0], open = k[1], high = k[2], low = k[3], close = k[4], volume = k[5], closeTime = k[6], quoteVolume = k[7], nbTrades = k[8], baseAssetVolume = k[9], quoteAssetVolume = k[10])
                        if len(klines) == 0 or kline['openTime'] != klines[-1]['openTime'] :
                            klines.append(kline)
                    endPeriod = klines[-1]['closeTime']
                else:
                    break
                
            
        else:
            if(start != ''):
                base_url = f'{base_url}&startTime={start}'
            if(end != ''):
                base_url = f'{base_url}&endTime={end}'

            response = requests.get(base_url)

            if(response.status_code == requests.codes.ok):
                for k in response.json():
                    #print(k)
                    kline = dict(openTime = k[0], open = k[1], high = k[2], low = k[3], close = k[4], volume = k[5], closeTime = k[6], quoteVolume = k[7], nbTrades = k[8], baseAssetVolume = k[9], quoteAssetVolume = k[10])
                    klines.append(kline)
                #print(len(klines))


        return klines

        # async with session.get(url) as response:
        #     if(response.status != 200):
        #         return await response.text()
        #     else:
        #         for k in await response.json():
        #             #print(k)
        #             kline = dict(openTime = k[0], open = k[1], high = k[2], low = k[3], close = k[4], volume = k[5], closeTime = k[6], quoteVolume = k[7], nbTrades = k[8], baseAssetVolume = k[9], quoteAssetVolume = k[10])
        #             klines.append(kline)
        #         print(klines[0])
        #         return klines

    def get_immediate_ticker(self, symbol, ref):
        route_url = '/ticker/price'
        symbol = f'{symbol}{ref}'
        url = f'{self.API_URL}{route_url}?symbol={symbol}'
        response = requests.get(url)

        if(response.status_code == requests.codes.ok and 'price' in response.json()):
            return response.json()['price']
    
    def convert_time_bi_to_py(self, timestamp:int):
        return datetime.fromtimestamp(timestamp / 1000)
    
    def convert_time_py_to_bi(self, time:datetime):
        return int(datetime.timestamp(time) * 1000)

    def get_ref_stable_conversion(self, ref):
        conversion = 1
        
        if ref == STABLE_COIN_REFERENCE:
            return conversion
        
        route_url = '/ticker/price'
        parameter_call = '?symbol='
        symbol_parameter = f'{ref}{STABLE_COIN_REFERENCE}'
        url = f'{self.API_URL}{route_url}{parameter_call}{symbol_parameter}'

        response = requests.get(url)

        if(response.status_code == requests.codes.bad_request):
            symbol_parameter = f'{STABLE_COIN_REFERENCE}{ref}'
            url = f'{self.API_URL}{route_url}{parameter_call}{symbol_parameter}'
            response = requests.get(url)
        #print(url)
        if(response.status_code == requests.codes.ok):
            exchange = response.json()
            symbol = exchange['symbol']
            price = float(exchange['price'])
            if(symbol.endswith(STABLE_COIN_REFERENCE)):
                conversion = price
            else:
                conversion = 1/price
            return conversion

async def main():
    #start_time = time.time()
    print("test")
    ref = 'USDT'
    api = BiAPIGeneral()
    time = api.convert_time_bi_to_py(1648128059999)
    print(time)
    print(api.convert_time_py_to_bi(time))
    print(api.get_immediate_ticker('GLMR','USDT'))
    
    # async with aiohttp.ClientSession() as session:
    #     cryptos = await api.get_all_symbols(session, ref)
    #     #print(cryptos)
    #     print(len(cryptos))
    #     #klines = await api.get_klines(session, cryptos[0], ref, start = '1639672020000', end = '1639672139999')
    #     # for crypto in cryptos:
    #     #     klines = api.get_klines(session, crypto, ref)
    #         #print(klines[0])
    #     #print(klines)

    #     # Spread the calls for the klines into 10 threads to speed-up the process, passes from 75 to 8.5 seconds
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #         executor.map(api.get_klines, [session] * len(cryptos), cryptos, [ref] * len(cryptos))

    # print(f'elapsed time: {time.time() - start_time} seconds')

if __name__ == '__main__':
    print('test?')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())