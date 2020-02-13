# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 07:21:41 2020

@author: Balarka
"""

from talib.abstract import EMA,SMA,MACD,STOCH

class TALIB_CALC_ERROR(Exception):
    pass

class TECH_FXS(object):
    
    def __init__(self,ipData):
        self.data = ipData
        
    def getEMA(self,period=18):
        try:
            return EMA(self.data,timeperiod=period)
        except:
            raise TALIB_CALC_ERROR("EMA Calculation Error")
    
    def getSMA(self,period=50):
        try:
            return SMA(self.data,timeperiod=period)
        except:
            raise TALIB_CALC_ERROR("SMA Calculation Error")
    
    def getMACD(self,fastP=12,slowP=26,signalP=9):
        try:
            return MACD(self.data,fastperiod=fastP,
                        slowperiod=slowP,
                        signalperdiod=signalP)
        except:
            raise TALIB_CALC_ERROR("MACD Calculation Error")
    
    def getSTOCH(self,fastKPeriod=14,slowKPeriod=5,slowDPeriod=5):
        try:
            return STOCH(self.data,fastk_period=fastKPeriod,slowk_period=slowKPeriod,slowd_period=slowDPeriod)
        except:
            raise TALIB_CALC_ERROR("MACD Calculation Error")
        
    def getVWAP(self):
        try:
            cumulitiveVol = self.data['volume'].cumsum().tolist()
            cumulitivePrice = (self.data['volume'] * (self.data['high'] + self.data['low'] + self.data['close'] + self.data['open'])/4).cumsum()
            vwap = cumulitivePrice / cumulitiveVol
            return vwap
        except:
            raise TALIB_CALC_ERROR("VWAP Calculation Error")
            
