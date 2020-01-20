# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 23:03:36 2020

@author: a
"""

def convertDate(ipdate):
    # generic date inputs can be seperated by the below seperators
    # convert the date to a list for easy use with datetime methods
    dateSeparatorList = ['-','/','\\','_']
    for separator in dateSeparatorList:
        if separator in ipdate:
            dateval = ipdate.strip().split(separator)
            break
    for idx in range(len(dateval)):
        dateval[idx] = int(dateval[idx])
    
    return dateval