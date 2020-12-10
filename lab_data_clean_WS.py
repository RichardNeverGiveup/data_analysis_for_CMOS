#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from pandas import DataFrame, Series
import os


# In[6]:


#############################################################################################################
# 只用配置这个文件的path就好了
originalfilepath = "A9B7790_D361_INT_1.txt"
#############################################################################################################

raw = open(originalfilepath).readlines()

clist = []
waferids = []
for count, line in enumerate(raw):
    if "SYS_WAFERID" in line:
        key = line.split("\t")[0] + line.split("\t")[1].strip()
        #print(key)
        clist.append(count)
        waferids.append(key)

# print(raw[clist[0]+1])
column_indicator = raw[clist[0]+1]
column_number = eval(column_indicator.strip().split("x")[1])

start_end_li = []
for i in range(len(clist)):
    if i <= len(clist)-2:
        start = clist[i] + 2
        end = clist[i+1] - 1
    else:
        start = clist[i] + 2
        end = None
#     print(start, end)    
    start_end_li.append((start,end)) 

stack_li = []
for i in start_end_li:
    if i[1] == None:
        stack = raw[i[0]:]
    else:
        stack = raw[i[0]:i[1]]
    stack_li.append(stack)

waferdatadict = {}
for i in range(len(waferids)):
    waferdatadict[waferids[i]] = stack_li[i]

objectfilename_list = []  # 记录了目标文件名的列表
for k in waferdatadict:
    txt_name = k + ".txt"
    f = open(txt_name, "w")
    for i in waferdatadict[k]:    
        f.write(i)
    f.close()
    objectfilename_list.append(txt_name)
###################输出各个wafer的txt完毕###########################################################################################

def getstats(filepath, column_number, wafer_NO):
    w = pd.read_csv(filepath,sep='\t',index_col=0,names=list(range(column_number))).drop(columns=[1,2,3])
    w.columns = Series(w.shape[-1]*[wafer_NO])
    w_median = w.apply(np.median, axis=1)
    w_std = w.apply(np.std, axis=1)
    w_max = w.apply(np.max, axis=1)
    w_min= w.apply(np.min, axis=1)
    stats = pd.concat([w_median,w_max,w_min,w_std],axis=1)
    s_wafer_NO = str(wafer_NO)
    stats.columns = [s_wafer_NO+ '_'+ 'median',s_wafer_NO + '_'+ 'max',s_wafer_NO+ '_'+ 'min',s_wafer_NO+ '_'+ 'std']
    return stats, w

wafer_stat_li = []
wafer_raw_li = []
for name in objectfilename_list:
    wafer_NO = name.split(".")[0].replace("SYS_WAFERID","")
    print(wafer_NO)
#     wafer_NO = name.split(".")[0][-1]
    wafersummary = getstats(name, column_number, wafer_NO)
    
    wafer_stat = wafersummary[0]
    wafer_raw = wafersummary[1]
    
    wafer_stat_li.append(wafer_stat)
    wafer_raw_li.append(wafer_raw)

stat_total = pd.concat(wafer_stat_li,axis=1)
raw_total = pd.concat(wafer_raw_li,axis=1)
test = pd.concat([stat_total,raw_total],axis=1)

def get_index_num(s):
    return s.split('_')[0]

def get_index_title(s):
    return '_'.join(s.split('_')[1:])

index1 = Series(test.index).apply(get_index_num)
index2 = Series(test.index).apply(get_index_title)
test.index = [index1,index2]
test.index.names = ["NO","wafer_NO"]

dest_file = originalfilepath.split(".")[0] + ".xlsx"
print(dest_file)

with pd.ExcelWriter(dest_file) as writer:  
    test.to_excel(writer, sheet_name="test")

#dest_file_new = originalfilepath.split(".")[0] + ".csv"
#test.to_csv(dest_file_new)

for f in objectfilename_list:
    os.remove(f)

input("输入任意键继续！")

