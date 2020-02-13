# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 21:35:09 2020
TODO: Many check function boundary conditions with respect to list lengths missing.
      Currently, all list lengths used inside the screening and sanity functions expect the lenght of the list to 
      be more than the threshold value or check period given

@author: Balarka
"""

class IPBSCREENER(object):
    
    def __init__(self,dataFrame,EMA6,EMA18,EMA50,EMA100,MACD12):
        self.open = dataFrame['open'].tolist()
        self.high = dataFrame['high'].tolist()
        self.close = dataFrame['close'].tolist()
        self.low = dataFrame['low'].tolist()
        self.EMA6 = EMA6.tolist()        
        self.EMA18 = EMA18.tolist()
        self.EMA50 = EMA50.tolist()
        self.EMA100 = EMA100.tolist()
        self.MACD12 = MACD12    
        self.dates = list(dataFrame.index.values)
        self.patternPos = []
        
    def longScreener_initParams(self,EMA_checkPeriod,EMA_checkType):
        
        self.EMA_longState = self.isEMA_long(EMA_checkPeriod,EMA_checkType)
        
    def isEMA_long(self,checkPeriod=5,checkType='18>50'):
        try:
            if checkType=='All':
                tempValue_list = [self.EMA18,self.EMA50,self.EMA100]            
                for emaListIdx in range(len(tempValue_list)-1):
                    for value in range(checkPeriod):
                        if tempValue_list[emaListIdx][-value-1] < tempValue_list[emaListIdx+1][-value-1]:
                            # if EMAa value falls below EMAb then the EMA suggests short position
                            # so return False
                            return False
                return True    
            elif checkType=='18>50':
                tempValue_list = [self.EMA18,self.EMA50] 
                for value in range(checkPeriod):
                    if tempValue_list[0][-value-1] < tempValue_list[1][-value-1]:
                        # if EMAa value falls below EMAb then the EMA suggests short position
                        # so return False
                        return False
                return True
            else:
                return False                
        except:
            return False
        
    def getNeg2Pos_CrossOverPosition(self,valList):
        try:
            bool_list = []
            for macdHistVal in valList:
                bool_list.append(macdHistVal > 0)
    
            if bool_list[-1]:
                for traceIdx in range(len(bool_list)):
                    if not(bool_list[-traceIdx-2]):
                        return -traceIdx-2
        except:
            pass
        
    def checkIPB_pattern(self,position,swingHighPeriod=2):
        positionsList = [position-1,position,position+1]
        
        patternMatch = False
        for posIdx in positionsList:
            if posIdx == -1 or posIdx == 0:
                patternMatch = patternMatch or False
            else:
                patternMatch = patternMatch or self.tryPatternMatch(posIdx,swingHighPeriod) 
        
        return patternMatch
    
    def tryPatternMatch(self,position,swingHighPeriod=2):
        try:
            # Check whether this current position is a swing high
            for periodIdx in range(swingHighPeriod):
                if self.high[position-periodIdx-1] > self.high[position]:
                    return False
                
            # first reference would always be with Swing High Candle
            if (    # is it a SH followed by PB candle
                    ((self.high[position] > self.high[position+1]) and (self.low[position] > self.low[position+1])) 
                    # is it a SH followed by IB candle
                 or ((self.high[position] > self.high[position+1]) and (self.low[position] < self.low[position+1]))
                 ):  
                self.patternPos.append(self.dates[position])
                return True
            return False
        except:
            return False
        
    def isInstrument_impulsePullBack(self,MACD_check=True,signalThresholdPeriod=5,swingHighPeriod=2):
        try:
            
            isMACD_bullish = (self.MACD12['macdhist'].tolist()[-1] > 0) or not(MACD_check)
            
            signalPos_list = []
            signalPos_list.append(self.getNeg2Pos_CrossOverPosition(self.MACD12['macdhist'].tolist()))
            
            if isMACD_bullish:
                emaDiff_list = [self.EMA6[idx] - self.EMA18[idx] for idx in range(len(self.EMA6))] 
                signalPos_list.append(self.getNeg2Pos_CrossOverPosition(emaDiff_list))
                
            # remove duplicates by using set function
            signalPos_list = list(set(signalPos_list))
            
            isPullBack_pattern = False
            for position in signalPos_list:
                isPullBack_pattern = isPullBack_pattern or self.checkIPB_pattern(position,swingHighPeriod)
                
            if self.EMA_longState and isPullBack_pattern:
                return [True,self.patternPos]
            else:
                return [False,'']
        except:
            return [False,'']
            

# Script standalone selftest
if __name__ == '__main__':
    from instrument_request import INSTRUMENT_DATA
    from auxFuncs import getDate_today,getDate_yesterday,getDate_previous,getPD_date
    import requests    
    
    currentInstrument = 'ZEEL'
    stockInfo_source = 'YAHOO'
    
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
    
    endDate = getDate_today()
    startDate = getDate_previous(365,endDate)
    
    
    temp_obj = INSTRUMENT_DATA(currentInstrument,stockInfo_source)
    temp_obj.requestData(startDate,endDate,sess)
    primaryData = temp_obj.get_primeData()
    
    screenedInstruments = []
    
    from technicalWrapper import TECH_FXS
    technical_obj = TECH_FXS(primaryData)
    # EMAs are Pandas Series type
    EMA6 = technical_obj.getEMA(6)
    EMA18 = technical_obj.getEMA(18)
    EMA50 = technical_obj.getEMA(50)
    EMA100 = technical_obj.getEMA(100)
    EMA200 = technical_obj.getSMA(200)
    MACD12 = technical_obj.getMACD(12,26,9)
    
    ipbScreener_obj = IPBSCREENER(primaryData,EMA6,EMA18,EMA50,EMA100,MACD12)
    ipbScreener_obj.longScreener_initParams(5,'18>50')                
    result = ipbScreener_obj.isInstrument_impulsePullBack(MACD_check=True)
    if result[0]:
        dateStr = '*'+'*'.join([getPD_date(dateVal).strftime("%d_%m_%Y") for dateVal in result[1]])
        instrStr = currentInstrument + dateStr
        print(instrStr)
                
        
            


                
