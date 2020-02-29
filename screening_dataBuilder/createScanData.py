# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""

import os
import sys
import statistics
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import required modules from project
from screener_backend.nselist import NSE_localCSV
from screener_backend.auxFuncs import convertDate,getDate_today,printProgressBar
from screener_backend.auxFuncs import getPD_date
from screener_backend.instrument_request import INSTRUMENT_DATA
from screener_backend.technicalWrapper import TECH_FXS
from screener_backend.bounceAlgo import BOUNCESCREENER
from screener_backend.ipbAlgo import IPBSCREENER
from auxObjs import BounceData_Dict

def createData_BounceIPB(instrument,startDate,endDate,
                         stockInfo_source = 'NSE',
                         forBounce = True,forIPB = True,
                         preDate_EntryTicks = 260,position = 'long',
                         postData_Ticks = 20):
    
    # fetch histrorical data of required equity instrument
    temp_obj = INSTRUMENT_DATA(instrument,infoSource=stockInfo_source)
    temp_obj.requestData(startDate,endDate,None)
    # get the OHLC, Volume values for the instrument as a Dataframe
    primaryData = temp_obj.get_primeData()
    deliveryData = temp_obj.get_Delivery()
    delivery_all = deliveryData['delivery'].tolist()     
    del temp_obj
    
    # store close values of all data 
    refDFs = [primaryData,deliveryData]
    refData = pd.concat(refDFs,axis=1)
    high_all = primaryData['high'].tolist()
    
    niftyStartDate = primaryData.index.values[0]
    niftyEndDate = primaryData.index.values[-1]
    # fetch historical data for NIFTY50 for RSC and Position Calculations
    tempNifty_obj = INSTRUMENT_DATA("NIFTY",infoSource="NSE")
    tempNifty_obj.requestData(niftyStartDate,niftyEndDate,None,True)
    niftyData = tempNifty_obj.get_allData()
      
    try:
        # compute required Nifty parameters
        technical_obj = TECH_FXS(niftyData)
        # not all technical details are required with regard to nifty values
        closeNifty_all = niftyData['close'].tolist()
        EMA18_nifty = technical_obj.getEMA(18).tolist()
        EMA50_nifty = technical_obj.getEMA(50).tolist()
        EMA150_nifty = technical_obj.getEMA(100).tolist()
        del technical_obj
    except Exception as excp:
        print(excp)   
        
    # save last 20sessions to compute TP/SL result
    primaryData = primaryData[:-postData_Ticks] 
    
    totalEntries = primaryData.shape[0]
    if totalEntries > preDate_EntryTicks:       
        scanDict = BounceData_Dict()
        
        for i in range(0,totalEntries-preDate_EntryTicks):
            tempData_df = primaryData[:preDate_EntryTicks+i]
            
            # get the required technical data using the talib interfaces to perform the screening of the instruments        
            technical_obj = TECH_FXS(tempData_df)
            try:
                # EMAs are Pandas Series type
                EMA6 = technical_obj.getEMA(6)
                EMA18 = technical_obj.getEMA(18)
                EMA20 = technical_obj.getEMA(20)
                EMA50 = technical_obj.getEMA(50)
                EMA100 = technical_obj.getEMA(100)
                EMA150 = technical_obj.getEMA(150)
                # As the EMA values are not accurate for longer time periods, we use 
                # SMA as substitute and manually verify the same for the screened 
                # instruments
                # MACD and STOCHASTICS are both Pandas Dataframe type
                MACD12 = technical_obj.getMACD(12,26,9)
                MACD50 = technical_obj.getMACD(50,100,9)
                MACD18 = technical_obj.getMACD(18,50,9)
                STOCH5_33 = technical_obj.getSTOCH(5,3,3)
            except:
                # skip current instrument if there is calculation exception from the TALIB wrapper. Generally occurs
                # with YAHOO FINANCIALS due to missing data. 
                continue 
            del technical_obj
            
            if position == 'long':
                if forBounce:
                    # create the object for long position screening
                    bounceScreener_obj = BOUNCESCREENER(tempData_df,EMA18,EMA20,EMA50,EMA100,EMA150,MACD18,MACD50,STOCH5_33)
                    # very less parameters taken from the caller function to get max data for the trade setups
                    bounceScreener_obj.longScreener_initParams(True,EMA_check = 'Step')
                    
                    fxPtr_dict = {
                                    'B18'   : bounceScreener_obj.isInstrument_bounce18longMatch,
                                    'B20'   : bounceScreener_obj.isInstrument_bounce20longMatch,
                                    'B50'   : bounceScreener_obj.isInstrument_bounce50longMatch,
                                    'B100'  : bounceScreener_obj.isInstrument_bounce100longMatch,
                                    'B150'  : bounceScreener_obj.isInstrument_bounce150longMatch,
                                    }
                    
                    for key,item in fxPtr_dict.items():
                        if item(deltaAllowed=False):    
                            scanDict.DataDict['date'].append(getPD_date(tempData_df.index.values[-1]).strftime("%d_%m_%Y"))
                            scanDict.DataDict['open1'].append(tempData_df['open'].tolist()[-3])
                            scanDict.DataDict['high1'].append(tempData_df['high'].tolist()[-3])
                            scanDict.DataDict['low1'].append(tempData_df['low'].tolist()[-3])
                            scanDict.DataDict['close1'].append(tempData_df['close'].tolist()[-3])
                            scanDict.DataDict['openR'].append(tempData_df['open'].tolist()[-2])
                            scanDict.DataDict['highR'].append(tempData_df['high'].tolist()[-2])
                            scanDict.DataDict['lowR'].append(tempData_df['low'].tolist()[-2])
                            scanDict.DataDict['closeR'].append(tempData_df['close'].tolist()[-2])
                            scanDict.DataDict['openC'].append(tempData_df['open'].tolist()[-1])
                            scanDict.DataDict['highC'].append(tempData_df['high'].tolist()[-1])
                            scanDict.DataDict['lowC'].append(tempData_df['low'].tolist()[-1])
                            scanDict.DataDict['closeC'].append(tempData_df['close'].tolist()[-1])
                            scanDict.DataDict['vol3avg'].append(sum(tempData_df['volume'].tolist()[-3:])/3)
                            if key == 'B18':
                                scanDict.DataDict['macdHist3var'].append(statistics.variance(MACD18['macdhist'].tolist()[-3:]))
                            else:
                                scanDict.DataDict['macdHist3var'].append(statistics.variance(MACD50['macdhist'].tolist()[-3:]))
                            scanDict.DataDict['stochastic'].append(STOCH5_33['slowk'].tolist()[-2])
                            scanDict.DataDict['delivery'].append(delivery_all[preDate_EntryTicks+i-1])
                            rsc = ( ((tempData_df['close'].tolist()[-1]/tempData_df['close'].tolist()[-52])/(closeNifty_all[preDate_EntryTicks+i-1]/closeNifty_all[preDate_EntryTicks+i-52])) - 1) * 100
                            scanDict.DataDict['rscnifty50'].append(rsc)
                            niftyLong = (EMA18_nifty[preDate_EntryTicks+i-1] > EMA50_nifty[preDate_EntryTicks+i-1]) and \
                                        ( (EMA50_nifty[preDate_EntryTicks+i-1] > EMA150_nifty[preDate_EntryTicks+i-1]) \
                                          or (closeNifty_all[preDate_EntryTicks+i-1] > EMA150_nifty[preDate_EntryTicks+i-1]))                            
                            scanDict.DataDict['niftylong'].append(niftyLong)
                            scanDict.DataDict['bounceType'].append(key)
                            E = tempData_df['high'].tolist()[-1] + (tempData_df['high'].tolist()[-1] * 0.5 / 100)
                            SL = tempData_df['low'].tolist()[-1] - (tempData_df['low'].tolist()[-1] * 0.5 / 100)
                            R = E-SL
                            TP = E + 2*R
                            result = "loss"
                            if high_all[preDate_EntryTicks+i+0] < E:
                                result = "none"
                                sessIdx = 0
                            else:
                                for sessIdx in range(postData_Ticks):
                                    if high_all[preDate_EntryTicks+i+sessIdx] >= TP:
                                        result = "win"
                                        break
                            scanDict.DataDict['result'].append(result)
                            scanDict.DataDict['time4trade'].append(sessIdx+1)                                 
                            

        with pd.ExcelWriter(os.path.join(os.path.dirname(os.path.abspath(__file__)),"rawData\\"+instrument+'.xls')) as xlsWriter:
            refData.to_excel(xlsWriter,sheet_name="PrimaryData")
            pd.DataFrame.from_dict(scanDict.DataDict).to_excel(xlsWriter,sheet_name="ScanData")
        
    
    

if __name__ == "__main__":
    stocksList = NSE_localCSV("G:\Investments\Scripts\Stock_Screener\screening_dataBuilder\EQStocks_NSE.csv")

    stockInfoSource = "NSE"
    startDate = convertDate("01-01-2010")
    endDate = getDate_today()
    # create a progressbar to track the screening process
    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format('') , length = 50)    
    for idx in range (len(stocksList)):
        createData_BounceIPB(stocksList[idx],startDate,endDate,
                             stockInfo_source = 'NSE',
                             preDate_EntryTicks = 260,position = 'long')
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format(stocksList[idx]), length = 50)        
    
