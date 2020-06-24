import shutil, os, re
import pandas as pd
import numpy as np
from pandas import DataFrame, Series
from pathlib import Path

def rename_data(workingdir):
    '''给一批机床测试数据按坐标重新命名的函数'''
#     C:\Users\E905825\notebook\JP\A02E461#19输入是字符串，而且要加r“”.
    cordinatepattern = re.compile(r'_\s(-?\d)\s(-?\d)')  # 从源文件找坐标的正则,xy坐标都可以是正负值
    workingdir = os.path.abspath(workingdir)
    p = Path(workingdir)
    for filename in os.listdir(p):
        if filename.endswith('.csv'):
            cordinate = cordinatepattern.findall(filename)
#             print(cordinate)
            x, y = cordinate[0]  # 获取坐标, 这里的x和y是字符串类型
            cord_filename = x + '_' + y + '.csv'  # 导出源文件数据表的文件名
            orin = p/filename
            dest = p/cord_filename
            shutil.move(orin, dest)            

def get_testcond(workingdir):
    '''拿到测试数据的步长，四端电压，不同测试的名称用来命名export里面的sheetname'''
    
    def regex_for_step(element):
        '''提取出步长的正则函数'''
        pat = re.compile(r'=(-?\d*\.?\d*)')
        return int(float(pat.findall(element)[0])*1000)
    
    
    workingdir = os.path.abspath(workingdir)
    p = Path(workingdir)
    for file in os.listdir(p):
        if file.endswith('.csv'):
            file_path = p/file
            raw = pd.read_csv(file_path, names=list('abcdefghijklmnopqrstuvwxyz'))
            test_cond = raw[raw['b'] == ' Analysis.Setup.Vector.Graph.Notes'][['d','g','h','i','m','o','q','s','u','w']]
            test_cond_pure = test_cond.iloc[1:-1]
            testnames = list(raw[raw['b'] == ' Analysis.Setup.Title']['c'][1:-1])
        break
            
    step_df = test_cond_pure[['g', 'h', 'i']].applymap(regex_for_step)
    step_df['i'] = step_df['i']/1000
    step_list = list(((step_df['h'] - step_df['g'])/step_df['i'] + 1).apply(int))    
    
#     test_desc = pd.concat([test_cond_pure, testnames])
    
    return step_list, test_cond_pure, testnames                        


def get_data(raw, testname, site):
#     传入testnam和行数site
    start = (raw['c'] == testname).idxmax()
    end = start + 3 + site
    temp = DataFrame(raw.iloc[start:end+1].drop('a', axis=1).values)[3:].iloc[:,:8]
    final = DataFrame(temp.values, columns=temp.values[0]).drop(0)
    return final

def concate_data(workingdir):
    '''把不同die上面的数据收集组合集中成一个大表'''
    workingdir = os.path.abspath(workingdir)
    step_list, test_cond_pure, testnames = get_testcond(workingdir)    
#     get the test condition and step    
    
    p = Path(workingdir)
#     export = r'p/export.xlsx'
    export_path = os.path.join(p, 'export.xlsx') # 合并路径和文件名
    
    columns = [' Vs', ' Vd', ' Vg', ' Vb', ' Id', ' Ig', ' Is', ' Ib']
    dummyVd29 = DataFrame([['dummy']*8],columns=columns, index=['cordinate']) # 这里要改成根据测试条目名字自动生成dummy个数
    dummyVd12 = DataFrame([['dummy']*8],columns=columns, index=['cordinate'])
    dummyVd5 = DataFrame([['dummy']*8],columns=columns, index=['cordinate'])
    dummyVd01 = DataFrame([['dummy']*8],columns=columns, index=['cordinate'])    
    
    for file in os.listdir(p):
        if file.endswith('.csv'):
            file_path = p/file
            raw = pd.read_csv(file_path, names=list('abcdefghijklmnopqrstuvwxyz'))
                        
            Vd29 = get_data(raw,testnames[0],step_list[0])   # 这里也应该要自动循环
            Vd12 = get_data(raw,testnames[1],step_list[1])  
            Vd5 = get_data(raw,testnames[2],step_list[2])
            Vd01 = get_data(raw,testnames[3],step_list[3])
            cordinate = file[:-4]
            cord_df = DataFrame([[cordinate]*8],columns=columns, index=['cordinate'])
            Vd29 = pd.concat([cord_df, Vd29], axis=0, sort=False)
            Vd12 = pd.concat([cord_df, Vd12], axis=0, sort=False)
            Vd5 = pd.concat([cord_df, Vd5], axis=0, sort=False)
            Vd01 = pd.concat([cord_df, Vd01], axis=0, sort=False)
            
            dummyVd29 = pd.concat([dummyVd29,Vd29])
            dummyVd12 = pd.concat([dummyVd12,Vd12])
            dummyVd5 = pd.concat([dummyVd5,Vd5])
            dummyVd01 = pd.concat([dummyVd01,Vd01])            

    with pd.ExcelWriter(export_path) as writer:  
        dummyVd29.to_excel(writer, sheet_name=testnames[0])
        dummyVd12.to_excel(writer, sheet_name=testnames[1])  # 要改写成自动循环写入
        dummyVd5.to_excel(writer, sheet_name=testnames[2])
        dummyVd01.to_excel(writer, sheet_name=testnames[3])
        test_cond_pure.to_excel(writer, sheet_name='test_description')

if __name__ == '__main__':                  
    rename_data(r"C:\Users\E905825\notebook\JP\A02E461#21")
    concate_data(r"C:\Users\E905825\notebook\JP\A02E461#21")
