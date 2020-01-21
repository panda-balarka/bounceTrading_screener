# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020
TODO: Many check function boundary conditions with respect to list lengths missing.

@author: Balarka
"""

class BOUNCESCREENER(object):

    def __init__(self,dataFrame,EMA18,EMA50,EMA100,EMA200,MACD18,MACD50,STOCH5_33):
        self.open = dataFrame['open'].tolist()
        self.high = dataFrame['high'].tolist()
        self.close = dataFrame['close'].tolist()
        self.low = dataFrame['low'].tolist()
        self.EMA18 = EMA18.tolist()
        self.EMA50 = EMA50.tolist()
        self.EMA100 = EMA100.tolist()
        self.EMA200 = EMA200.tolist()
        self.MACD = { '18' : MACD18,
                      '50' : MACD50
                      }
        self.STOCH = STOCH5_33
        
    def longScreener_initParams(self,stochasticThreshold=30,stochasticTPeriod=5):
        
        self.isEMA_StateLong = self.isEMA_Long(4)
        self.isStochastics_OverSold = self.isSTOCH_OverSold(stochasticThreshold,stochasticTPeriod)
        # used specifically for 18 bounce long
        self.MACD18_isPos = self.MACD_neg2pos('18',1)
        self.MACD50_isPos = self.MACD_neg2pos('50',1)
        # use for 50,100 bounce long
        self.MACD50_Ok = self.isMACD_BullBearCross_OK('50',5)
        

    def isEMA_Long(self,period=5):
        tempValue_list = [self.EMA18,self.EMA50,self.EMA100]
        # EMA200 Calculations are not so accurate, so ignored until an alternative solution can be implemented
        # tempValue_list = [self.EMA18,self.EMA50,self.EMA100,self.EMA200]
        for emaListIdx in range(len(tempValue_list)-1):
            for value in range(period):
                if tempValue_list[emaListIdx][-value-1] < tempValue_list[emaListIdx+1][-value-1]:
                    # if EMAa value falls below EMAb then the EMA suggests short position
                    # so return False
                    return False
        return True
    
    def isSTOCH_OverSold(self,threshold=30,tracePeriod=3):
        slowK_list = self.STOCH['slowk'].tolist()
        for traceIdx in range(tracePeriod):
            if slowK_list[-traceIdx-1] <= threshold:
                return True
        return False
    
    def MACD_neg2pos(self,MACDtype,tracePeriod):
        # if macd has crossed signal line and is positive, the macdhist value will be positive
        macdHist = self.MACD[MACDtype]['macdhist'].tolist()
        for traceIdx in range(tracePeriod):
            if macdHist[-traceIdx-1] < 0:
                return False
        return True
    
    def isMACD_BullBearCross_OK(self,MACDtype,tracePeriod):
        # macdhist provides the difference between macd and macdSignal, can be used to check when
        # the macd went bearish
        macdHist = self.MACD[MACDtype]['macdhist'].tolist()     
        # if MACD is already positive, then no further checks
        if macdHist[-1] > 0:
            return True
        # counter to check when the MACD went from Pos to Neg value
        posCtr = 0
        # loop and calculate how long the MACD has been negetive
        for traceIdx in range(len(macdHist)):
            if macdHist[-traceIdx-1] < 0:
                posCtr += 1
            else:
                break
        if posCtr >= tracePeriod:
            return True
        else:
            return False
    
    def isCandle_BullishReversal(self,patternType,emaType):
        # each of the input parameter is a list of 2 or 3 values, 
        # if two : first element has the reversal candle info and the second has the confirmation candle info. 
        # This is used to checks if its a EMA bounce with Single Candle reversal or two candle reversal with original 
        # and inside bar pattern
        # if three : first element has the Bearish Candle info, the second element has the reversal candle info and 
        # the last element has the confirmation candle info. This function checks if its a EMA bounce with two candle 
        # trade through pattern
        emaDict = {
                    '18' : self.EMA18,
                    '50' : self.EMA50,
                    '100' : self.EMA100,
                    }
        openVals = self.open[-patternType:]
        highVals = self.high[-patternType:]
        closeVals = self.close[-patternType:]
        lowVals = self.low[-patternType:]
        emaVals = emaDict[emaType][-patternType:]
        if patternType == 2:
            rvrsCandle  = 0
            cnfrmCandle = 1
            # The below conditions expand in simple term to the reversal candle's shadow cutting the EMA line and
            # the confirmation candle being bullish and closing above the reversal candle and the other conditions
            # for a long position
            if ( 
                    (lowVals[rvrsCandle] < emaVals[rvrsCandle])
                and (openVals[rvrsCandle] > emaVals[rvrsCandle])
                and (closeVals[rvrsCandle] > emaVals[rvrsCandle])
                and (closeVals[cnfrmCandle] > highVals[rvrsCandle])
                and (closeVals[cnfrmCandle] > closeVals[cnfrmCandle])
                ):
                return True
            else:
                return False
        elif patternType == 3:
            bearCandle = 0
            rvrsCandle = 1
            cnfrmCandle = 2
            # The below conditions expand in simple term to a bearish and bullish candle cutting through an EMA line
            # a confirmation bullish candle closing above the high of the bullish reversal candle
            if (
                    (openVals[bearCandle] > emaVals[bearCandle])
                and (closeVals[bearCandle] < emaVals[bearCandle])
                and (openVals[rvrsCandle] < emaVals[rvrsCandle])
                and (closeVals[rvrsCandle] > emaVals[rvrsCandle])
                and (closeVals[cnfrmCandle] > openVals[cnfrmCandle])
                and (closeVals[cnfrmCandle] > highVals[rvrsCandle])
                ):
                return True
            else:
                return False            
        
                
    def isInstrument_bounce18longMatch(self):
        if (    
                (self.isEMA_StateLong)
            and (self.isStochastics_OverSold)
            and (self.MACD18_isPos)
            and (self.MACD50_isPos)
            and (self.isCandle_BullishReversal(2,'18') or self.isCandle_BullishReversal(3,'18'))
            ):
            return True
        else:
            return False

    def isInstrument_bounce50longMatch(self):
        if (    
                (self.isEMA_StateLong)
            and (self.isStochastics_OverSold)
            and (self.MACD50_Ok)
            and (self.isCandle_BullishReversal(2,'50') or self.isCandle_BullishReversal(3,'50'))
            ):
            return True
        else:
            return False

    def isInstrument_bounce100longMatch(self):
        if (    
                (self.isEMA_StateLong)
            and (self.isStochastics_OverSold)
            and (self.MACD50_Ok)
            and (self.isCandle_BullishReversal(2,'100') or self.isCandle_BullishReversal(3,'100'))
            ):
            return True
        else:
            return False

    

            