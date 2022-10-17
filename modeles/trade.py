
from .crypto import Crypto
from abc import ABC, abstractmethod
import datetime


class Trade:

    def __init__(self, crypto: Crypto, entryValue):
        self._crypto = crypto
        self._entryTime = crypto.openTime()
        self._entryValue = entryValue 


    def crypto(self):
        return self._crypto

    def exit(self):
        return float(self._exit)
    
    def exit_stamp(self):
        return self._exit_stamp



    @staticmethod
    @abstractmethod
    def test_entry(crypto: Crypto):
        pass

    @staticmethod
    @abstractmethod
    def test_exit(crypto:Crypto):
        pass

    @abstractmethod
    def exit_position(self):
        pass