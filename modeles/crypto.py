#!/usr/bin/env python3

#from queue import Queue

from asyncio.windows_events import NULL
import numpy as np

QUEUE_MAX_LEN = 200
NO_POSITION = 0
LONG_POSITION = 1
SMA_LENGTH = [9, 10, 15, 20, 65, 200]
EMS_LENGTH = [9, 10, 15, 20, 65, 200]
RSI_SIZE = 14

class Crypto:

    # to create a new object Crypto, you need it's symbol
    def __init__(self, symbol):
        self._symbol = symbol
        self.averages = self.Queue(QUEUE_MAX_LEN)
        self._openTime = NULL
        self._position = NO_POSITION
        self._trade_tests = {}
        self._message = []
    
    def symbol(self):
        return self._symbol

    # parameters for the latest candlestick
    def high(self):
        return float(self._high)
    
    def low(self):
        return float(self._low)

    def open(self):
        return float(self._open)

    def close(self):
        return float(self._close)
       
    def openTime(self):
        return self._openTime

    def volume(self):
        return float(self._volume)

    def trade_tests(self):
        return self._trade_tests
    
    def message(self):
        return self._message

    def setPosition(self, position):
        self._position = position

    # assemble the complete state of the crypto
    def giveState(self):
        SMAS = [9, 10, 15, 20, 65, 200]
        TREND_LENGTHS = [5, 15, 30, 60, 120, 200]

        state = []
        # start with basic infos
        state.append(self._openTime)    # to change for relative time in day
        state.append(self._volume)
        state.append(self._position)
        state.append(float(self._high))
        state.append(float(self._low))
        state.append(float(self._open))
        state.append(float(self._close))
        # then those infos relative to close
        state.append(float((self._high - self._close)/self._close))
        state.append(float((self._low - self._close)/self._close))
        state.append(float((self._open - self._close)/self._close))
        # relative statistical values for crypto
        for ems in EMS_LENGTH:
            state.append(float((self.averages.ems(ems) - self._close)/self._close))
        for sma in SMA_LENGTH:
            state.append(float((self.averages.sma(sma) - self._close)/self._close))
        state.append(self.averages.RSI())
        # adding the trend variations and their R2 for different time spans
        for length in TREND_LENGTHS:
            trend = self.averages.trendIndex(length)
            state.append(trend['trend'])
            state.append(trend['R2'])


    
    
    # Receive the latest candlestick values, saves them and update the averages
    def addResults(self, **kwargs):
        #print(f"{kwargs['openTime']}, {kwargs['open']}, {kwargs['close']}")
        if 'openTime' in kwargs:
            # if a timestamp for the candle is given, make sure it is different than the presviously saved one
            if(self._openTime == NULL or self._openTime != kwargs['openTime']):
                self._openTime = kwargs['openTime']
                if 'high' in kwargs:
                    self._high = kwargs['high']
                if 'low' in kwargs:
                    self._low = kwargs['low']
                if 'open' in kwargs:
                    if len(self.averages.items) > 0:
                        self._open = self.averages.items[0]
                    else:
                        self._open = kwargs['open']
                if 'close' in kwargs:
                    self._close = float(kwargs['close'])
                    self.averages.enqueue(self._close)
                if 'volume' in kwargs:
                    self._volume = kwargs['volume']
                if 'open' in kwargs and 'close' in kwargs and 'volume' in kwargs:
                    if self.volume() > 0:
                        self.averages.updateRSI(self.open(), self.close())
        else:
            if 'high' in kwargs:
                self._high = kwargs['high']
            if 'low' in kwargs:
                self._low = kwargs['low']
            if 'open' in kwargs:
                if len(self.averages.items) > 0:
                    self._open = self.averages.items[0]
                else:
                    self._open = kwargs['open']
            if 'close' in kwargs:
                self._close = float(kwargs['close'])
                self.averages.enqueue(self._close)
            if 'volume' in kwargs:
                self._volume = kwargs['volume']
            if 'open' in kwargs and 'close' in kwargs and 'volume' in kwargs:
                if self.volume() > 0:
                    self.averages.updateRSI(self.open(), self.close())
        #print(len(self.averages.items))
        

    class Queue:
        # TODO: switch to inner class
        # https://www.datacamp.com/community/tutorials/inner-classes-python

        # On creation, the queue registers it's maximum length
        def __init__(self, length):
            self.items = []
            self._length = length
            # Exponential moving average (initial value in the negative to indicate it hasn't been calculated yet)
            self._ems9 = -1
            self._ems10 = -1
            self._ems15 = -1
            self._ems20 = -1
            self._ems65 = -1
            self._ems200 = -1

            self._ems = {}

            self._RSI_gain = 0
            self._RSI_loss = 0
            self._RSI = 50

        # properties of the EMSs
        def ems9(self):
            return self._ems9

        def ems10(self):
            return self._ems10

        def ems15(self):
            return self._ems15

        def ems20(self):
            return self._ems20

        def ems65(self):
            return self._ems65
        
        def ems200(self):
            return self._ems200
        
        def ems(self, length):
            if not length in EMS_LENGTH:
                return -1   # EMS length not available
            return self._ems[length]

        
        def RSI_gain(self):
            return self._RSI_gain
        def RSI_loss(self):
            return self._RSI_loss
        def RSI(self):
            return self._RSI
    
        # Add a new element to the queue
        def enqueue(self, item):
            self.items.insert(0, item)  # insert at begining of Queue

            # If the queue has attained it's max length, pop the last to only keep 200
            if len(self.items) > self._length:
                self.items.pop()
                # We also wait for that momemt to start calculating the ems
                if self.ems(EMS_LENGTH[0]) < 0:
                    for length in EMS_LENGTH:
                        self._ems[length] = self.sma(length)
                else:
                    for length in EMS_LENGTH:
                        self._ems[length] = (item - self._ems[length]) * (2 / (length + 1)) + self._ems[length]

                # if self._ems10 < 0:
                #     self._ems9 = self.sma(9)
                #     self._ems10 = self.sma(10)
                #     self._ems15 = self.sma(15)
                #     self._ems20 = self.sma(20)
                #     self._ems65 = self.sma(65)
                #     self._ems200 = self.sma(200)
                # else:
                #     # The EMS is readjusted at each cycle
                #     self._ems9 = (item - self._ems9) * (2 / (9 + 1)) + self._ems9 
                #     self._ems10 = (item - self._ems10) * (2 / (10 + 1)) + self._ems10
                #     self._ems15 = (item - self._ems15) * (2 / (15 + 1)) + self._ems15
                #     self._ems20 = (item - self._ems20) * (2 / (20 + 1)) + self._ems20
                #     self._ems65 = (item - self._ems65) * (2 / (65 + 1)) + self._ems65
                #     self._ems200 = (item - self._ems200) * (2 / (200 + 1)) + self._ems200


        # Getting the appropriate length SMA
        def sma(self, length):
            # Verify that the length asked for the mean isn't greater than the registered number of values
            if length > len(self.items):
                return sum(self.items) / len(self.items)
            elif length == 0:
                return 0
            else:
                return sum(self.items[0:length]) / length

        # Rough calculation of the general % of variation of the title for each time interval
        def trendIndex(self, length):
            # if parameter length is -1, we want the whole length of the recorded datas
            if length < 0 or length > len(self.items):
                reverse = list(reversed(self.items))
            else:
                reverse = list(reversed(self.items[0:length]))
            mean = self.sma(len(reverse))
            x = np.arange(0, len(reverse))
            y = np.array(reverse)
            z = np.polyfit(x, y, 1)

            correlation_matrix = np.corrcoef(x, y)
            correlation_xy = correlation_matrix[0,1]
            r_squared = correlation_xy**2

            response = {'trend':100*z[0] / mean, 'R2': r_squared}
            #print (z[0])
            return response

        # Calculation of the RSI14 for the crypto
        def updateRSI(self, open, close):
            
            variation = 100*(close - open)/open
            if len(self.items) < RSI_SIZE:
                if variation > 0: self._RSI_gain += variation
                else: self._RSI_loss -= variation       # -- == +|-|
            elif len(self.items) == RSI_SIZE:
                if variation > 0: self._RSI_gain += variation
                else: self._RSI_loss -= variation       # -- == +|-|
                self._RSI_gain = self._RSI_gain/RSI_SIZE
                self._RSI_loss = self._RSI_loss/RSI_SIZE
            else:
                if variation > 0:
                    self._RSI_gain = ((RSI_SIZE-1)*self._RSI_gain + variation)/RSI_SIZE
                    self._RSI_loss = ((RSI_SIZE-1)*self._RSI_loss)/RSI_SIZE
                else:
                    self._RSI_gain = ((RSI_SIZE-1)*self._RSI_gain)/RSI_SIZE
                    self._RSI_loss = ((RSI_SIZE-1)*self._RSI_loss - variation)/RSI_SIZE

                if self._RSI_loss == 0: RS = 100
                else: RS = self._RSI_gain/self._RSI_loss
                self._RSI = 100 - 100/(1+RS)






def main():
    print("test")
    # crypto = Crypto('test')
    # kline = {'openTime': 1542270060000, 'open': '449.92000000', 'high': '453.69000000', 'low': '449.75000000', 'close': '453.26000000', 'volume': '231.37886000', 'closeTime': 1542270119999, 'quoteVolume': '104350.73942990', 'nbTrades': 106, 'baseAssetVolume': '146.88690000', 'quoteAssetVolume': '66228.08371000'}
    # print(len(kline))
    # #print(**kline)
    # print(crypto.symbol())
    # crypto.addResults(**kline)
    # print(crypto.close())
    # crypto.addResults(**kline)
    # print(crypto.averages.ems10())
    kwargs = dict()
    crypto = Crypto('BTC')
    #api = BiAPIGeneral.BiAPIGeneral()
    #klines = api.get_klines(crypto.symbol(), 'USDT', **kwargs)
    # for kline in klines:
    #     crypto.addResults(**kline)
    # print(crypto.averages.trendIndex(-1))
    # print(crypto.averages.trendIndex(200))
    # print(crypto.averages.trendIndex(20))
    # print(f'200 trend: {crypto.averages.trendIndex(-1)}, 20 trend: {crypto.averages.trendIndex(20)}')


if __name__ == '__main__': main()