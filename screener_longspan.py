# -*- coding: utf-8 -*-
"""
Created on Thu Feb 13 19:40:06 2020

@author: Balarka
"""

# import required modules from project
from screener_backend.nselist import NSE_TradedStocks,Nifty50,NiftyNext50,NSE_localAll
from screener_backend.auxFuncs import convertDate,getDate_previous,getDate_today,getDate_yesterday,printProgressBar
from screener_backend.auxFuncs import getPD_date,timeDiff_inDays
from screener_backend.instrument_request import INSTRUMENT_DATA
from screener_backend.technicalWrapper import TECH_FXS
from screener_backend.trendRetracementAlgo import TREND_RETRACEMENTSCREENER


# import required native modules 
import sys
import requests
from statistics import mean
import pandas as pd
import os

def TrendRetracement_Stocks(stocksList, stockInfo_source = 'NSE', customSession = None,
                            volumeCutOff=1500000,position='long',
                            endDate=getDate_today(),historialDataTicks=3650, trendTracePeriod = 3,
                            EMAfilter_period=15):
    
    screenedInstruments = {
            }
    
    startDate = getDate_previous(historialDataTicks,endDate)
    
    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format('') , length = 50)
    for idx,currentInstrument in enumerate(stocksList):
        try:
            # fetch histrorical data of required equity instrument
            temp_obj = INSTRUMENT_DATA(currentInstrument,stockInfo_source)
            temp_obj.requestData(startDate,endDate,customSession)
            primaryData = temp_obj.get_primeData()
            del temp_obj         
        
            # perform a volume sanity check
            meanVolume = mean(primaryData['volume'].tolist()[-int(historialDataTicks*0.1)-1:])
        except:
            continue
        if meanVolume >= volumeCutOff:
            # get the required technical data using the talib interfaces to perform the bounce screening
            # of the instruments        
            technical_obj = TECH_FXS(primaryData)
            try:    
                # EMAs are Pandas Series type
                EMA20 = technical_obj.getEMA(20)
                EMA40 = technical_obj.getEMA(40)
                SMA50 = technical_obj.getSMA(50)
                SMA100 = technical_obj.getSMA(100)
                SMA150 = technical_obj.getSMA(150)
                # The Value of SMA200 is inaccurate for historical data periods less than 5 years
                SMA200 = technical_obj.getSMA(200)
            except:
                continue
            del technical_obj
            
            # create the object for long position screening 
            trendScreener_obj = TREND_RETRACEMENTSCREENER(primaryData,EMA20,EMA40,SMA50,SMA100,SMA150,SMA200)            
            if 'long' == position:  
                tempRes = trendScreener_obj.isInstrumentValid(EMAcheckPeriod=EMAfilter_period,tracePeriod=trendTracePeriod)
                if tempRes[0]: screenedInstruments[currentInstrument] = tempRes[1]
            elif 'short' == position:
                # shorting not yet implemented as short positions on NSE,BSE have to be squared off on the same day
                # maybe useful for futures and options later
                print("Short Position Scans still not supported")                
                pass 
                sys.exit(0)
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format(currentInstrument), length = 50)
        
    return screenedInstruments
            
if __name__=="__main__":
    
    endDate = getDate_today()
    stocksList = NSE_TradedStocks(endDate)
    #stocksList = [*Nifty50(),*NiftyNext50()]
    #stocksList = NSE_localAll()
    
    # Select the source for downloading the stock information. Option are NSE (from official NSE website using nsepy APIs or
    # YAHOO (from yahoo finance using panda-webreader APIs)
    stockSource = 'NSE'

    isCustomProxy = False    
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
        
    result = TrendRetracement_Stocks(stocksList,stockInfo_source=stockSource,customSession=sess,
                                     volumeCutOff = 25000,position='long',
                                     endDate=endDate,historialDataTicks=1800,trendTracePeriod=1)
    if len(result.keys()) > 0:
        tempDict = {
                    'Instruments'   : list(result.keys()),
                    'Description'   : list(result.values())
                    }
        scanDf = pd.DataFrame.from_dict(tempDict)
        if os.path.exists("TrendRetracement_Scan.xlsx"): os.remove("TrendRetracement_Scan.xlsx") 
        scanDf.to_excel("TrendRetracement_Scan.xlsx")        
    else:
        print("No Instruments matching LongTrendRetracement Setup Found")

