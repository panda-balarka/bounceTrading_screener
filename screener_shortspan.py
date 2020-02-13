# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""
# import required modules from project
from screener_backend.nselist import NSE_TradedStocks,Nifty50,NiftyNext50,NSE_localAll
from screener_backend.auxFuncs import convertDate,getDate_previous,getDate_today,getDate_yesterday,printProgressBar
from screener_backend.auxFuncs import getPD_date,timeDiff_inDays
from screener_backend.instrument_request import INSTRUMENT_DATA
from screener_backend.technicalWrapper import TECH_FXS
from screener_backend.bounceAlgo import BOUNCESCREENER
from screener_backend.ipbAlgo import IPBSCREENER

# import required native modules
import sys
import requests

""" The screener functions that calls the screening algorithms based on user parameters and returns any matching instruments to the user.
    @Parameters@
           Param                :   Description
        -> stocksList           :   List of instruments to be screened
        -> stockInfo_source     :   Source to fetch instrument historical data ('NSE' for NSE or 'YAHOO' YAHOO_Financials)
        -> customSession        :   Use a custom requests session with proxy configurations (Only for 'YAHOO' stockInfo_source
                                    option, for NSE this is ignored)
        -> endDate              :   EndDate for the historical data fetched
        -> historicalDataTicks  :   Number of days prior to the EndDate for which the historical data is fetched
        -> position             :   Option to choose to screen for Bullish or Bearish postions ('long' for Bullish and 
                                    'short' for bearish)
        -> ignoreStochastic     :   Ignore the Stochastic check while screening the instruments (True-Ignore filter)
        -> stochasticThreshold  :   Threshold value for the Stochastic Check (Ignored if ignoreStochastic is True)
                                    Pass: InstrumentStochastic <= stochasticThreshold 
        -> stochTest_period     :   Number of days considered for checking the stochasticThreshold condition (Ignored if ignoreStochastic 
                                    is True)
        -> ignoreEMA            :   Ignore the EMA check while screening the instruments (True-Ignore filter)
        -> EMA_check            :   Type of EMA filter to be used ('All' for EMA18>EMA50>EMA100 or 
                                    'Step' for EMA18>EMA50 in 18 Bounce, EMA50>EMA100 in 50 Bounce, 100 Bounce and 150 Bounce.
                                    Ignored if ignoreEMA is True)
        -> bounce18             :   Scan the instruments for Bounce18 setup
        -> bounce50             :   Scan the instruments for Bounce50 setup
        -> bounce100            :   Scan the instruments for Bounce100 setup
        -> bounce150            :   Scan the instruments for Bounce150 setup
        -> useDelta             :   Use a small delta on the OHLC values while screening for setups to compensate for inaccurate 
                                    EMA calculations if required (True-Use delta adjustments)
        -> delta18              :   The delta value as percent to be used in Bounce18 setup (Ignored if useDelta is False)
        -> delta50              :   The delta value as percent to be used in Bounce50 setup (Ignored if useDelta is False)
        -> delta100             :   The delta value as percent to be used in Bounce100 setup (Ignored if useDelta is False)
        -> delta150             :   The delta value as percent to be used in Bounce150 setup (Ignored if useDelta is False)
        -> ipbEMA_checkPeriod   :   Number of days considered for checking the EMA condition 
        -> ipbMACD_filter       :   Option to use the MACD filter together with the EMA crossover in for IPB setup
                                    (True-Enable MACD based screening)
        -> ipb_EMA_check        :   Type of EMA check to be performed ('All' for EMA18>EMA50>EMA100, '18>50' for EMA18>EMA50)
        -> ipb_tracePeriod      :   Number of days considered for checking the EMA crossover or MACD screening for IPB setup 
    @Return@
        A dictionary of instruments that fit the trade setups based on the user screening parameters.
    """
def Bounce_IPB_Stocks(stocksList, stockInfo_source = 'NSE', customSession = None,
                      endDate=getDate_today(),historialDataTicks=3650,
                      volumeCutoff=15000000, position='long', 
                      ignoreStochastic = False, stochasticThreshold = 30, stochTest_period=3, 
                      ignoreEMA=False,EMA_check='All',
                      bounce18=False, bounce20=False, bounce50=True, bounce100=False, bounce150=False,
                      useDelta=False,delta18=0.001,delta20=0.001,delta50=0.005,delta100=0.01,delta150=0.01,
                      ipbEMA_checkPeriod = 5,ipbMACD_filter=True,ipb_EMA_check='18>50', ipb_tracePeriod=5,
                      ):
       
    screenedInstruments = {
        '18 Bounce Long'  : [],
        '20 Bounce Long'  : [],
        '50 Bounce Long'  : [],
        '100 Bounce Long' : [],
        '150 Bounce Long' : [],
        'ImpulsePullBack' : [],
    }
    # ensure this value is yesterday if the script is run in the morning before trading session
    # or should be today if the analysis is done after the close of the market for the present
    # day
    startDate = getDate_previous(historialDataTicks,endDate)

    printProgressBar(0,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format('') , length = 50)
    for idx,currentInstrument in enumerate(stocksList):
        # fetch histrorical data of required equity instrument
        temp_obj = INSTRUMENT_DATA(currentInstrument,stockInfo_source)
        temp_obj.requestData(startDate,endDate,customSession)
        primaryData = temp_obj.get_primeData()
        del temp_obj

        # perform a volume sanity check
        meanVolume = primaryData['volume'].mean()
        if meanVolume >= volumeCutoff:
            # get the required technical data using the talib interfaces to perform the bounce screening
            # of the instruments        
            technical_obj = TECH_FXS(primaryData)
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
            del technical_obj
            
            try:
                if "ERROR" in [EMA6,EMA18,EMA20,EMA50,EMA100,EMA150,MACD12,MACD18,MACD50,STOCH5_33]:
                    continue
            except:
                pass

            if position == 'long':
                # create the object for long position screening
                bounceScreener_obj = BOUNCESCREENER(primaryData,EMA18,EMA20,EMA50,EMA100,EMA150,MACD18,MACD50,STOCH5_33)
                bounceScreener_obj.longScreener_initParams(ignoreStochastic,stochasticThreshold,stochTest_period,
                                                           ignoreEMA,EMA_check)

                if bounce18:
                    if bounceScreener_obj.isInstrument_bounce18longMatch(deltaAllowed=useDelta,deltaValue=delta18): screenedInstruments['18 Bounce Long'].append(currentInstrument)
                    
                if bounce20:
                    if bounceScreener_obj.isInstrument_bounce20longMatch(deltaAllowed=useDelta,deltaValue=delta20): screenedInstruments['20 Bounce Long'].append(currentInstrument)                    

                if bounce50:
                    if bounceScreener_obj.isInstrument_bounce50longMatch(deltaAllowed=useDelta,deltaValue=delta50): screenedInstruments['50 Bounce Long'].append(currentInstrument)

                if bounce100:
                    if bounceScreener_obj.isInstrument_bounce100longMatch(deltaAllowed=useDelta,deltaValue=delta100): screenedInstruments['100 Bounce Long'].append(currentInstrument)                                       

                if bounce150:
                    if bounceScreener_obj.isInstrument_bounce100longMatch(deltaAllowed=useDelta,deltaValue=delta150): screenedInstruments['100 Bounce Long'].append(currentInstrument)                                                           
                
                del bounceScreener_obj

                ipbScreener_obj = IPBSCREENER(primaryData,EMA6,EMA18,EMA50,EMA100,MACD12)
                ipbScreener_obj.longScreener_initParams(ipbEMA_checkPeriod,ipb_EMA_check) 
                tempRes = ipbScreener_obj.isInstrument_impulsePullBack(MACD_check=ipbMACD_filter)
                if tempRes[0]: 
                    for dateVal in tempRes[1]:
                        if stockSource == 'YAHOO':
                            dateDiff = timeDiff_inDays(endDate,getPD_date(dateVal))
                        else:
                            dateDiff = timeDiff_inDays(endDate,dateVal)
                            
                        if dateDiff <= ipb_tracePeriod:
                            dateStr = '[ '+', '.join([getPD_date(dateVal).strftime("%d_%m_%Y") for dateVal in tempRes[1]])+']'
                            instrumentStr = currentInstrument + dateStr
                            screenedInstruments['ImpulsePullBack'].append(instrumentStr)  
                del ipbScreener_obj                              

            else:
                # code the short position calculations
                pass 
                print("Short Position Scans still not supported")
                sys.exit(0)
        printProgressBar(idx+1,len(stocksList),prefix='Progress:', suffix = '{:15s}'.format(currentInstrument), length = 50)
                
    if (
            len(screenedInstruments['18 Bounce Long']) > 0
        or  len(screenedInstruments['20 Bounce Long']) > 0
        or  len(screenedInstruments['50 Bounce Long']) > 0
        or  len(screenedInstruments['100 Bounce Long']) > 0
        or  len(screenedInstruments['150 Bounce Long']) > 0   
        or  len(screenedInstruments['ImpulsePullBack']) > 0   
        ):
        return [0,screenedInstruments]
    else:
        return [1,screenedInstruments]
    
                  
if __name__ == '__main__':
    
    stocksList = NSE_TradedStocks(getDate_today())
    #stocksList = [*Nifty50(),*NiftyNext50()]
    #stocksList = NSE_localAll()
    isDaily = True
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

    # Perform a daily scan or a customised scan
    if isDaily:
        endDate = getDate_today()
        print('Results with Strict Screening')
        # Daily
        result = Bounce_IPB_Stocks(stocksList,stockInfo_source=stockSource,customSession=sess,
                                   endDate=endDate,volumeCutoff=10000,historialDataTicks=365,
                                   bounce18=True,bounce50=True,bounce100=True,
                                   useDelta=False,ipbMACD_filter=False,ipb_tracePeriod=3)
        if result[0] == 0:
            for key,value in result[1].items():
                print('{}:{}\n'.format(key,value))
        else:
            print('No instruments for screening criteria')
        print('\nResults with Lenient Screening')
        # Daily
        result = Bounce_IPB_Stocks(stocksList,stockInfo_source=stockSource,customSession=sess,
                                   endDate=endDate,volumeCutoff=10000,historialDataTicks=365,
                                   EMA_check = 'Step',
                                   ignoreStochastic = True,
                                   bounce18=True,bounce50=True,bounce100=True,
                                   useDelta=False,ipbMACD_filter=False,ipb_tracePeriod=3)
        if result[0] == 0:
            for key,value in result[1].items():
                print('{}:{}\n'.format(key,value))
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
            result = Bounce_IPB_Stocks(stocksList,stockInfo_source=stockSource,customSession=sess,
                                       volumeCutoff=1000000,endDate=dateTemp,historialDataTicks=365,
                                       bounce18=True,bounce50=True,bounce100=True,
                                       useDelta=False)
            if result[0] == 0:
                totalHitDays += 1
                resultList.append('>>{}\n{}\n{}\n'.format(dateTemp.strftime("%d_%m_%Y"),str(result[1]),'-'*120)) 
            print("->Total Days with Screening Hits: {}".format(totalHitDays))

        with open('{}\{}.txt'.format('G:\Investments\Scripts\Stock_Screener\Scans','Scan'),'w') as fileobj:
            fileobj.write(''.join(resultList))        
                    












