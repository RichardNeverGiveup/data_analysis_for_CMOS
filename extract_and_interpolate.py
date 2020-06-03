import shutil, os, re
import pandas as pd
import numpy as np
from pandas import DataFrame, Series

def getdata1(rawdata):
    '''提取Id vs. Vg@Vd=5V的测试数据，此数据暂不需要插值'''
    start = (rawdata['c'] == ' Id vs. Vg@Vd=5V').idxmax()
    end = (rawdata['b'] == ' Initial Id vs. Vg@Vd=0.1V').idxmax()

    # rawdata.iloc[start:end]
    selected = rawdata.iloc[start:end]
    selected1 = selected.drop('a',axis=1)
    selected2 = DataFrame(selected1.values)
    selected3 = selected2[3:selected2.shape[0]]
    selected4 = selected3.iloc[:,:8]
    selected5 = DataFrame(selected4.values)
    final = DataFrame(selected5.values, columns=selected5.iloc[0]).drop(0)
    return final
    #final # 此时已经在杂乱的表里找到了数据，可以直接输出，也可以分析了再输出
    
def getdata2(rawdata):
    '''提取Initial Id vs. Vg@Vd=0.1V的测试数据'''
    start = (rawdata['c'] == ' Initial Id vs. Vg@Vd=0.1V').idxmax()
    end = start + 185

    # rawdata.iloc[start:end]
    selected = rawdata.iloc[start:end]
    selected1 = selected.drop('a',axis=1)
    selected2 = DataFrame(selected1.values)
    selected3 = selected2[3:selected2.shape[0]]
    selected4 = selected3.iloc[:,:8]
    selected5 = DataFrame(selected4.values)
    final = DataFrame(selected5.values, columns=selected5.iloc[0]).drop(0) 
    return final
    #final # 此时已经在杂乱的表里找到了数据，可以直接输出，也可以分析了再输出
    
def getdata3(rawdata):
    '''提取Id vs. Vs@Vd=29V的测试数据'''
    start = (rawdata['c'] == ' Id vs. Vs@Vd=29V').idxmax()  # mark是' Id vs. Vs@Vd=29V'
    end = (rawdata['b'] == ' Id vs. Vs@Vd=29V').idxmax()
    # rawdata.iloc[start:end]
    selected = rawdata.iloc[start:end]
    selected1 = selected.drop('a',axis=1)
    selected2 = DataFrame(selected1.values)
    selected3 = selected2[3:selected2.shape[0]]
    selected4 = selected3.iloc[:,:8]
    selected5 = DataFrame(selected4.values)
    final = DataFrame(selected5.values, columns=selected5.iloc[0]).drop(0) 
    #final # 此时已经在杂乱的表里找到了数据，可以直接输出，也可以分析了再输出
    return final

def log_interpolation(final):
    '''对一个表进行插值分析,输入的final应该是一个Dataframe'''
    Is = final[' Is'].astype(np.float).abs() # 把I和V从字符转成浮点数,I取绝对值
    Vs = final[' Vs'].astype(np.float)
    Is_needed = Is[Is.abs() > 1e-12] # 把Is列中Is大于1e-12的提取
    Is_needed_for_K = Is_needed[:2]  # 拿出前两个点求斜率
    a, b = Is_needed_for_K.index[0], Is_needed_for_K.index[1] # a, b是满足要求的首两个点的行索引

    Is_needed_log = np.log10(Is_needed_for_K)  # 对拿出来的两个点取LOG
    deltaV = Vs[a] - Vs[b]
    deltaI = Is_needed_log[a] - Is_needed_log[b]
    slope = deltaV / deltaI
    Vs_target = Vs[a] + (np.log10(1e-12) - np.log10(Is[a]))*slope  # Vs at Is=1e-12
    return Vs_target

def linear_interpolation(final):
    '''电流常规外推插值'''
    Id = final[' Id'].astype(np.float)
    Vg = final[' Vg'].astype(np.float)
    Id_needed = Id[Id > 1e-8][Id < 1e-6]
    '''等价于
    Id_needed = Id[Id > 1e-8]
    Id_needed = Id_needed[Id_needed < 1e-6]
    Id_needed
    '''
    '''
    ideal = (Id_needed - 1e-7).abs().idxmin() # 找出距离1e-7最近的点索引
    a = Id_needed.index[0]
    b = ideal
    deltaV = Vg[b] - Vg[a]
    deltaI = Id_needed[b] - Id_needed[a]
    slope = deltaV / deltaI
    Vg_target = Vg[a] + ((1e-7)-Id[a])*slope
    Vg_target
    '''
    '''
    a = Id_needed.index[0]
    b = Id_needed.index[-1]
    deltaV = Vg[b] - Vg[a]
    deltaI = Id_needed[b] - Id_needed[a]
    slope = deltaV / deltaI
    Vg_target = Vg[a] + ((1e-7)-Id[a])*slope
    Vg_target
    '''
    ideal = (Id_needed - 1e-7).abs().idxmin() # 找出距离1e-7最近的点索引
    b = ideal
    a = b - 1
    deltaV = Vg[b] - Vg[a]
    deltaI = Id_needed[b] - Id_needed[a]
    slope = deltaV / deltaI
    Vg_target = Vg[a] + ((1e-7)-Id[a])*slope
    Vg_target
    return Vg_target

if __name__ == '__main__':
    
    workingDir = os.path.abspath(r'JP\A9A5202#03') # 读取的目录
    exportDir = os.path.abspath(r'JP\exported')    # 导出的目录
    cordinatepattern = re.compile(r'_\s(\d)\s(-?\d)')  # 从源文件找坐标的正则


    exportfilename = 'interpolate.xlsx'     # 插值文件名
    exportpath = os.path.join(exportDir, exportfilename)  # 插值文件的路径，给pd输出

    result = {}
    for filename in os.listdir(workingDir):
        if filename.endswith('.csv'):
            cordinate = cordinatepattern.findall(filename)
            x, y = cordinate[0]  # 获取坐标, 这里的x和y是字符串类型
            originfilename = x + '_' + y + '.xlsx'  # 导出源文件数据表的文件名

            filepath = os.path.join(workingDir, filename)  # 文件的路径，给pd用来读入
            originfile_exportpath = os.path.join(exportDir, originfilename)  # 文件的路径，给pd输出

            rawdata = pd.read_csv(filepath, names=list('abcdefghijklmnopqrstuvwxyz')) # 读入数据

            data1 = getdata1(rawdata)  # 提取Id vs. Vg@Vd=5V的测试数据，此数据暂不需要插值
            data2 = getdata2(rawdata)  # 提取Initial Id vs. Vg@Vd=0.1V的测试数据
            data3 = getdata3(rawdata)  # 提取Id vs. Vs@Vd=29V的测试数据,用log()
            #data1.to_excel(originfile_exportpath, sheet_name='Sheet1')
            with pd.ExcelWriter(originfile_exportpath) as writer:  # doctest: +SKIP
                data1.to_excel(writer, sheet_name='Id vs. Vg@Vd=5V')
                data2.to_excel(writer, sheet_name='Initial Id vs. Vg@Vd=0.1V')
                data3.to_excel(writer, sheet_name='Id vs. Vs@Vd=29V')

            Vg_target = linear_interpolation(data2) # 插值得到Vg
            Vs_target = log_interpolation(data3)    # 插值得到Vs
            key = x+'_'+y
            li = [Vg_target, Vs_target]
            result[key] = li
            
    df = DataFrame(result, columns=result.keys(), index=['Vg_target', 'Vs_target']).T
    df.to_excel(exportpath)     # 导出插值结果


    
    
    
    
    
