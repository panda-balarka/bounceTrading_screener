# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 20:23:37 2020

@author: Balarka
"""

from screener_backend.intraday_instrument_request import getQuote_data as qRequest
from screener_backend.technicalWrapper import TECH_FXS

def intraDay_scanner():
    instrumentDf = qRequest('SBIN.NS','1d','15m')
    techObj = TECH_FXS(instrumentDf)
    macd12 = techObj.getMACD()['macdhist']
    vwap = techObj.getVWAP().tolist()
    
    
    
intraDay_scanner()