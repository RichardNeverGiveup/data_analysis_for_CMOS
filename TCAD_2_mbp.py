import os
import re
import pandas as pd
from pandas import DataFrame, Series


def write_to_mbp(file):
    
    # testdata = pd.read_csv('10XD24IDVDVB0V.csv', header=None)
    testdata = pd.read_csv(file, header=None)
    mbp = Series([])

    regex = re.compile(r'(ID.*).csv$')
    # testfilename = regex.search('10XD24IDVDVB0V.csv').group()  # 'IDVDVB-2.2V.csv'
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



    with open("newmbp.txt", mode="a") as f:
        header = "page(name=" + test_type + ",group=LVN in LVPW,x=Vgs,p=Vbs,y=Ids,ref_s=0){" + test_voltage + ",W=0.4,L=0.6,NF=1,m=1,SA=2.1E-7,SB=2.1E-7,T=25.0}"
        f.write(header)
        f.write("\n")

        for i in mbp.values:
            f.write(i)
            f.write("\n")
            
            
def main():
    regex = re.compile(r'(ID.*).csv$')

    for file in os.listdir():
        if regex.search(file):
            write_to_mbp(file)

if __name__ == "__main__":
    main()
