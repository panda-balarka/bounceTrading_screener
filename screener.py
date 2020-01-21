# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:50:10 2020

@author: Balarka
"""

from auxFuncs import convertDate,getDate_previous,getDate_today,getDate_yesterday
from nselist import NSE_TradedStocks
from instrument_request import INSTRUMENT_DATA

from technicalWrapper import TECH_FXS

stocksList = NSE_TradedStocks(convertDate('20-01-2020'))

screenedList = []
currentInstrument = stocksList[0]
# ensure this value is yesterday if the script is run in the morning before trading session
# or should be today if the analysis is done after the close of the market for the present
# day
endDate = getDate_yesterday()
startDate = getDate_previous(500,endDate)

temp_obj = INSTRUMENT_DATA(currentInstrument)
temp_obj.requestData(startDate,endDate)
primaryData = temp_obj.get_primeData()
technical_obj = TECH_FXS(primaryData)
EMA18 = technical_obj.getEMA(18)
SMA50 = technical_obj.getSMA(50)
SMA100 = technical_obj.getSMA(100)
SMA200 = technical_obj.getSMA(200)
MACD50 = technical_obj.getMACD(50,100,9)
MACD18 = technical_obj.getMACD(18,50,9)
STOCH5_33 = technical_obj.getSTOCH(5,3,3)








