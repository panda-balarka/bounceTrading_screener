# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 20:23:37 2020

@author: Balarka
"""

import nsepy
from datetime import date

class INSTRUMENT_DATA(object):
    
    def __init__(self,symbol):
        # initialises an object variable to store the SCRIP SYMBOL
        # used to fetch data from NSE
        self.symbol = symbol
    
    def requestData(self,startDate,endDate):
        # call the nsepy wrapper to fetch historical data of the
        # requested symbol from the NSE website
        self.instrument_data = nsepy.get_history(self.symbol,
                                           start=date(startDate[2],startDate[1],startDate[0]),
                                           end=date(endDate[2],endDate[1],endDate[0]))
    
    def get_primeData(self):
        # function to return the primary OHLC and volume values as a
        # dataframe
        temp_df = self.instrument_data.get(['Open','High','Low','Close','Volume'])
        return temp_df
    
    def get_allData(self):
        # return the whole dataframe from the NSEPY wrapper
        return self.instrument_data
        

        
# Script standalone selftest
if __name__ == '__main__':
    
    # Load data of equity from SBIN
    temp_obj = INSTRUMENT_DATA('SBIN')
    # Fetch the values from
    temp_obj.requestData([1,12,2019],[20,1,2020])
    # Display the dataframe with the required results
    print(temp_obj.get_primeData())
    
    
    
    