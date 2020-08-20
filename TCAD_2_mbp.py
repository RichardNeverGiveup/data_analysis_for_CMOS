import os
import re
import pandas as pd
from pandas import DataFrame, Series


def write_to_mbp(file, destination):
    
    testdata = pd.read_csv(file, header=None)
    mbp = Series([])
    regex = re.compile(r'(ID.*).csv$')

    testfilename = regex.search(file).group()  # 'IDVDVB-2.2V.csv'
    testcond = testfilename[6:][:-5]    # '-2.2'


    if testfilename[:6] == "IDVDVB":
        test_type = "Ids_Vgs_Vbs"
        test_voltage = "Vbs=" + testcond
    else:
        test_type = "Ids_Vds_Vgs"
        test_voltage = "Vds=" + testcond    


    for i in range(0, len(testdata.columns), 2):

        title = testdata[i][0]
        start = title.find('=') + 1
        curve = title[start:][:-3]

        x = testdata[i] + "   "
        y = testdata[i + 1]
        result = x + y
        result[0] = "curve{" + curve + "}"
        mbp = mbp.append(result, ignore_index=True)



    with open(destination, mode="a") as f:
        header = "page(name=" + test_type + ",group=LVN in LVPW,x=Vgs,p=Vbs,y=Ids,ref_s=0){" + test_voltage + ",W=0.4,L=0.6,NF=1,m=1,SA=2.1E-7,SB=2.1E-7,T=25.0}"
        f.write(header)
        f.write("\n")

        for i in mbp.values:
            f.write(i)
            f.write("\n")
            
def main():
    regex = re.compile(r'(ID.*).csv$')
    destination = input("请输入TCAD数据转换后存入到的文件名，如newbmp.txt：")
    with open(destination, mode="a") as f:
        f.write("condition{date=2020-05-18,type=NMOS,ports=(d,g,s,b)}")
        f.write("\n")
        f.write("#pins=1,2,3,4")
        f.write("\n")
        f.write("#lot=,wafer=,tile=LUS,process=LVN in LVPW,other=,die=(0,0)")
        f.write("\n")

      
    for file in os.listdir():
        if regex.search(file):
            write_to_mbp(file, destination)

if __name__ == "__main__":
    main()
