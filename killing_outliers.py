#!/usr/bin/env python
# coding: utf-8

# In[13]:


import pandas as pd
import numpy as np
from pandas import Series, DataFrame


def Get_Width(column):
    li = column.name.split('_')
    width = li[-2]
    return width

def Get_Length(column):
    li = column.name.split('_')
    length = li[-1]
    return length

'''
import re
def Get_Size(tittle):

    # 抽取命名里面晶体管的尺寸
    # 输入应该是单个字符串
    
    size_regex = re.compile(r'_(((\d*)D)\d*)_(((\d*)D)\d*)') # 保证了也可以匹配 1D308_1D308这种尺寸
    mo = size_regex.search(tittle)
    a, b, c, d, e, f = mo.groups()
    c = c + '.'
    f = f + '.'
    Width = a.replace(b,c)
    Length = d.replace(e,f)
    return Width, Length
'''
    
    
def Dataclean(column):
    '''数据清洗函数，用于处理含有异常值的非正态分布数据，使用了箱形图的统计思想'''    
    
    Percentile = np.percentile(column,[0,35,50,65,100]) # 计算出35，50，65，分位数
    IQR = Percentile[3] - Percentile[1]                 # 取35分位到65分位为标准
    UpLimit = Percentile[3]+IQR*2                       # 取35分位到65分位两数直接的距离*2倍作为箱须
    DownLimit = Percentile[1]-IQR*2 
    test1 = column[(column<UpLimit)][column>DownLimit]  # 筛选出一列里上下界内的元素
    S = test1.describe()                                # 得到统计描述
    S.loc[r'std/median'] = S.loc['std']/S.loc['50%']    #要求std/median<10%   standard = S.loc['std']/S.loc['50%']
    S.loc['numofoutliers'] = len(column) - S.loc['count']
    #S.loc['Width'] = Get_Size(column.name)
    #S.loc['Length'] = Get_Size(column.name)
    return S

def Drop_tittle(frame):
    '''去除不需要的测试条目,返回一个新的数据表'''
    
    def Booleancheck(tittle):
        '''去除IDOF,ISOF的检查函数'''
        if tittle[:4] in ['IDOF', 'ISOF']: # 去除IDOF,ISOF
            return False
        else:
            return True
    
    tittles = Series(frame.columns)
    mask = tittles.apply(Booleancheck) # 筛选列名的筛子
    remain_tittles = tittles[mask]
    frame = frame[remain_tittles]
    return frame



if __name__ == '__main__':
    frame = pd.read_excel(r'device_exp\A9B7792#06.xlsx') # 调整好格式的文件表的路径
    frame = Drop_tittle(frame)           # 去除不要的参数
    result = frame.apply(Dataclean)      # 对读入的表格案列按列进行dataclean的函数处理
    width_series = result.apply(Get_Width)
    length_series = result.apply(Get_Length)
    result.loc['width'] = width_series
    result.loc['length'] = length_series    
    result = result.T                    # 转置表格    
    
    result.to_excel(r'device_exp\A9B7792#06_export.xlsx')  #  输出路径'C:\\Users\\E905825\\notebook'下面的device_exp\result_export.xlsx






# In[ ]:




