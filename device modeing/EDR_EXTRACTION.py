import pandas as pd
from pandas import DataFrame, Series

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
corner_sequences = []
for i in items:
    corner = i.strip().split('_')[-1]
    size = i.strip().split('_')[0] + '/' + i.strip().split('_')[1]
    size_sequences.append(size)
    corner_sequences.append(corner)
###################################################################################
##################build the df#####################################################
final = DataFrame(row,columns=columns,index=[size_sequences,corner_sequences]).sort_index(level=0)
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
icc_pivot = standard_pivot.loc[cc_li[0:4]].reindex(columns=['SS','SF','SSG','SFG','TT','FSG','FFG','FS','FF'])
igm_pivot = standard_pivot.loc[gm_li[0:4]].reindex(columns=['SS','SF','SSG','SFG','TT','FSG','FFG','FS','FF'])
vcc_pivot = standard_pivot.loc[cc_li[4:]].reindex(columns=['FF','FS','FFG','FSG','TT','SFG','SSG','SF','SS'])
vgm_pivot = standard_pivot.loc[gm_li[4:]].reindex(columns=['FF','FS','FFG','FSG','TT','SFG','SSG','SF','SS'])
#######################################################################################################
flag = input("Please input the mode you want, eg: input 'cc' or 'gm' \n")

if flag == 'cc':
    with pd.ExcelWriter('CC_result.xlsx') as writer:  
        icc_pivot.to_excel(writer, sheet_name="Current-Related")
        vcc_pivot.to_excel(writer, sheet_name="Vcc-Related")
if flag == 'gm':
    with pd.ExcelWriter('GM_result.xlsx') as writer:  
        icc_pivot.to_excel(writer, sheet_name="Current-Related")
        vcc_pivot.to_excel(writer, sheet_name="Vgm-Related")

#######################################################################################################
