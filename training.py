#!/usr/bin/env python3

import asyncio
from asyncio.windows_events import NULL
from ctypes import Array
from datetime import datetime, timedelta
from datetime import date
import time
# import schedule
import sys
from numpy import array
import pandas as pd

import concurrent.futures

import modeles.crypto as crypto
from modeles.crypto import Crypto
# from modeles.trade import Trade_Parent

from modeles.BiAPIGeneral import BiAPIGeneral
from helpers.excelIO import ExcelIO

REFERENCE_CRYPTO = 'ETH'

def main():
    print("main training")
    api = BiAPIGeneral()

    print(len(sys.argv))
    if len(sys.argv) not in [3, 4]:
        sys.exit("Training expects a start and end date for the training range")
    
    boundaries = test_boundary_dates(sys.argv[1], sys.argv[2])
    print(boundaries)

    # get reference crypto if given
    ref = REFERENCE_CRYPTO
    if len(sys.argv) == 4:
        ref = sys.argv[3]

    list = get_crypto_list(api, ref)
    print(list)
    print(len(list))

    days = separate_days(boundaries, api)

    runs = assemble_runs(days, list, api)
    print(runs)
    print(len(runs))


# making sure the dates given are valid
def test_boundary_dates(start:str, finish:str):
    #check format
    try:
        training_start = datetime.strptime(start, '%Y-%m-%d')
        training_end = datetime.strptime(finish, '%Y-%m-%d')
    except:
        sys.exit("Invalid date format, looking for yyyy-mm-dd")

    # check are in the right order
    if training_end <= training_start:
        sys.exit("First date must be lower than last one")

    # check if the finish boundary is at least one day ago
    if training_end >= datetime.today() - timedelta(days=1):
        sys.exit("The training boundaries must be in the past")

    return {"start": training_start, "finish": training_end} 

# get a list of cryptos exchanged with the reference one with which train the model
def get_crypto_list(api:BiAPIGeneral, ref:str):

    # Getting the exchange rate of the reference coin to a stable coin set to 1 $US
    ref_value = api.get_ref_stable_conversion(ref)
    if ref_value is None:
        sys.exit("Exchange rate for reference crypto couldn't be found, please try another reference symbol")
    print(ref_value)

    # multipliers used to cast a broader net of cryptos then the ones that are in range today, to have more points of reference for the training
    lowest = (api.LOWEST_PRICE/ref_value) * 0.25
    highest = (api.HIGHEST_PRICE/ref_value) * 10

    list = api.get_all_symbols(ref, lowest, highest)
    return list

# separate the training range into discrete days
def separate_days(boundaries:dict, api:BiAPIGeneral):
    #print(boundaries['start'])
    start_date = boundaries['start'].strftime("%Y-%m-%d")
    end_date = boundaries['finish'].strftime("%Y-%m-%d")
    datelist = pd.date_range(start=start_date, end=end_date).to_pydatetime().tolist()
    days = []
    #print(datelist)
    
    delta = get_proper_timedelta(api)
    for day in datelist:
        bounds = {"start": day - delta, "finish": day + timedelta(days=1)}
        days.append(bounds)

    # print(days)
    return days

# getting the right timedelta in function of the queue length of crypto and the interval from the API 
def get_proper_timedelta(api:BiAPIGeneral):

    interval = api.BASE_INTERVAL
    value = int(interval[:-1])
    value = value * crypto.QUEUE_MAX_LEN
    unit = interval[-1]
    delta = 0
    if unit == 'm':
        delta = timedelta(minutes=value)
    elif unit == 'h':
        delta = timedelta(hour=value)
    elif unit == 'd':
        delta = timedelta(days=value)
    elif unit == 'w':
        delta = timedelta(weeks=value)
    elif unit == 'M':
        delta = timedelta(days=value*30)
    elif unit == 's':
        delta = timedelta(seconds=value)
    return delta
    
# 
def assemble_runs(days:Array, symbols:Array, api:BiAPIGeneral):
    runs = []
    for crypto in symbols:
        print(crypto)
        traded_that_day = False
        i = 1
        # check if there were trades on the last day of the range, if not, pass the crypto entirely
        kwargs = dict(start = api.convert_time_py_to_bi(days[-1]["start"]), end = api.convert_time_py_to_bi(days[-1]["finish"]))
        if len(api.get_klines(crypto, REFERENCE_CRYPTO, **kwargs)) > 0:
            for day in days:
                # if it hasn't been confirmed that there are data for that day, check for them
                if not traded_that_day:
                    kwargs = dict(start = api.convert_time_py_to_bi(day["start"]), end = api.convert_time_py_to_bi(day["finish"]))
                    print(i)
                    i = i+1
                    if len(api.get_klines(crypto, REFERENCE_CRYPTO, **kwargs)) > 0:
                        traded_that_day = True
                
                # includes current day if it's the first with data available
                if traded_that_day:
                    run = {"start": day["start"], "finish": day["finish"], "symbol": crypto}
                    runs.append(run)
    return runs


if __name__ == '__main__': 
    main()