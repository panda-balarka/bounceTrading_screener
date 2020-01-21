# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""

class BOUNCESCREENER(object):

    def __init__(self,dataFrame,EMA18,EMA50,EMA100,EMA200,MACD18,MACD50,STOCH5_33):
        self.open = dataFrame['open'].tolist()
        self.high = dataFrame['high'].tolist()
        self.close = dataFrame['close'].tolist()
        self.low = dataFrame['low'].tolist()
        self.EMA18 = EMA18['EMA18'].tolist()
        self.EMA50 = EMA18['EMA18'].tolist()
        self.EMA100 = EMA18['EMA18'].tolist()
        self.EMA200 = EMA18['EMA18'].tolist()
        self.MACD18 = MACD18
        self.MACD50 = MACD50
        self.STOCH = STOCH5_33

    def isEMA_Long(self,period=10):
        tempValue_list = [self.EMA18,self.EMA50,self.EMA100,self.EMA200]
        for emaListIdx in range(len(tempValue_list)-1):
            for value in range(len(period)):
                if tempValue_list[emaListIdx][-value-1] < tempValue_list[emaListIdx+1][-value-1]:
                    # if EMAa value falls below EMAb then the EMA has become negetive 
                    return False
        return True

    def isInstrument_bounce18longMatch(self):
        if (
            (isEMA_Long) and
            (self.low[-2] < self.EMA18[-2]) and
            (MACD_pos2neg('18',12)) and
            (MACD_pos2neg('50',12)) and
            (STOCH_oversold(30,3)) and
            (self.open[-2] > self.EMA18[-2]) and
            (self.close[-2] > self.EMA18[-2]) and
            (self.close[-1] > self.high[-2]) and
            (self.close[-1] > self.open[-1]) and
            ):
            return True
        else:
            return False

    def isInstrument_bounce50longMatch(self):
        pass

    def isInstrument_bounce100longMatch(self):
        pass

    def MACD_pos2neg(self,MACDtype,period):
        pass

    def STOCH_oversold(self,threshold,period):
        pass
    

            