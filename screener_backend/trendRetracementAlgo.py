# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 21:35:09 2020
TODO: Many check function boundary conditions with respect to list lengths missing.
      Currently, all list lengths used inside the screening and sanity functions expect the lenght of the list to 
      be more than the threshold value or check period given

@author: Balarka
"""

class TREND_RETRACEMENTSCREENER(object):
    
    def __init__(self,dataFrame,EMA20,EMA40,SMA50,SMA100,SMA150,SMA200):
        self.open = dataFrame['open'].tolist()
        self.high = dataFrame['high'].tolist()
        self.close = dataFrame['close'].tolist()
        self.low = dataFrame['low'].tolist()
        self.EMA20 = EMA20.tolist()        
        self.EMA40 = EMA40.tolist()
        self.SMA50 = SMA50.tolist()
        self.SMA100 = SMA100.tolist()
        self.SMA150 = SMA150.tolist()
        self.SMA200 = SMA200.tolist()  
        self.dates = list(dataFrame.index.values)
        self.tracePeriod = 3
        self.hitPos = []    
        self.infoLst = []
    
    def checkEMAstate(self,emaPeriod=15):
        try:
            EMA20x40_flag = True
            SMA50x100_flag = True
            SMA50x150_flag = True
            CPx200_flag = False
            # check if EMA20>EMA40
            for value in range(emaPeriod):
                if self.EMA20[-value-1] < self.EMA40[-value-1]:
                    EMA20x40_flag = False
                    break
                
            # check if SMA50>SMA100
            for value in range(emaPeriod):
                if self.SMA50[-value-1] < self.SMA100[-value-1]:
                    SMA50x100_flag = False
                    break 
                
            # check if SMA50>SMA150
            for value in range(emaPeriod):
                if self.SMA50[-value-1] < self.SMA150[-value-1]:
                    SMA50x150_flag = False
                    break  
            
            # CP > SMA200
            for value in range(self.tracePeriod):
                if self.close[-value-2] > self.SMA200[-value-2]:
                    CPx200_flag = True
                    break
                
            if EMA20x40_flag and SMA50x100_flag:
                self.infoLst.append("EMA20>EMA40")
                if SMA50x150_flag or CPx200_flag:
                    if SMA50x150_flag: self.infoLst.append("SMA50>SMA150")
                    if CPx200_flag: self.infoLst.append("CP>SMA200")
                    return True
                else:
                    return False
            else:
                return False
        except:
            return False
    
    def testMA_Cross(self,lowVal,idx):
        
        try:
            bounceFlag = False
            if lowVal < self.EMA20[idx]:
                self.infoLst.append('Pivot of EMA20')
                bounceFlag |= True
            
            if lowVal < self.SMA50[idx]:
                self.infoLst.append('Pivot of SMA50')
                bounceFlag |= True
                
            if lowVal < self.SMA100[idx]:
                self.infoLst.append('Pivot of SMA100')
                bounceFlag |= True
    
            if lowVal < self.SMA150[idx]:
                self.infoLst.append('Pivot of SMA150')
                bounceFlag |= True  
                
            if lowVal < self.SMA200[idx]:
                self.infoLst.append('Pivot of SMA200')
                bounceFlag |= True    
                
            return bounceFlag
        except:
            return False
        
            
    def findPivot_dip(self):
        
        try:
            for value in range(self.tracePeriod):
                if self.low[-value-2] < self.low[-value-1] and self.low[-value-2] < self.low[-value-3]:
                    self.infoLst.append("Pivot at {}".format(self.dates[-value-2]))
                    if self.testMA_Cross(self.low[-value-2],(-value-2)):
                        return True
            return False
        except:
            return False
                
        
    def isInstrumentValid(self,tracePeriod=3,EMAcheckPeriod=15):
        
        self.traceperiod = tracePeriod
        EMAstate = self.checkEMAstate(EMAcheckPeriod)
        
        if EMAstate:
            pivotSearch_result = self.findPivot_dip()
            if pivotSearch_result:
                return [True,','.join(self.infoLst)]
            else:
                return [False,None]
        else:
            return [False,None]
        
        
    
        
        