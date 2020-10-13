#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from pandas import DataFrame, Series


# In[104]:


with open("EDR_result.txt") as f:
    list = f.readlines()
newlist = []
for i in list:
    newlist.append(i.strip().strip(','))

    
sizelistW = []
sizelistL = []
cornerlist = []
temperaturelist = []
valuelist = []
for i in range(0, len(newlist), 2):    
    templi = newlist[i].split('_')
#     size = templi[0] + '_' + templi[1]
    sizeW = templi[0]
    sizeL = templi[1]
    corner = templi[2]
    temperature = templi[3]
#     sizelist.append(size)
    sizelistW.append(sizeW)
    sizelistL.append(sizeL)
    cornerlist.append(corner)
    temperaturelist.append(temperature)
    
for i in range(1, len(newlist), 2):
    value = newlist[i].split('=')[1]
    valuelist.append(value)

    
df = DataFrame(valuelist,columns=["Ioff"],index=[temperaturelist,sizelistW,sizelistL,cornerlist])
df.index.names = ['temp','sizeW','sizeL','corner']


if np.float(df['Ioff'][0]) > 0: # if Ioff > 0, this data is nmos
    order_of_i = ['SS', 'SF', 'SSG', 'SFG', 'TT', 'FSG', 'FFG', 'FS', 'FF']
if np.float(df['Ioff'][0]) < 0:
    order_of_i = ['SS', 'FS', 'SSG', 'FSG', 'TT', 'SFG', 'FFG', 'SF', 'FF']
# df.unstack('corner')

final = df.unstack('corner').sort_values(by=['temp', 'sizeW', 'sizeL'], ascending=False)
final.columns = final.columns.levels[1]
output = final.reindex(columns = order_of_i)
with pd.ExcelWriter('Ioff_result.xlsx') as writer:  
    output.to_excel(writer, sheet_name="Ioff")

