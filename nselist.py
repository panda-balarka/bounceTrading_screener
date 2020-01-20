# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:43:09 2020

@author: Balarka
"""
from datetime import date
from nsepy.history import get_price_list


def NSE_TradedStocks(dateval):
    # date list used in reverse order as date method takes input as
    # (yyyy,mm,dd)
    prices = get_price_list(dt=date(dateval[2],dateval[1],dateval[0]))
    return prices['SYMBOL'].tolist()
    
if __name__ == '__main__':
    
    NSE_TradedStocks('20-01-2020')
    
    

