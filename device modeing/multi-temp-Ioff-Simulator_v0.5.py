#!/usr/bin/env python
# -*- coding:utf-8 -*-


import os
ls = os.linesep


#******************input information******************#
corner_TT = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_FF = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" fast_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_SS = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" slow_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_FS = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" fnsp_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_SF = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" snfp_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_FFG = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" fast_g_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_SSG = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" slow_g_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_FSG = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" fnsp_g_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""
corner_SFG = """
.lib "./WYS_V0.5_20200731/lib/cs501_lib" presim
.lib "./WYS_V0.5_20200731/lib/cs501_lib" snfp_g_llv
.lib "./WYS_V0.5_20200731/lib/cs501_lib" typ_diode
"""


corner = [corner_TT,corner_FF,corner_SS,corner_FS,corner_SF,corner_FFG,corner_SSG,corner_FSG,corner_SFG] #add the corner above
cornerName = ["TT","FF","SS","FS","SF","FFG","SSG","FSG","SFG"] #Arbitrary name but should match above corner


# T = 25
temp_li = [25, 90, 100]  # 尝试支持多个温度下的IOFF
Vs = "-1"  # support Vs configure

modelType = "S" # "S" or "C"
MN = "lvnemos4_1p2_lvpw"
CMP = ".m1" #core model path of subckt model
polarity= "N"
nodeNO = 4 # only for subckt model
icon = 4e-8 # no sign
Vdcon = 0.05 # no sign
vdd = 1.2
vgg = 1.2
vbb = -1.2
vdoff = 1.32
vcgg = -1.2
cgg_size = "10/10/1" # "w(um)/l(um)/m"
device_size = ["10/10/0.23","10/0.08/0.23","1/0.08/0.23","0.6/0.08/0.23","0.4/0.08/0.23","0.3/0.08/0.23"] # "w(um)/l(um)/sa(um)"
#device_size = ["10/10/0.23"] # "w(um)/l(um)/sa(um)"

#******************input information end******************#

addNode = (nodeNO - 4) * ' 0'
# cornerNO = len(corner)

#******************netlist component******************#
title = "$ hspice netlist for EDR simulation"
options = ".options probe brief=1 nomod post ingold=2 dccap=1 numdgt=5 list"
# temp = ".temp %d"%T
end = os.linesep + ".end" + os.linesep
#******************netlist component end******************#

#******************spec function for compact model******************#
def specIoffC(NO,mdl,mType,vdoff,size):
    if mType == 'N':
        #mS = 1
        step = 0.01
    elif mType == 'P':
        #mS = -1
        step = -0.01
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specIoffCNet = """

m%s06 d%02d06 0 %s 0 %s w=%su l=%su %s
Vd%02d06 d%02d06 0 %s
.dc Vd%02d06 0 %s %s
.meas dc ioff_%s find I(m%s06) when V(d%02d06,0)=%s
"""%(mdl,NO, Vs, mdl,w,l,lodSize,NO,NO,vdoff,NO,vdoff,step,mdl,mdl,NO,vdoff)
    return specIoffCNet
#******************spec function for compact model end******************#



#******************spec function for subckt model******************#
def specIoffS(NO,mdl,mType,vdoff,size):
    if mType == 'N':
        #mS = 1
        step = 0.01
    elif mType == 'P':
        #mS = -1
        step = -0.01
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specIoffSNet = """

x%s06 d%02d06 0 %s 0%s %s w=%su l=%su %s
Vd%02d06 d%02d06 0 %s
.dc Vd%02d06 0 %s %s
.meas dc ioff_%s find I(x%s06%s) when V(d%02d06,0)=%s
"""%(mdl,NO,Vs,addNode,mdl,w,l,lodSize,NO,NO,vdoff,NO,vdoff,step,mdl,mdl,CMP,NO,vdoff)
    return specIoffSNet
#******************spec function for subckt model end******************#

def main():
    specList = ["ioff_"+MN]

    for i in device_size:
        if modelType == "S":
            ioffNetlist = specIoffS(1,MN,polarity,vdoff,i)

        elif modelType == "C":
            ioffNetlist = specIoffC(1,MN,polarity,vdoff,i)

        netlist2 = ioffNetlist    

        corner_index = 0
        for j in corner:
            for t in temp_li:
                temp = ".temp %d"%t

                netlist1 = title + ls*2 + options + ls + j + ls + temp + ls*2   #这里的j对应着每一个corner
                netlist = netlist1 + netlist2 + end
                cornertitle = cornerName[corner_index]  # 这会给我们一个“TT”, "SS"之类的字符串
                # i is the device size, like "10/10/0.23", so i.replace('/','_') can get "10_10_0.23"
                size_for_filename = i.replace('/','_')
                netlistFile = "EDR_hspice_%s_%s_%sC.sp"%(size_for_filename,cornertitle,t)  #this will generate a series of netlist
                with open(netlistFile, 'w') as file:
                    file.write(netlist)

                listFile = "EDR_%s_%s_%sC.lis"%(size_for_filename,cornertitle,t)
                cmd = "hspice " + netlistFile + " > " + listFile
                os.system(cmd)

            corner_index += 1
    delFile = "rm *.ms* *.sw* *.st* *.pa*"
    os.system(delFile)

    DICT = {}
    for file in os.listdir('.'):
        if file.endswith('.lis'):
            size = '_'.join(file.split('_')[1:3])
            temperature = file.split('_')[-1][0:-4]
            corner_na = file.split('_')[-2]
            KEY = size + '_' + corner_na + '_' + temperature
            
            LIST = []
            with open(file) as f:
        
                for eachline in f:
                    for eachspec in specList:
                        if eachspec + '=' in eachline:
                            if 'at=' in eachline:
                                value = eachline.split('at=')[0].split('=')[1].strip()
                            else:
                                value = eachline.split('=')[1].strip()
                        
                            VALUE = eachspec.split('_')[0] + '='+ value
                            LIST.append(VALUE)
            DICT[KEY] = LIST
    with open('EDR_result.txt', 'w') as f:
        for k in DICT:
            f.write(k)
            f.write(ls)
            for i in DICT[k]:
                f.write(i)
                f.write(',')
            f.write(ls)


if __name__ == "__main__":
    main()




