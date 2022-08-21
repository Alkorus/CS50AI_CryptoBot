
from .crypto import Crypto
from abc import ABC, abstractmethod
import datetime


class Trade_Parent:

    def __init__(self, crypto: Crypto, stop_loss, stop_gain):
        self._crypto = crypto
        self._exit = 0
        self._exit_stamp = datetime.datetime.now()
        self._stop_loss = stop_loss
        self._stop_gain = stop_gain

    def crypto(self):
        return self._crypto

    def stop_loss(self):
        return self._stop_loss
    
    def stop_gain(self):
        return self._stop_gain

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