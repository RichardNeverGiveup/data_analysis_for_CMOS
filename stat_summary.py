import numpy as np
import pandas as pd
from pandas import DataFrame, Series

'''
1.读入数据并且去除不需要的IDOF, ISOF，得到原始数据每行的测试点个数Orin
2.预清洗（35-65分位数法），将超出的点设置为NAN
3.给左右两个相同的testkey找出原始名
4.按原始名将左右两个相同的testkey按行去除NAN以后再连接在一起构成更长的一行
  2*Orin - 两行合一行的测试点个数（1st） = 第一次清洗去除的个数
5.对二合一的行进行循环清洗（25-75分位数法），直到std/meidian<10%，现在每行
  的个数是（2nd），2nd-1st = 第二次清洗去除的个数
6.从原始名中提取出W,L

'''
#1.读入数据并且去除不需要的IDOF, ISOF，得到原始数据每行的测试点个数Orin
def content_check(tittle, *p):
    '''check whether the testkey in the list is in the tittle.
    p is of arbitrary length, p = ['IDOF','ISOF','VTLB1']'''
    flag = True
    for i in p:#['IDOF','ISOF','VTLB1']: 
        if tittle.find(i) == 0: # if find i in the tittle, 0 will be returned
            flag = False
    return flag

def drop_tittle(df, *p):
    '''the testkey in p should be drop from the dataframe '''
    tittles = Series(df.columns)
    param = p
    mask = tittles.apply(content_check, args=(param))
    tittles = tittles[mask]
    return df[tittles]


#2.预清洗（35-65分位数法），将超出的点设置为NAN
def column_preclean(column):
    Percentile = np.percentile(column,[0,35,50,65,100])
    IQR = Percentile[3] - Percentile[1]
    Up = Percentile[3] + IQR*2
    Low = Percentile[1] - IQR*2
    column[column>Up] = np.nan
    column[column<Low] = np.nan

    return column

def data_preclean(df):
    df.apply(column_preclean)
    return df


#3.给左右两个相同的testkey找出原始名
def get_parameter(column):    
    '''得到脱离testplan格式的真正测试项目名称'''    
    item, mos, _, width, length = column.name.split('_')
    #original = item + '_' + mos + '_' + width + '_' + length
    original = '_'.join((item, mos, width, length))
    return original

#4.按原始名将左右两个相同的testkey按行去除NAN以后再连接在一起构成更长的一行
def concatenate_columns(dataframe):  # 把两列合一的函数
    a = dataframe
    return np.concatenate([a.iloc[:,0],a.iloc[:,1]])

def combine_data(df):
    '''得到了两列合一的数据'''
    combined_data = DataFrame([])
    for i in df.columns.unique():
        combined_data[i] = concatenate_columns(df[i])
    return combined_data


#5.对二合一的行进行循环清洗（25-75分位数法），直到std/meidian<10%，现在每行的个数是（2nd），2nd-1st = 第二次清洗去除的个数
def column_2ndclean(column):
    Percentile = np.percentile(column,[0,35,50,65,100])
    IQR = Percentile[3] - Percentile[1]
    Up = Percentile[3] + IQR*1.5
    Low = Percentile[1] - IQR*1.5
    column = column[(column<Up)][column>Low]
    return column

def second_dataclean(df):
    '''这一方法可以调整成返回经过清洗之后的原始数据，需要处理索引，因为直接的列拼凑会有空值
    调整成df.to_excel(r'cleaned_rawdata.xlsx')'''
    second_datacleaned = DataFrame([])
    for i in df.columns:
        column = df[i].dropna()
        column = column_2ndclean(column)
        stat = column.describe()
        second_datacleaned[i] = stat
    return second_datacleaned


'''
# 这样重新构造的df还是有NAN是因为每列去除的点数不同，拼起来会有索引错位。
second_datacleaned = DataFrame([])
for i in combined_data.columns:        
    column = combined_data[i].dropna()
    second_datacleaned[i] = column
second_datacleaned   
'''


'''
# 这个方法会陷入死循环，暂时没调试出结果
def second_dataclean(combined_data):   
    second_datacleaned = DataFrame([])
    for i in combined_data.columns:        
        column = combined_data[i].dropna()    # 先去除这列的空值
        while True:
            column = column_2ndclean(column)
            if (column.std()/column.median()) < 0.1:
                break
        second_datacleaned[i] = column
    return second_datacleaned
'''


'''
# 之前直接构造出新的DF然后apply(second_dataclean)或者apply(describe)会出问题是因为新构造的里面又会有空值可以用列版本的函数+apply来解决
def second_dataclean(column):
    column = column.dropna()
    column = column_2ndclean(column)
    stat = column.describe()
    secondcleaned_col = stat
    return secondcleaned_col

# 配合apply使用    
combined_data.apply(second_dataclean)
'''
# 6.从原始名中提取出W,L
def Get_Width(column):
    li = column.name.split('_')
    width = li[-2]
    return width

def Get_Length(column):
    li = column.name.split('_')
    length = li[-1]
    return length

def replace_size(size):
    '''把文字size转换成数字'''
    if size[0].isdigit():
        size = size.replace('D','.')
    else: 
        size = size.replace('D','0.')
    return size

if __name__ == '__main__':
    '''main函数内容'''
    df = pd.read_excel(r'device_exp\data#6.xlsx') # 读入数据
    param = ['IDOF','ISOF','VTLB1'] # 要从原始数据剔除的测试参数
    frame = drop_tittle(df, *param)
    Orgin = frame.shape[0] # 原始测试数据点数
    precleaned = data_preclean(frame)
    tkSeries = Series(precleaned.apply(get_parameter).values) # 得到了一个含有原始参数的序列
    # resambled_data = DataFrame(precleaned.values, columns=[tkSeries,precleaned.columns]) # 双索引的重构表
    # resambled_data.columns.names = ['tname', 'tpname'] # tname是true name, tpname是testplan name

    resambled_data2 = DataFrame(precleaned.values, columns=tkSeries) # 不要双重列名了，直接用true name作为列名
    combined_data = combine_data(resambled_data2)  # 每次tname下的两列都叠加成了一列，此时输出则是Preclean后DF，里面包含空值
    #combined_data.to_excel(r'device_exp\precleanedsites.xlsx')

    useful_sites = combined_data.apply(Series.count) # 每个tname下非NA的点的个数
    sites_precleaned = Orgin*2 - useful_sites  # 现在一列是原始的两列，得出Preclean去除的点数构成的series

    pure_data = second_dataclean(combined_data) # 第二次清洗完了的数据
    sites_2nd_cleaned = useful_sites - pure_data.loc['count'] # 第二次清洗了多少数据

    pure_data.loc['std/median'] = pure_data.loc['std']/pure_data.loc['50%']
    pure_data.loc['pre_cleaned'] = sites_precleaned
    pure_data.loc['2nd_cleaned'] = sites_2nd_cleaned

    pure_data.loc['width'] = pure_data.apply(Get_Width).apply(replace_size)
    pure_data.loc['length'] = pure_data.apply(Get_Length).apply(replace_size)

    pure_data.T.to_excel(r'device_exp\cleaneddata#6.xlsx')  # 输出路径
