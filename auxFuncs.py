# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 23:03:36 2020

@author: a
"""
from datetime import date,timedelta

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
    
    # date list used in reverse order as date method takes input as
    # (yyyy,mm,dd)
    return date(dateval[2],dateval[1],dateval[0])

def getDate_previous(difference_in_days,dateReference):
    return (dateReference - timedelta(days=difference_in_days))

def getDate_today():
    return date.today()

def getDate_yesterday():
    return (date.today() - timedelta(days=1))