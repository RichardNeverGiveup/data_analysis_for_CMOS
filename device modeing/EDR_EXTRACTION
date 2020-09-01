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
DataFrame(row,columns=columns,index=[size_sequences,corner_sequences]).sort_index(level=0)
###################################################################################
