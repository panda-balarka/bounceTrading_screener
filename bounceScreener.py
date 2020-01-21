# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""

from nselist import NSE_TradedStocks
from auxFuncs import getDate_previous,getDate_today,getDate_yesterday,printProgressBar
from instrument_request import INSTRUMENT_DATA
from technicalWrapper import TECH_FXS
from screenAlgo import BOUNCESCREENER

def screenStocks(volumeCutoff=150000,position='long',bounce18=False,bounce50=True,bounce100=False,endDate_select='Today'):
    endDate = getDate_today() if endDate_select == 'Today' else getDate_yesterday()
    stocksList = NSE_TradedStocks(endDate)
    screendedInstruments = {
        '18 Bounce Long'  : [],
        '50 Bounce Long'  : [],
        '100 Bounce Long' : []
    }
    # ensure this value is yesterday if the script is run in the morning before trading session
    # or should be today if the analysis is done after the close of the market for the present
    # day
    startDate = getDate_previous(3650,endDate)

    stocksList = stocksList[:100]
    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = 'Complete', length = 50)
    for idx,currentInstrument in enumerate(stocksList):
        # fetch histrorical data of required equity instrument
        temp_obj = INSTRUMENT_DATA(currentInstrument)
        temp_obj.requestData(startDate,endDate)
        primaryData = temp_obj.get_primeData()
        del temp_obj
        # perform a volume sanity check
        meanVolume = primaryData['volume'].mean()
        if meanVolume >= volumeCutoff:
            # get the required technical data using the talib interfaces to perform the bounce screening
            # of the instruments        
            technical_obj = TECH_FXS(primaryData)
            # EMAs are Pandas Series type
            EMA18 = technical_obj.getEMA(18)
            EMA50 = technical_obj.getEMA(50)
            EMA100 = technical_obj.getEMA(100)
            EMA200 = technical_obj.getSMA(200)
            # As the EMA values are not accurate for longer time periods, we use 
            # SMA as substitute and manually verify the same for the screened 
            # instruments
            # MACD and STOCHASTICS are both Pandas Dataframe type
            MACD50 = technical_obj.getMACD(50,100,9)
            MACD18 = technical_obj.getMACD(18,50,9)
            STOCH5_33 = technical_obj.getSTOCH(5,3,3)
            del technical_obj

            if position == 'long':
                # create the object for long position screening
                bounceScreener_obj = BOUNCESCREENER(primaryData,EMA18,EMA50,EMA100,EMA200,MACD18,MACD50,STOCH5_33)
                bounceScreener_obj.longScreener_initParams()

                if bounce18:
                    if bounceScreener_obj.isInstrument_bounce18longMatch(): screendedInstruments['18 Bounce Long'].append(currentInstrument)

                if bounce50:
                    if bounceScreener_obj.isInstrument_bounce50longMatch(): screendedInstruments['50 Bounce Long'].append(currentInstrument)

                if bounce100:
                    if bounceScreener_obj.isInstrument_bounce100longMatch(): screendedInstruments['100 Bounce Long'].append(currentInstrument)                                       
                
            else:
                # code the short position calculations
                pass 
                print("Short Position Scans still not supported")
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = 'Complete', length = 50)
                
    if (
            len(screendedInstruments['18 Bounce Long']) > 0
        or  len(screendedInstruments['50 Bounce Long']) > 0
        or  len(screendedInstruments['100 Bounce Long']) > 0
        ):
        print(screendedInstruments)
    else:
        print('No Instrument matching screening criteria found')
                
if __name__ == '__main__':
    screenStocks(100000,bounce18=True,bounce50=True,bounce100=True)












