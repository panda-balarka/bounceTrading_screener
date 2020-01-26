# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 07:21:41 2020

@author: Balarka
"""

from talib.abstract import EMA,SMA,MACD,STOCH

class TECH_FXS(object):
    
    def __init__(self,ipData):
        self.data = ipData
        
    def getEMA(self,period=18):
        return EMA(self.data,timeperiod=period)
    
    def getSMA(self,period=50):
        return SMA(self.data,timeperiod=period)
    
    def getMACD(self,fastP=12,slowP=26,signalP=9):
        return MACD(self.data,fastperiod=fastP,
                       slowperiod=slowP,
                       signalperdiod=signalP)
    
    def getSTOCH(self,fastKPeriod=14,slowKPeriod=5,slowDPeriod=5):
        return STOCH(self.data,fastk_period=fastKPeriod,slowk_period=slowKPeriod,slowd_period=slowDPeriod)

