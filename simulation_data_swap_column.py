import pandas as pd
import numpy as np
from pandas import DataFrame


filename = input("输入要被转格式的文件名，如EDR_result_hspice")

table = pd.read_csv(filename,sep='\s+', header=None)

# table = pd.read_csv("EDR_result_hspice",sep='\s+', header=None)
for a in range(len(table[0])):
    if table[0][a][0] == "i":
        cutline = a 
        break
        
table1 = table[:cutline]
table2 = table[cutline:]
reindexed1 = table1.reindex(columns=[0,2,4,6,8,1,9,7,5,3])
reindexed2 = table2.reindex(columns=[0,3,5,7,9,1,8,6,4,2])
df1 = DataFrame(reindexed1.values)
df2 = DataFrame(reindexed2.values)
final = pd.concat([df1, df2])
final.to_excel("transformed_output.xlsx")
