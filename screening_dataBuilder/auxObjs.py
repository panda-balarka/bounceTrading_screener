# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 19:47:07 2020

@author: Balarka
"""

class BounceData_Dict(object):
    
    def __init__(self):
        self.DataDict = {
                          'date'            : [],
                          'result'          : [],
                          'time4trade'      : [],
                          'low1'            : [],   # normalise
                          'close1'          : [],   # normalise
                          'openR'           : [],   # normalise
                          'highR'           : [],   # normalise
                          'lowR'            : [],   # normalise
                          'closeR'          : [],   # normalise
                          'openC'           : [],   # normalise
                          'highC'           : [],   # normalise
                          'lowC'            : [],   # normalise
                          'closeC'          : [],   # normalise
                          'entryP'          : [],   # normalise
                          'stoplossP'       : [],   # normalise
                          'targetP'         : [],   # normalise
                          'vol3avg'         : [],   # normalise
                          'macdHist3var'    : [],   # normalise
                          'stochastic'      : [],   # do not normalise
                          'delivery'        : [],   # do not normalise                          
                          'rscnifty50'      : [],   # do not normalise
                          'niftylong'       : [],   # one hot encoding
                          'bounceType'      : [],   # one hot encoding
                          }