# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd
import time


class AudioDB:
    """deal with DB"""
    df = pd.DataFrame()
    colDic = {}
    reColDic = {}

    def __init__(self,filename):
        self.filename = filename
        self.getCsv()
        self.setColDic()

    def getCsv(self):
        self.df = pd.DataFrame(pd.read_csv(self.filename))
        #print self.df

    def getValue(self,row,col):
        #如果传入的列名
        if type(col) is not int:
            col = self.colDic.get(col)

        return self.df.iat[row,col]

    def setValue(self,row,col,value):
        # 如果传入的列名
        if type(col) is not int:
            col = self.colDic.get(col)

        self.df.iat[row,col] = value

    def setColDic(self):
        for i in range(self.df.shape[1]):
            self.colDic[self.df.columns[i]] = i
            self.reColDic[i] = self.df.columns[i]


    def savCsv(self):
        times = str(time.localtime().tm_year) + '_' + str(time.localtime().tm_mon) + '_' + str(time.localtime().tm_mday) + '_'+str(time.localtime().tm_hour) +'_'+ str(time.localtime().tm_min)
        filename = 'result' + times +'.csv'
        self.df.to_csv(filename)








if __name__ == '__main__':
    t = AudioDB('db.csv')
    print t
    print t.getValue(0,'question')
    t.setValue(0,'question','三个火念什么')

    print t.getValue(0, 'question')
    t.savCsv()







