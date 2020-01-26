# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 21:35:09 2020

@author: Balarka
"""

from screener_backend.instrument_request import INSTRUMENT_DATA

cuurrentInstrument = 'INFY'

temp_obj = INSTRUMENT_DATA(currentInstrument,stockInfo_source)
temp_obj.requestData(startDate,endDate,customSession)
primaryData = temp_obj.get_primeData()
