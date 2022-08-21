#!/usr/bin/env python3

import asyncio
from asyncio.windows_events import NULL
import time
import schedule

import concurrent.futures

from modeles.crypto import Crypto
from modeles.trade_parent import Trade_Parent
from modeles.trade_trend_testA import Trade_Trend_TestA
from modeles.trade_trend_testB import Trade_Trend_TestB
from modeles.trade_trend_testC import Trade_Trend_TestC
from modeles.trade_trend_testD import Trade_Trend_TestD
from modeles.trade_RSI_A import Trade_RSI_A
from modeles.trade_RSI_B import Trade_RSI_B
from modeles.trade_RSI_C import Trade_RSI_C
from modeles.trade_RSI_D import Trade_RSI_D
from modeles.trade_RSI_E import Trade_RSI_E
from modeles.trade_RSI_F import Trade_RSI_F
from modeles.BiAPIGeneral import BiAPIGeneral
from helpers.excelIO import ExcelIO

class Main:
    REFERENCE_CRYPTO = 'USDT'

    def __init__(self):
        print("init Main class")

    def initialise_cryptos(self, **kwargs):
        cryptos = kwargs['cryptos'] if 'cryptos' in kwargs else []
        api = kwargs['api'] if 'api' in kwargs else BiAPIGeneral()
        c = api.get_all_symbols(self.REFERENCE_CRYPTO)

        for crypto in c:
            crypto = Crypto(crypto)
            cryptos.append(crypto)
            #print(cryptos[-1].symbol())
        print(len(cryptos))

        #self.assemble_crypto(cryptos[0])

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.assemble_crypto, cryptos, [api] * len(cryptos))

        temp_cryptos = []
        for crypto in cryptos:
           if len(crypto.averages.items) > 0:
               temp_cryptos.append(crypto)
        
        cryptos = temp_cryptos
        print(len(cryptos))

        if(len(cryptos)):
            crypto = cryptos[0]
            #print(crypto.symbol())
            #print(crypto.openTime())
            return crypto.openTime()

    
    def assemble_crypto(self, crypto: Crypto, api: BiAPIGeneral):

        kwargs = dict()
        if(crypto.openTime() != NULL):
            kwargs = dict(start = crypto.openTime()+1)
            
        #print(crypto.symbol())

        klines = api.get_klines(crypto.symbol(), self.REFERENCE_CRYPTO, **kwargs)
        #print(len(klines))
        #print(f'{crypto.symbol()} with {len(klines)} lines')

        for kline in klines:
            crypto.addResults(**kline)
        #print(f'crypto: {crypto.symbol()}, ems20: {crypto.averages.ems20()}')

    def update(self, cryptos, **kwargs):

        api = kwargs['api'] if 'api' in kwargs else BiAPIGeneral()
        print(f'begin updating {time.time()}')
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.assemble_crypto, cryptos, [api] * len(cryptos))
        #self.assemble_crypto(cryptos[0], api)

        if(len(cryptos)):
            crypto:Crypto = cryptos[0]
            #print(f'{crypto.symbol()} {crypto.openTime()}')
        print(f'end updating: {time.time() - start_time} seconds')
        for crypto in cryptos:
            if not 'trendA' in crypto.trade_tests():
                Trade_Trend_TestA.test_entry(crypto)
            if not 'trendB' in crypto.trade_tests():
                Trade_Trend_TestB.test_entry(crypto)
            if not 'trendC' in crypto.trade_tests():
                Trade_Trend_TestC.test_entry(crypto)
            if not 'trendD' in crypto.trade_tests():
                Trade_Trend_TestD.test_entry(crypto)
            if not 'RSI-A' in crypto.trade_tests():
                Trade_RSI_A.test_entry(crypto)
            if not 'RSI-B' in crypto.trade_tests():
                Trade_RSI_B.test_entry(crypto)
            if not 'RSI-C' in crypto.trade_tests():
                Trade_RSI_C.test_entry(crypto)
            if not 'RSI-D' in crypto.trade_tests():
                Trade_RSI_D.test_entry(crypto)
            if not 'RSI-E' in crypto.trade_tests():
                Trade_RSI_E.test_entry(crypto)
            if not 'RSI-F' in crypto.trade_tests():
                Trade_RSI_F.test_entry(crypto)

            keys = []
            for key in crypto.trade_tests().keys():
                keys.append(key)
            for key in keys:
                type(crypto.trade_tests()[key]).test_exit(crypto)
            # else:
            #     trade_type = type(crypto.trade())
            #     #print(trade_type)
            #     if trade_type == Trade_Trend_Test:
            #         Trade_Trend_Test.test_exit(crypto)
        print(f'end tests: {time.time() - start_time} seconds')

        i = 0
        for crypto in cryptos:
            for message in crypto.message():
                #print(message)
                ExcelIO.enter_record(**message)
                crypto._message = []
                i += 1
            # if crypto.message() != NULL:
            #     ExcelIO.enter_record(**crypto.message())
            #     crypto._message = NULL
            #     i += 1
        print(f'end records: {time.time() - start_time} seconds with {i} new reports')


        #crypto = cryptos[5]
        #print(f'{crypto.symbol()}, open: {crypto.open()}, close: {crypto.close()}, gain: {crypto.averages.RSI_gain()}, loss: {crypto.averages.RSI_loss()}, RSI: {crypto.averages.RSI()}')

        
        



async def main():
    print('main')

    main = Main()
    api = BiAPIGeneral()
    cryptos = []
    last_update:int
    
    # c = Crypto('test')
    # c._trade = Trade_Trend_Test(c, 10, 1)
    # print(type(c.trade()))
    # if type(c.trade()) == Trade_Trend_Test:
    #     print("mêmes")
    

    start_time = time.time()

    last_update = main.initialise_cryptos(api = api, cryptos = cryptos)
    print(last_update)

    print(f'elapsed time: {time.time() - start_time} seconds')

    schedule.every().minutes.at(":05").do(main.update, cryptos = cryptos, api = api)
    print('before loop')

    while True:
        schedule.run_pending()
        time.sleep(1)

    # start_time = time.time()
    # print("test")
    # ref = 'USDT'
    # api = BiAPIGeneral()
    # cryptos = {}
    
    # async with aiohttp.ClientSession() as session:
    #     c = await api.get_all_symbols(session, ref)
    #     #print(cryptos)
    #     print(len(c))

    #     for crypto in c:
    #         cryptos[crypto] = Crypto(crypto)
    #     print(len(cryptos))

    #     # Spread the calls for the klines into 10 threads to speed-up the process, passes from 75 to 8.5 seconds
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    #         executor.map(api.get_klines, [session] * len(c), c, [ref] * len(c))

    # print(f'elapsed time: {time.time() - start_time} seconds')



if __name__ == '__main__': 
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())