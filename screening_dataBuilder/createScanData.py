# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""

import os
import sys
import statistics
import pandas as pd
import logging
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

def create_logger():
    # create logger 
    logger = logging.getLogger('AutomatedDataCreation')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('CreateDataScan.log', mode='w')
    fh.setLevel(logging.INFO)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('{:8} --- %(message)s'.format("%(levelname)s"))
    fh.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)

    return logger

logger = create_logger()

def createData_BounceIPB(instrument,startDate,endDate,
                         stockInfo_source = 'NSE',
                         forBounce = True,forIPB = True,
                         preDate_EntryTicks = 260,position = 'long',
                         postData_Ticks = 30):
    
    # fetch histrorical data of required equity instrument
    temp_obj = INSTRUMENT_DATA(instrument,infoSource=stockInfo_source)
    temp_obj.requestData(startDate,endDate,None)
    # get the OHLC, Volume values for the instrument as a Dataframe
    primaryData = temp_obj.get_primeData()
    deliveryData = temp_obj.get_Delivery()
    delivery_all = deliveryData['delivery'].tolist()     
    del temp_obj
    
    if primaryData.shape[0] == 0:
        # return in case the stock is new and no data for the instrument is available
        logger.info("No Historical Data Retrived")
        return 

    # store close values of all data 
    refDFs = [primaryData,deliveryData]
    refData = pd.concat(refDFs,axis=1)
    high_all = primaryData['high'].tolist()
    logger.info("ReferenceData Shape = {}".format(refData.shape))
    
    # fetch historical data for NIFTY50 for RSC and Position Calculations    
    niftyStartDate = primaryData.index.values[0]
    niftyEndDate = primaryData.index.values[-1]
    tempNifty_obj = INSTRUMENT_DATA("NIFTY 50",infoSource="NSE")
    tempNifty_obj.requestData(niftyStartDate,niftyEndDate,None,True)
    niftyData = tempNifty_obj.get_allData()    
    logger.info("NiftyData Shape = {}".format(niftyData.shape))   
          
    try:
        # compute required Nifty parameters
        technical_obj = TECH_FXS(niftyData)
        # not all technical details are required with regard to nifty values
        closeNifty_all = niftyData.get(['close'])
        EMA18_nifty = technical_obj.getEMA(18).tolist()
        EMA50_nifty = technical_obj.getEMA(50).tolist()
        EMA150_nifty = technical_obj.getEMA(100).tolist()
        del technical_obj
        logger.info("Sucessfully computed NIFTY technicals")
    except Exception as excp:
        logger.error("Failed to compute Technicals for Nifty")
        return
        
    # save last 20sessions to compute TP/SL result
    primaryData = primaryData[:-postData_Ticks] 
    logger.info("PrimaryData Shape = {}".format(primaryData.shape))
    
    totalEntries = primaryData.shape[0]
    if totalEntries > preDate_EntryTicks:
        logger.info("Starting Data Fetch")       
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
                logger.error("Failed to compute Technicals for Instrument")
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
                        E = tempData_df['high'].tolist()[-1] + (tempData_df['high'].tolist()[-1] * 0.5 / 100)
                        if item(deltaAllowed=False) and (high_all[preDate_EntryTicks+i] < E):
                            try:
                                logger.info("Entry at date : {}".format(getPD_date(tempData_df.index.values[-1]).strftime("%d_%m_%Y")))
                                # perform all the computations first and then write the dictionary to avoid partial row creation for dataframe
                                SL = tempData_df['low'].tolist()[-1] - (tempData_df['low'].tolist()[-1] * 0.5 / 100)
                                R = E-SL
                                TP = E + 2*R    
                                rsc = ( ((tempData_df['close'].tolist()[-1]/tempData_df['close'].tolist()[-52])/(closeNifty_all.loc[tempData_df.index.values[-1],'close']/closeNifty_all.loc[tempData_df.index.values[-52],'close'])) - 1) * 100                                                                                       
                                niftyLong = (EMA18_nifty[preDate_EntryTicks+i-1] > EMA50_nifty[preDate_EntryTicks+i-1]) and \
                                            ( (EMA50_nifty[preDate_EntryTicks+i-1] > EMA150_nifty[preDate_EntryTicks+i-1]) \
                                            or (closeNifty_all.loc[tempData_df.index.values[-1],'close'] > EMA150_nifty[preDate_EntryTicks+i-1]))                                 
                                result = "loss"
                                for sessIdx in range(postData_Ticks):
                                    if high_all[preDate_EntryTicks+i+sessIdx] >= TP:
                                        result = "win"
                                        break

                                # create entry in the dictionary                                            
                                scanDict.DataDict['date'].append(getPD_date(tempData_df.index.values[-1]).strftime("%d_%m_%Y"))
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
                                scanDict.DataDict['entryP'].append(E)
                                scanDict.DataDict['stoplossP'].append(SL)
                                scanDict.DataDict['targetP'].append(TP)
                                scanDict.DataDict['vol3avg'].append(sum(tempData_df['volume'].tolist()[-3:])/3)
                                if key == 'B18':
                                    scanDict.DataDict['macdHist3var'].append(statistics.variance(MACD18['macdhist'].tolist()[-3:]))
                                else:
                                    scanDict.DataDict['macdHist3var'].append(statistics.variance(MACD50['macdhist'].tolist()[-3:]))
                                scanDict.DataDict['stochastic'].append(STOCH5_33['slowk'].tolist()[-2])
                                scanDict.DataDict['delivery'].append(delivery_all[preDate_EntryTicks+i-1])
                                scanDict.DataDict['rscnifty50'].append(rsc)                           
                                scanDict.DataDict['niftylong'].append(niftyLong)
                                scanDict.DataDict['bounceType'].append(key)
                                scanDict.DataDict['result'].append(result)
                                scanDict.DataDict['time4trade'].append(sessIdx+1)
                            except:
                                logger.error("Failed to create entry for instrument at {}".format(getPD_date(tempData_df.index.values[-1]).strftime("%d_%m_%Y")))
                                sys.exit(0)                               

        if len(scanDict.DataDict['result']) > 0:                   
            with pd.ExcelWriter(os.path.join(os.path.dirname(os.path.abspath(__file__)),"rawData\\"+instrument+'.xls')) as xlsWriter:
                refData.to_excel(xlsWriter,sheet_name="PrimaryData")
                pd.DataFrame.from_dict(scanDict.DataDict).to_excel(xlsWriter,sheet_name="ScanData")
            logger.info("Sucessfully wrote data to XL file\n")
        else:
            logger.info("Sucessfully finished data scan \n")
if __name__ == "__main__":

    stocksList = NSE_localCSV("G:\Investments\Scripts\Stock_Screener\screening_dataBuilder\EQStocks_NSE.csv")
    stockInfoSource = "NSE"
    
    startDate = convertDate("01-01-2010")
    endDate = getDate_today()
    logger.info("Starting CreateData Script")
    # create a progressbar to track the screening process
    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format('') , length = 50)    
    for idx in range (len(stocksList)):
        logger.info("-----\n\t\t ******<<{}>>******".format(stocksList[idx]))        
        createData_BounceIPB(stocksList[idx],startDate,endDate,
                             stockInfo_source = 'NSE',
                             preDate_EntryTicks = 260,position = 'long',
                             postData_Ticks = 30)
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format(stocksList[idx]), length = 50)
