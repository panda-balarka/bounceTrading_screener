# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""

from nselist import NSE_TradedStocks,Nifty50,NiftyNext50
from auxFuncs import convertDate,getDate_previous,getDate_today,getDate_yesterday,printProgressBar
from instrument_request import INSTRUMENT_DATA
from technicalWrapper import TECH_FXS
from screenAlgo import BOUNCESCREENER

import sys

def screenStocks(stocksList,
                 volumeCutoff=15000000, position='long', endDate=getDate_today(),historialDataTicks=3650,
                 bounce18=False, bounce50=True, bounce100=False,
                 ignoreStochastic = False, stochasticThreshold = 30, stochasticThreshold_period=3, 
                 ignoreEMA=False,EMA_check='All',
                 useDelta=False,delta18=0.001,delta50=0.005,delta100=0.01
                 ):

    screendedInstruments = {
        '18 Bounce Long'  : [],
        '50 Bounce Long'  : [],
        '100 Bounce Long' : []
    }
    # ensure this value is yesterday if the script is run in the morning before trading session
    # or should be today if the analysis is done after the close of the market for the present
    # day
    startDate = getDate_previous(historialDataTicks,endDate)

    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format('') , length = 50)
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
                bounceScreener_obj.longScreener_initParams(ignoreStochastic,stochasticThreshold,stochasticThreshold_period,
                                                           ignoreEMA,EMA_check)

                if bounce18:
                    if bounceScreener_obj.isInstrument_bounce18longMatch(deltaAllowed=useDelta,deltaValue=delta18): screendedInstruments['18 Bounce Long'].append(currentInstrument)

                if bounce50:
                    if bounceScreener_obj.isInstrument_bounce50longMatch(deltaAllowed=useDelta,deltaValue=delta50): screendedInstruments['50 Bounce Long'].append(currentInstrument)

                if bounce100:
                    if bounceScreener_obj.isInstrument_bounce100longMatch(deltaAllowed=useDelta,deltaValue=delta100): screendedInstruments['100 Bounce Long'].append(currentInstrument)                                       
                
                del bounceScreener_obj
                
            else:
                # code the short position calculations
                pass 
                print("Short Position Scans still not supported")
                sys.exit(0)
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format(currentInstrument), length = 50)
                
    if (
            len(screendedInstruments['18 Bounce Long']) > 0
        or  len(screendedInstruments['50 Bounce Long']) > 0
        or  len(screendedInstruments['100 Bounce Long']) > 0
        ):
        return [0,screendedInstruments]
    else:
        return [1,screendedInstruments]
                
if __name__ == '__main__':
    
    #stocksList = NSE_TradedStocks(getDate_yesterday())
    stocksList = [*Nifty50(),*NiftyNext50()]
    isDaily = False
    if isDaily:
        # Daily
        result = screenStocks(stocksList,endDate=getDate_yesterday(),
                              volumeCutoff=100000,historialDataTicks=365,bounce18=True,bounce50=True,bounce100=True,
                              useDelta=False)
        if result[0] == 0:
            print(result[1])
        else:
            print('No instruments for screening criteria')
    else:       
        screenFor = 100 #days
        # a custom screening 
        resultList = []
        totalHitDays = 0
        for i in range(screenFor):
            dateTemp = getDate_previous(i,getDate_yesterday())
            print(dateTemp.strftime("%d_%m"))
            result = screenStocks(stocksList,
                                  volumeCutoff=1000000,endDate=dateTemp,historialDataTicks=365,
                                  bounce18=True,bounce50=True,bounce100=True,
                                  useDelta=False)
            if result[0] == 0:
                totalHitDays += 1
                resultList.append('>>{}\n{}\n{}\n'.format(dateTemp.strftime("%d_%m_%Y"),str(result[1]),'-'*120)) 
            print("->Total Days with Screening Hits: {}".format(totalHitDays))

        with open('{}\{}.txt'.format('G:\Investments\Scripts\Stock_Screener\Scans','Scan'),'w') as fileobj:
            fileobj.write(''.join(resultList))        
                    












