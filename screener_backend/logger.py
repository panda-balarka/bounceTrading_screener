# -*- coding: utf-8 -*-

import logging

class LOG(object):
    
    logger = logging.getLogger('tradeScreener')
    logger.propagate = False    

    fileHandler = logging.FileHandler('LastLog.log')
    formatter = logging.Formatter('{:7s}:%(asctime)s>>%(message)s'.format('%(levelname)s'))
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)    
    
    def __init__(self,logLevel='INFO'):
        levelDict = {
                     'DEBUG'    : logging.DEBUG,
                     'INFO'     : logging.INFO,
                     'WARNING'  : logging.WARNING,
                     'ERROR'    : logging.ERROR,
                     'CRITICAL' : logging.CRITICAL
                     }  
        self.fileHandler.setLevel(levelDict[logLevel.upper()])        
        
    def debug(self,ipStr):
        self.logger.debug(ipStr)
        
    def info(self,ipStr):
        self.logger.info(ipStr)

    def warning(self,ipStr):
        self.logger.warning(ipStr)

    def error(self,ipStr):
        self.logger.error(ipStr)

    def critical(self,ipStr):
        self.logger.critical(ipStr)        
        

