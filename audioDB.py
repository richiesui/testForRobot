# -*- coding: UTF-8 -*-

import numpy as np
import pandas as pd


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








if __name__ == '__main__':
    t = AudioDB('db.csv')
    print t
    print t.getValue(0,'question')
    t.setValue(0,'question','三个火念什么')

    print t.getValue(0, 'question')






