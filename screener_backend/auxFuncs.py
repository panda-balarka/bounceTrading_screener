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

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()