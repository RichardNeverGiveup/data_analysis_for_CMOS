import pandas as pd
from pandas import DataFrame, Series
import numpy as np

##################get the data and devicesize+corner#####################
items = []
datas = []
with open("EDR_result.txt") as f:
    list = f.readlines()
for i in range(0,len(list),2):
    items.append(list[i])
for i in range(1,len(list)+1,2):
    datas.append(list[i])
##########################################################################
################use params like Vtbcc as column names#####################  
columns = []
for i in datas[0].split(',')[:-1]:
    params = i.split('=')[0]
    columns.append(params)
columns
#########################################################################
##########build a list of lists contained all the values##################
row = []  # row is the data for each size and corner
for i in datas:
    col = []  # col is the different params
    for ev in i.split(',')[:-1]:
        value = ev.split('=')[1]
        col.append(value)
    row.append(col)
#########################################################################
############bulit the two lists for the df as hierarchical index##############
size_sequences = []
width_sequences = []
length_sequences = []
corner_sequences = []
for i in items:
    corner = i.strip().split('_')[-1]
    width = i.strip().split('_')[0]
    length = i.strip().split('_')[1]
    size = i.strip().split('_')[0] + '/' + i.strip().split('_')[1]
    size_sequences.append(size)
    corner_sequences.append(corner)
    width_sequences.append(width)
    length_sequences.append(length)
###################################################################################
##################build the df#####################################################
final = DataFrame(row,columns=columns,index=[size_sequences,corner_sequences]).sort_index(level=0)
# final = DataFrame(row,columns=columns,index=[size_sequences,corner_sequences])
# final['width'] = width_sequences
# final['length'] = length_sequences
# final.sort_index(level=0)

final.index.names = ['size','corner']
final.columns.names = ['params']
###################################################################################
###############bulid and sort the params list for gm and cc###################################
vtbcc_li = []
vtbgm_li = []
for i in final.columns:
    if i.startswith('vtbcc'):
        vtbcc_li.append(i)
    elif i.startswith('vtbgm'):
        vtbgm_li.append(i)

gm_li = ['cgg', 'vtlgm', 'idlin','vtsgm', 'idsat', 'ioff'] + vtbgm_li
cc_li = ['cgg', 'vtlcc', 'idlin','vtscc', 'idsat', 'ioff'] + vtbcc_li
gm_li.sort()
cc_li.sort()  # out put is ['cgg','idlin','idsat','ioff','vtbcc50', ...,'vtbcc55','vtbcc56','vtlcc','vtscc']
#######################################################################################################
########################get a standard form pivot####################################################
# reindex(columns=['FF','FS','FFG','FSG','TT','SFG','SSG','SF','SS']) for v
# reindex(columns=['SS','SF','SSG','SFG','TT','FSG','FFG','FS','FF']) for i
standard_pivot = final.unstack().stack(0).swaplevel(0,1).sort_index(level=0)
#######################################################################################################
if np.float(standard_pivot.loc['idsat']['TT'][0]) > 0: # 随便取了第一个TT的IDSAT判断正负，负的就是pmos
    order_of_i = ['SS', 'FS', 'SSG', 'FSG', 'TT', 'SFG', 'FFG', 'SF', 'FF']
    order_of_v = ['FF', 'SF', 'FFG', 'SFG', 'TT', 'FSG', 'SSG', 'FS', 'SS']
if np.float(standard_pivot.loc['idsat']['TT'][0]) < 0: # 随便取了第一个TT的IDSAT判断正负，负的就是pmos
    order_of_i = ['SS', 'SF', 'SSG', 'SFG', 'TT', 'FSG', 'FFG', 'FS', 'FF']
    order_of_v = ['FF', 'FS', 'FFG', 'FSG', 'TT', 'SFG', 'SSG', 'SF', 'SS']


icc_pivot = standard_pivot.loc[cc_li[0:4]].reindex(columns=order_of_i)
igm_pivot = standard_pivot.loc[gm_li[0:4]].reindex(columns=order_of_i)
vcc_pivot = standard_pivot.loc[cc_li[4:]].reindex(columns=order_of_v)
vgm_pivot = standard_pivot.loc[gm_li[4:]].reindex(columns=order_of_v)
###############################################################################################################
##################################get the order of W & L you want #############################################################################
df_icc = DataFrame(icc_pivot.reset_index()['size'].apply(str.split,args=('/')).tolist(), columns=['width', 'length'], dtype=np.float)
icc_pivot = icc_pivot.reset_index().join(df_icc).set_index(['params', 'size']).sort_values(by=['params','width', 'length'], ascending=False)

df_igm = DataFrame(igm_pivot.reset_index()['size'].apply(str.split,args=('/')).tolist(), columns=['width', 'length'], dtype=np.float)
igm_pivot = igm_pivot.reset_index().join(df_igm).set_index(['params', 'size']).sort_values(by=['params','width', 'length'], ascending=False)

df_vcc = DataFrame(vcc_pivot.reset_index()['size'].apply(str.split,args=('/')).tolist(), columns=['width', 'length'], dtype=np.float)
vcc_pivot = vcc_pivot.reset_index().join(df_vcc).set_index(['params', 'size']).sort_values(by=['params','width', 'length'], ascending=False)

df_vgm = DataFrame(vgm_pivot.reset_index()['size'].apply(str.split,args=('/')).tolist(), columns=['width', 'length'], dtype=np.float)
vgm_pivot = vgm_pivot.reset_index().join(df_vgm).set_index(['params', 'size']).sort_values(by=['params','width', 'length'], ascending=False)

##########################################################################################################
flag = input("Please input the mode you want, eg: input 'cc' or 'gm' \n")

if flag == 'cc':
    with pd.ExcelWriter('CC_result.xlsx') as writer:  
        icc_pivot.to_excel(writer, sheet_name="Current-Related")
        vcc_pivot.to_excel(writer, sheet_name="Vcc-Related")
if flag == 'gm':
    with pd.ExcelWriter('GM_result.xlsx') as writer:  
        igm_pivot.to_excel(writer, sheet_name="Current-Related")
        vgm_pivot.to_excel(writer, sheet_name="Vgm-Related")

#######################################################################################################
