# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020
TODO: Many check function boundary conditions with respect to list lengths missing.
      Currently, all list lengths used inside the screening and sanity functions expect the lenght of the list to 
      be more than the threshold value or check period given

@author: Balarka
"""

class BOUNCESCREENER(object):

    def __init__(self,dataFrame,EMA18,EMA20,EMA50,EMA100,EMA150,MACD18,MACD50,STOCH5_33):
        self.open = dataFrame['open'].tolist()
        self.high = dataFrame['high'].tolist()
        self.close = dataFrame['close'].tolist()
        self.low = dataFrame['low'].tolist()
        self.EMA18 = EMA18.tolist()
        self.EMA20 = EMA20.tolist()
        self.EMA50 = EMA50.tolist()
        self.EMA100 = EMA100.tolist()
        self.EMA150 = EMA150.tolist()
        self.MACD = { '18' : MACD18,
                      '50' : MACD50
                      }
        self.STOCH = STOCH5_33
        
    def longScreener_initParams(self,ignoreStochastic=False,stochasticThreshold=30,stochasticTPeriod=3,
                                ignoreEMA=False,EMA_check='All',EMA_period=4):

        self.EMA_check = EMA_check
        self.isStochastics_OverSold = False

        # Calcualte EMA long condition state
        if ignoreEMA:
            self.isEMA_long = True
            self.isEMA18_long = True
            self.isEMA20_long = True
            self.isEMA50_long = True
        else:
            self.isEMA_long = self.calcEMA_Long('All',EMA_period)
            self.isEMA18_long = self.calcEMA_Long('18',EMA_period)
            self.isEMA20_long = self.calcEMA_Long('20',EMA_period)
            self.isEMA50_long = self.calcEMA_Long('50',EMA_period)
        # Calculate the Stochasitic condition state
        if ignoreStochastic:
            self.isStochastics_OverSold = True
        else:
            self.isStochastics_OverSold = self.isSTOCH_OverSold(stochasticThreshold,stochasticTPeriod)
        # used specifically for 18 bounce long
        self.MACD18_isPos = self.MACD_neg2pos('18',1)
        self.MACD50_isPos = self.MACD_neg2pos('50',1)
        # use for 50,100 bounce long
        self.MACD50_Ok = self.isMACD_BullBearCross_OK('50',5)
        

    def calcEMA_Long(self,EMA_type='All',period=5):
        try:
            if EMA_type == 'All':
                tempValue_list = [self.EMA18,self.EMA50,self.EMA100]            
                for emaListIdx in range(len(tempValue_list)-1):
                    for value in range(period):
                        if tempValue_list[emaListIdx][-value-1] < tempValue_list[emaListIdx+1][-value-1]:
                            # if EMAa value falls below EMAb then the EMA suggests short position
                            # so return False
                            return False
                return True
            elif EMA_type == '18':
                tempValue_list = [self.EMA18,self.EMA50] 
                for value in range(period):
                    if tempValue_list[0][-value-1] < tempValue_list[1][-value-1]:
                        # if EMAa value falls below EMAb then the EMA suggests short position
                        # so return False
                        return False
                return True
            elif EMA_type == '20':
                tempValue_list = [self.EMA20,self.EMA50] 
                for value in range(period):
                    if tempValue_list[0][-value-1] < tempValue_list[1][-value-1]:
                        # if EMAa value falls below EMAb then the EMA suggests short position
                        # so return False
                        return False
                return True
            elif EMA_type == '50':
                tempValue_list = [self.EMA50,self.EMA100]  
                for value in range(period):
                    if tempValue_list[0][-value-1] < tempValue_list[1][-value-1]:
                        # if EMAa value falls below EMAb then the EMA suggests short position
                        # so return False
                        return False
                return True 
            else:
                return False
        except:
            return True
    
    def isSTOCH_OverSold(self,threshold=30,tracePeriod=3):
        try:
            slowK_list = self.STOCH['slowk'].tolist()
            for traceIdx in range(tracePeriod):
                if slowK_list[-traceIdx-1] <= threshold:
                    return True
            return False
        except:
            return True
    
    def MACD_neg2pos(self,MACDtype,tracePeriod):
        try:
            # if macd has crossed signal line and is positive, the macdhist value will be positive
            macdHist = self.MACD[MACDtype]['macdhist'].tolist()
            for traceIdx in range(tracePeriod):
                if macdHist[-traceIdx-1] < 0:
                    return False
            return True
        except:
            return True    
        
    def isMACD_BullBearCross_OK(self,MACDtype,tracePeriod):
        try:
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
        except:
            return True
    
    def isCandle_BullishReversal(self,patternType,emaList):
        try:
            # each of the input parameter is a list of 2 or 3 values, 
            # if two : first element has the reversal candle info and the second has the confirmation candle info. 
            # This is used to checks if its a EMA bounce with Single Candle reversal or two candle reversal with original 
            # and inside bar pattern
            # if three : first element has the Bearish Candle info, the second element has the reversal candle info and 
            # the last element has the confirmation candle info. This function checks if its a EMA bounce with two candle 
            # trade through pattern
            openVals = self.open[-patternType:]
            highVals = self.high[-patternType:]
            closeVals = self.close[-patternType:]
            lowVals = self.low[-patternType:]
            emaVals = emaList[-patternType:]
            if patternType == 2:
                rvrsCandle  = 0
                cnfrmCandle = 1
                # The below conditions expand in simple term to the reversal candle's shadow cutting the EMA line and
                # the confirmation candle being bullish and closing above the reversal candle and the other conditions
                # for a long position
                if ( 
                        (lowVals[rvrsCandle] <= emaVals[rvrsCandle])
                    and (openVals[rvrsCandle] > emaVals[rvrsCandle])
                    and (closeVals[rvrsCandle] > emaVals[rvrsCandle])
                    and (lowVals[cnfrmCandle] > lowVals[rvrsCandle])
                    and (closeVals[cnfrmCandle] > highVals[rvrsCandle])
                    and (closeVals[cnfrmCandle] > openVals[cnfrmCandle])
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
                    and (closeVals[bearCandle] <= emaVals[bearCandle])
                    and (closeVals[bearCandle] < openVals[bearCandle])
                    and (openVals[rvrsCandle] <= emaVals[rvrsCandle])
                    and (closeVals[rvrsCandle] > emaVals[rvrsCandle])
                    and (closeVals[rvrsCandle] > openVals[rvrsCandle])
                    and (lowVals[rvrsCandle] < lowVals[bearCandle])
                    and (closeVals[cnfrmCandle] > openVals[cnfrmCandle])
                    and (closeVals[cnfrmCandle] > highVals[rvrsCandle])
                    and (closeVals[cnfrmCandle] > emaVals[cnfrmCandle])
                    ):
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False
        
                
    def isInstrument_bounce18longMatch(self,deltaAllowed=False,deltaValue=0.001):
        try:
            if self.EMA_check == 'All':
                isEMA_StateLong = self.isEMA_long
            else:
                isEMA_StateLong = self.isEMA18_long
            
            candlePatternMatch = (self.isCandle_BullishReversal(2,self.EMA18) 
                                  or self.isCandle_BullishReversal(3,self.EMA18))

            if deltaAllowed:
                delta = [deltaValue* closeElem for closeElem in self.close[-3:]]
                EMA18_delP = [0,0,0]
                EMA18_delN = [0,0,0]
                for posIdx in range(3):
                    EMA18_delP[-posIdx-1] = self.EMA18[-posIdx-1] + delta[-posIdx-1]
                    EMA18_delN[-posIdx-1] = self.EMA18[-posIdx-1] - delta[-posIdx-1]
                candlePatternMatch = (candlePatternMatch
                                      or self.isCandle_BullishReversal(2,EMA18_delP)
                                      or self.isCandle_BullishReversal(3,EMA18_delP)
                                      or self.isCandle_BullishReversal(2,EMA18_delN)
                                      or self.isCandle_BullishReversal(3,EMA18_delN))

            if (    
                    (isEMA_StateLong)
                and (self.isStochastics_OverSold)
                and (self.MACD18_isPos)
                and (self.MACD50_isPos)
                and (candlePatternMatch)
                ):
                return True
            else:
                return False
        except:
            return False
        
    def isInstrument_bounce20longMatch(self,deltaAllowed=False,deltaValue=0.001):
        try:
            if self.EMA_check == 'All':
                isEMA_StateLong = self.isEMA_long
            else:
                isEMA_StateLong = self.isEMA20_long
            
            candlePatternMatch = (self.isCandle_BullishReversal(2,self.EMA20) 
                                  or self.isCandle_BullishReversal(3,self.EMA20))

            if deltaAllowed:
                delta = [deltaValue* closeElem for closeElem in self.close[-3:]]
                EMA20_delP = [0,0,0]
                EMA20_delN = [0,0,0]
                for posIdx in range(3):
                    EMA20_delP[-posIdx-1] = self.EMA20[-posIdx-1] + delta[-posIdx-1]
                    EMA20_delN[-posIdx-1] = self.EMA20[-posIdx-1] - delta[-posIdx-1]
                candlePatternMatch = (candlePatternMatch
                                      or self.isCandle_BullishReversal(2,EMA20_delP)
                                      or self.isCandle_BullishReversal(3,EMA20_delP)
                                      or self.isCandle_BullishReversal(2,EMA20_delN)
                                      or self.isCandle_BullishReversal(3,EMA20_delN))

            if (    
                    (isEMA_StateLong)
                and (self.isStochastics_OverSold)
                and (self.MACD18_isPos)
                and (self.MACD50_isPos)
                and (candlePatternMatch)
                ):
                return True
            else:
                return False
        except:
            return False        

    def isInstrument_bounce50longMatch(self,deltaAllowed=False,deltaValue=0.005):
        try:
            if self.EMA_check == 'All':
                isEMA_StateLong = self.isEMA_long
            else:
                isEMA_StateLong = self.isEMA50_long 

            candlePatternMatch = (self.isCandle_BullishReversal(2,self.EMA50) 
                                  or self.isCandle_BullishReversal(3,self.EMA50))  

            if deltaAllowed:         
                # the EMA50 is not so accurate, so we try to screen the candle stick patterns with EMA50, 
                # EMA50 + 0.5%(Close) and EMA100 - 0.5%(Close)
                # max number of elements needed are the last 3
                delta = [deltaValue * closeElem for closeElem in self.close[-3:]]
                EMA50_delP = [0,0,0]
                EMA50_delN = [0,0,0]
                for posIdx in range(3):
                    EMA50_delP[-posIdx-1] = self.EMA50[-posIdx-1] + delta[-posIdx-1]
                    EMA50_delN[-posIdx-1] = self.EMA50[-posIdx-1] - delta[-posIdx-1]       
                candlePatternMatch = (candlePatternMatch
                                      or self.isCandle_BullishReversal(2,EMA50_delP)
                                      or self.isCandle_BullishReversal(3,EMA50_delP)
                                      or self.isCandle_BullishReversal(2,EMA50_delN)
                                      or self.isCandle_BullishReversal(3,EMA50_delN))                

            if (    
                    (isEMA_StateLong)
                and (self.isStochastics_OverSold)
                and (self.MACD50_Ok)
                and (candlePatternMatch)
                ):
                return True
            else:
                return False
        except:
            return False

    def isInstrument_bounce100longMatch(self,deltaAllowed=False,deltaValue=0.01):
        try:
            if self.EMA_check == 'All':
                isEMA_StateLong = self.isEMA_long
            else:
                # EMA 100+ calculation are not so accurate, therefore use EMA50 to confirm an uptrend and manually
                # check for the actual EMA trend style
                isEMA_StateLong = self.isEMA50_long

            candlePatternMatch = (self.isCandle_BullishReversal(2,self.EMA100) 
                                  or self.isCandle_BullishReversal(3,self.EMA100))
            
            if deltaAllowed:
                # the EMA100 is not accurate, so we try to screen the candle stick patterns with EMA100, 
                # EMA100 + 1%(Close) and EMA100 - 1%(Close)
                # max number of elements needed are the last 3
                delta = [0.01 * closeElem for closeElem in self.close[-3:]]
                EMA100_delP = [0,0,0]
                EMA100_delN = [0,0,0]
                for posIdx in range(3):
                    EMA100_delP[-posIdx-1] = self.EMA100[-posIdx-1] + delta[-posIdx-1]
                    EMA100_delN[-posIdx-1] = self.EMA100[-posIdx-1] - delta[-posIdx-1]
                candlePatternMatch = (candlePatternMatch
                                      or self.isCandle_BullishReversal(2,EMA100_delP)
                                      or self.isCandle_BullishReversal(3,EMA100_delP)
                                      or self.isCandle_BullishReversal(2,EMA100_delN)
                                      or self.isCandle_BullishReversal(3,EMA100_delN))                    

            if (    
                    (isEMA_StateLong)
                and (self.isStochastics_OverSold)
                and (self.MACD50_Ok)
                and (candlePatternMatch)
                ):
                return True
            else:
                return False
        except:
            return False
        
    def isInstrument_bounce150longMatch(self,deltaAllowed=False,deltaValue=0.01):
        try:
            if self.EMA_check == 'All':
                isEMA_StateLong = self.isEMA_long
            else:
                # EMA 100+ calculation are not so accurate, therefore use EMA50 to confirm an uptrend and manually
                # check for the actual EMA trend style
                isEMA_StateLong = self.isEMA50_long

            candlePatternMatch = (self.isCandle_BullishReversal(2,self.EMA150) 
                                  or self.isCandle_BullishReversal(3,self.EMA150))
            
            if deltaAllowed:
                # the EMA100 is not accurate, so we try to screen the candle stick patterns with EMA100, 
                # EMA100 + 1%(Close) and EMA100 - 1%(Close)
                # max number of elements needed are the last 3
                delta = [0.01 * closeElem for closeElem in self.close[-3:]]
                EMA150_delP = [0,0,0]
                EMA150_delN = [0,0,0]
                for posIdx in range(3):
                    EMA150_delP[-posIdx-1] = self.EMA150[-posIdx-1] + delta[-posIdx-1]
                    EMA150_delN[-posIdx-1] = self.EMA150[-posIdx-1] - delta[-posIdx-1]
                candlePatternMatch = (candlePatternMatch
                                      or self.isCandle_BullishReversal(2,EMA150_delP)
                                      or self.isCandle_BullishReversal(3,EMA150_delP)
                                      or self.isCandle_BullishReversal(2,EMA150_delN)
                                      or self.isCandle_BullishReversal(3,EMA150_delN))                    

            if (    
                    (isEMA_StateLong)
                and (self.isStochastics_OverSold)
                and (self.MACD50_Ok)
                and (candlePatternMatch)
                ):
                return True
            else:
                return False
        except:
            return False        

    

            