# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 20:23:37 2020

@author: Balarka
"""
from screener_backend.auxFuncs import getDate_today,getDate_yesterday,getDate_previous,printProgressBar
from screener_backend.auxFuncs import convertDate
from screener_backend.intraday_instrument_request import getQuote_data as qRequest
from screener_backend.technicalWrapper import TECH_FXS
from screener_backend.instrument_request import INSTRUMENT_DATA
from screener_backend.nselist import NSE_TradedStocks,NSE_localAll,Nifty50,NiftyNext50
from screener_backend.intraday_momentum import INTRADAY_MOMENTUM_SCREENER

# import required native modules
import sys
import requests

def intraDay_momentumStocks(stocksList,stockInfo_source='NSE',customSession=None,
                            screenDate=getDate_today(),
                            cutoffVolume=500000,OHOL_margin=0.5,OC_change=3):
    screenedInstruments = {
        'Long'  : [],
        'Short' : [],
    }

    # create a progressbar to track the screening process
    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format('') , length = 50)
    # loop through the list of instruments sent to check for the trade setups
    for idx,currentInstrument in enumerate(stocksList):
        try:
            # fetch histrorical data of required equity instrument
            temp_obj = INSTRUMENT_DATA(currentInstrument,stockInfo_source)
            temp_obj.requestData(screenDate,screenDate,customSession)
            # get the OHLC, Volume values for the instrument as a Dataframe
            primaryData = temp_obj.get_primeData()
            del temp_obj

        except:
            # skip the instrument in case of an exception while calculating the mean if the stock is just a day old,
            # or volume data is not available
            continue  
        
        if primaryData.shape[0] > 0:
            # scan if the stock can provide either bullish or bearish momentum in the next session
            momentum_screener_obj = INTRADAY_MOMENTUM_SCREENER(primaryData)
            result = momentum_screener_obj.scanInstrument(cutoffVolume,OHOL_margin,OC_change)
            if result == "Bullish":
                screenedInstruments['Long'].append(currentInstrument)
            elif result == "Bearish":
                screenedInstruments['Short'].append(currentInstrument)
            del momentum_screener_obj
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format(currentInstrument), length = 50)

    if len(screenedInstruments['Long']) > 0 or \
        len(screenedInstruments['Short']) > 0:
        return [0,screenedInstruments]
    else:
        return [1,screenedInstruments]
        
     
if __name__ == '__main__':
    # ensure this value is yesterday if the script is run in the morning before trading session
    # or should be today if the analysis is done after the close of the market for the present
    # day    
    #endDate = convertDate("17-04-2020")
    endDate = getDate_today()
    try:
        stocksList = NSE_TradedStocks(endDate)
    except:
        stocksList = NSE_TradedStocks(getDate_yesterday())
    # Local StockScreening Lists
    #stocksList = [*Nifty50(),*NiftyNext50()]
    #stocksList = NSE_localAll()        
    isCustomProxy = False
    # Select the source for downloading the stock information. Option are NSE (from official NSE website using nsepy APIs or
    # YAHOO (from yahoo finance using panda-webreader APIs)
    stockSource = 'NSE'

    # Configure any custom session to overcome proxy configurations
    if isCustomProxy:
        proxies = {'http': 'http://user:pwd@proxy:8080',
                   'https': 'https://user:pwd@proxy:8080'}
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
    else:
        sess = None   

    result =  intraDay_momentumStocks(stocksList,stockInfo_source=stockSource,customSession=sess,
                                      screenDate=endDate,
                                      cutoffVolume=400000,OHOL_margin=1.2,OC_change=3)
    if result[0] == 0:
        for key,value in result[1].items():
            print('{}=>\n{}\n'.format(key,value))
    else:
        print('No instruments for screening criteria')
            