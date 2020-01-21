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
        self.EMA18 = EMA18

    def isEMA_Long(self,period=10):
        tempValue_list = [EMA18,EMA50,EMA100,EMA200]
        for emaDF in range(len(tempValue_list)-1):
            for value in range(len(period)):
                if tempValue_list[emaDF]['EMA'][-value] < tempValue_list[emaDF+1]['EMA'][-value]:
                    # if EMAa value falls below EMAb then the EMA has become negetive 
                    return False
        return True

            