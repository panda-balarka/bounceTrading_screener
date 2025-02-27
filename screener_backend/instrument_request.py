# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 20:23:37 2020

@author: Balarka
"""

import nsepy
import pandas_datareader.data as web
import requests

class INSTRU_REQ_ERROR(Exception):
    pass

class INSTRUMENT_DATA(object):
    
    def __init__(self,symbol,infoSource='NSE'):
        # initialises an object variable to store the SCRIP SYMBOL
        # used to fetch data from NSE
        if infoSource == 'YAHOO':
            self.symbol = symbol+'.NS'        
        else:
            self.symbol = symbol
        self.API = infoSource
    
    def requestData(self,startDate,endDate,customSession=None,isIndex=False):
        if self.API == 'NSE':
            # call the nsepy wrapper to fetch historical data of the
            # requested symbol from the NSE website
            if isIndex:
                self.instrument_data = nsepy.get_history(self.symbol,
                                                   start=startDate,
                                                   end=endDate,
                                                   index=True)                
            else:
                self.instrument_data = nsepy.get_history(self.symbol,
                                                   start=startDate,
                                                   end=endDate)
        elif self.API == 'YAHOO':
            if customSession != None:
                self.instrument_data = web.DataReader(self.symbol, 'yahoo', startDate, endDate, session=customSession)
            else:
                self.instrument_data = web.DataReader(self.symbol, 'yahoo', startDate, endDate)
        self.instrument_data.rename(columns={'Open':'open',
                                             'High':'high',
                                             'Low':'low',
                                             'Close':'close',
                                             'Volume':'volume',
                                             '%Deliverble':'delivery'},inplace=True)
    
    def get_primeData(self):
        # function to return the primary OHLC and volume values as a
        # dataframe
        temp_df = self.instrument_data.get(['open','high','low','close','volume'])
        return temp_df
    
    def get_allData(self):
        # return the whole dataframe from the NSEPY wrapper
        return self.instrument_data
    
    def get_Delivery(self):
        if self.API == 'NSE':
            return self.instrument_data.get(['delivery'])
        elif self.API == 'YAHOO':
            raise INSTRU_REQ_ERROR("DELIVERY INFORMATION NOT SUPPORTED WITH YAHOO FINANCIALS")
        
        

        
# Script standalone selftest
if __name__ == '__main__':
    
    from auxFuncs import convertDate,getDate_today,getDate_yesterday
    
    apiType = "NSE"
    if apiType == "NSE":
        # Load data of equity from SBIN
        temp_obj = INSTRUMENT_DATA('SBIN')
        # Fetch the values from
        temp_obj.requestData(convertDate('01/01/2020'),getDate_yesterday())
        # Display the dataframe with the required results
        print(temp_obj.get_primeData().tail())
        
    elif apiType == 'YAHOO':
        proxies = {'http': 'http:your proxy:8080'}
        headers = { "Accept":"application/json",
                    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
                    "Accept-Encoding":"none",
                    "Accept-Language":"en-US,en;q = 0.8",
                    "Connection":"keep-alive",
                    "Referer":"https://cssspritegenerator.com",
                    "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML,like Gecko) Chrome/23.0.1271.64 Safari/537.11"
                    }

        with requests.Session() as sess:
            sess.headers = headers
            sess.proxies.update(proxies)
            
        # Load data of equity from SBIN
        temp_obj = INSTRUMENT_DATA('SBIN',apiType)    
        # Fetch the values from
        temp_obj.requestData(convertDate('01/01/2019'),getDate_yesterday(),customSession=None) 
        # Display the dataframe with the required results
        print(temp_obj.get_primeData().tail())
    
    
    
    