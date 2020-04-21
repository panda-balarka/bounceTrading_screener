# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 19:17:00 2020

@author: Balarka
"""

class INTRADAY_MOMENTUM_SCREENER(object):

    def __init__(self,ohlc_df):
        self.open = ohlc_df['open'].tolist()[0]
        self.high = ohlc_df['high'].tolist()[0]
        self.low = ohlc_df['low'].tolist()[0]
        self.close = ohlc_df['close'].tolist()[0]
        self.volume = ohlc_df['volume'].tolist()[0]
    
    def scanInstrument(self,cutoffVolume=500000,OHOL_margin=0.5,OC_change=3):
        
        # check if the instrument has enough liquidity in terms of volume
        if self.volume >= cutoffVolume:
            # check for bullish momentum entry
            if ((self.open-(self.open*OHOL_margin/100)) < self.low < self.open) and \
                (abs((self.close-self.open)/self.open * 100) >= OC_change):
                return "Bullish"
            
            if ((self.open+(self.open*OHOL_margin/100)) > self.high > self.open) and \
                (abs((self.close-self.open)/self.open * 100) >= OC_change):
                return "Bearish"
        
        return "Invalid"

if __name__ == "__main__":

    import pandas as pd
    # local testing of screener algorithm
    print("Local Testing of screener class: INTRADAY_MOMENTUM_SCREENER")
    valdict = {
        'open'   : [],
        'high'   : [],
        'low'    : [],
        'close'  : [],
        'volume' : []
    }
    tcDict = {
        # Bullish Setup TestCase Values
        0 : [[100],[110],[99.75],[105],[600000],"Bullish"], # All conditions for bullish setup met
        1 : [[100],[110],[99.25],[105],[600000],"Invalid"], # Low is lesser the Open threshold with OHOL_margin of 0.5%
        2 : [[100],[110],[99.75],[101],[600000],"Invalid"], # OC_change is less than 2%
        3 : [[100],[110],[99.75],[105],[60000],"Invalid"],  # Volume less than cutoffVolume
        # Bearish Setup TestCase Values
        4 : [[100],[100.25],[90],[95],[600000],"Bearish"], # All conditions for bearish setup met        
        5 : [[100],[100.75],[90],[95],[600000],"Invalid"], # High is greater the Open threshold with OHOL_margin of 0.5%
        6 : [[100],[100.25],[90],[99],[600000],"Invalid"], # OC_change is less than 2%
        7 : [[100],[100.25],[90],[95],[60000],"Invalid"],  # Volume less than cutoffVolume
    }
    for key,value in tcDict.items():
        valdict['open'],valdict['high'],valdict['low'],valdict['close'],valdict['volume'] = value[0],value[1],value[2],value[3],value[4]
        df = pd.DataFrame(valdict)
        temp_obj = INTRADAY_MOMENTUM_SCREENER(df)
        result = temp_obj.scanInstrument(cutoffVolume=600000,OHOL_margin=0.5,OC_change=2)
        if result == value[5]:
            print("TestCase {}: Passed".format(key))
        else:
            print("TestCase {}: Failed".format(key))





