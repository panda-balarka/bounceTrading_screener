# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 09:42:55 2020

@author: Balarka
"""

import requests
import pandas as pd
import time

def getQuote_data(symbol, data_range='1d', data_interval='15m'):
    res = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/{}?range={}&interval={}'.format(symbol,data_range,data_interval))
    jsonData = res.json()
    mainData = jsonData['chart']['result'][0]
    dtList = [time.strftime("%d_%m %H:%M",time.localtime(int(utdate))) for utdate in mainData['timestamp']]
    quoteDict = mainData['indicators']['quote'][0]
    dataDict = {
                'open'   : quoteDict['open'],
                'high'   : quoteDict['high'],
                'low'    : quoteDict['low'],
                'close'  : quoteDict['close'],
                'volume' : quoteDict['volume']            
                }
    
    primaryData = pd.DataFrame(dataDict)
    primaryData.index = dtList
    return (primaryData)


if __name__ == '__main__':
    
    #print(getQuote_data('SBIN.NS', '1d', '15m'))
    
    from bs4 import BeautifulSoup
    import urllib3 as url
    import certifi as cert
    name = 'INFY.NS'
    
    http = url.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=cert.where())
    html_doc = http.request('GET', 'https://finance.yahoo.com/quote/' + name + '?p=' + name)
    soup = BeautifulSoup(html_doc.data, 'html.parser')
    print(soup.find("span", class_="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)").get_text() )


