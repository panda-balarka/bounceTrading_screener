# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 22:43:09 2020

@author: Balarka
"""

from nsepy.history import get_price_list


def NSE_TradedStocks(dateval):

    prices = get_price_list(dt=dateval)
    return prices['SYMBOL'].tolist()
    
if __name__ == '__main__':
    
    NSE_TradedStocks('20-01-2020')
    
    

