#!/usr/bin/env python
# -*- coding:utf-8 -*-
#*************************************************#
#              EDR VALIDATION(HSPICE)             #
#                                                 #
#    Author: Yukang Zhou                          #
#    Email: yukon_zhou@hotmail.com                #
#    Date: Jun 7, 2018                            #
#*************************************************#

#******************update history******************#
#date          version     update record
#2020/07/22    v1p0        1)add search path of subckt model's core model name in input information, like '.m0';
#                          2)reorganize EDR result file to match model vs EDR Excel file;   
#                          3)extend corner number to simulate all corners 
# 
# 
#2020/08/30     v2         1)add user input function for different vbb
#
#
#2020/09/01     v3		   1)reconstructed the final output data structure
#						   2)builid work flow with another data extraction script
#                          -------by Ruilin
#******************update history end******************#






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

T = 25
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
cornerNO = len(corner)

#******************netlist component******************#
title = "$ hspice netlist for EDR simulation"
options = ".options probe brief=1 nomod post ingold=2 dccap=1 numdgt=5 list"
temp = ".temp %d"%T
end = os.linesep + ".end" + os.linesep
#******************netlist component end******************#

#******************spec function for compact model******************#
def cggC(NO,mdl,vcgg,size_cgg):
    w = size_cgg.split('/')[0]
    l = size_cgg.split('/')[1]
    m = size_cgg.split('/')[2]
    abs_vcgg = abs(float(vcgg))
    cggCNet = """
m%s01 0 g%02d01 0 0 %s w=%su l=%su m=%s
Vg%02d01 g%02d01 0 -1
.dc Vg%02d01 poi 7 -%.2f -1 -0.5 0 0.5 1 %.2f
.meas cgg_%s find par('lx18(m%s01)+lv36(m%s01)+lv37(m%s01)+lv38(m%s01)') when V(g%02d01)=%s
"""%(mdl,NO,mdl,w,l,m,NO,NO,NO,abs_vcgg,abs_vcgg,mdl,mdl,mdl,mdl,mdl,NO,vcgg)
    return cggCNet

def specLinC(NO,mdl,mType,vgg,size):
    if mType == 'N':
        mS = 1
        Vdcon1 = Vdcon
        step = 0.01
        vtlgmExp = "max par('(lx7(m%s02)*v(g%02d02)-lx4(m%s02))/lx7(m%s02)-0.05')"%(mdl,NO,mdl,mdl)
    elif mType == 'P':
        mS = -1
        Vdcon1 = -1*Vdcon
        step = -0.01
        vtlgmExp = "min par('(lx7(m%s02)*v(g%02d02)+lx4(m%s02))/lx7(m%s02)+0.05')"%(mdl,NO,mdl,mdl)
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specLinCNet = """

m%s02 d%02d02 g%02d02 0 0 %s w=%su l=%su %s
Vd%02d02 d%02d02 0 %s
Vg%02d02 g%02d02 0 0.1
.dc Vg%02d02 0 %s %s
.meas dc vtlgm_%s %s
.meas dc vtlcc_%s find V(g%02d02) when I(Vd%02d02)=par('%s*%s*%s/%s')
.meas dc idlin_%s find I(m%s02) when V(g%02d02,0)=%s
"""%(mdl,NO,NO,mdl,w,l,lodSize,NO,NO,Vdcon1,NO,NO,NO,vgg,step,mdl,vtlgmExp,mdl,NO,NO,-1*mS,icon,w,l,mdl,mdl,NO,vgg)
    return specLinCNet

def specSatC(NO,mdl,mType,vdd,vgg,size):
    if mType == 'N':
        mS = 1; step = 0.01
    elif mType == 'P':
        mS = -1; step = -0.01
    vtsgmExp = """.probe dc SSId%02d03=deriv("sqrt(I(m%s03))")
.meas dc SSIdm%02d03 max par(SSId%02d03)
.meas dc Vgsm%02d03 find v(g%02d03,0) when deriv("sqrt(I(m%s03))")=SSIdm%02d03
.meas dc Idsm%02d03 find i(m%s03) when deriv("sqrt(I(m%s03))")=SSIdm%02d03
.meas dc SIdsm%02d03 param='sqrt(Idsm%02d03)'
.meas dc vtsgm_%s PARAM="Vgsm%02d03-SIdsm%02d03/SSIdm%02d03" """%(NO,mdl,NO,NO,NO,NO,mdl,NO,NO,mdl,mdl,NO,NO,NO,mdl,NO,NO,NO)
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specSatCNet = """

m%s03 d%02d03 g%02d03 0 0 %s w=%su l=%su %s
Vd%02d03 d%02d03 0 %s
Vg%02d03 g%02d03 0 0.1
.dc Vg%02d03 0 %s %s
%s
.meas dc vtscc_%s find V(g%02d03) when I(Vd%02d03)=par('%s*%s*%s/%s')
.meas dc idsat_%s find I(m%s03) when V(g%02d03,0)=%s
"""%(mdl,NO,NO,mdl,w,l,lodSize,NO,NO,vdd,NO,NO,NO,vgg,step,vtsgmExp,mdl,NO,NO,-1*mS,icon,w,l,mdl,mdl,NO,vgg)
    return specSatCNet

def specVtbC(NO,mdl,mType,vgg,vbb,size,sq):    # need to add several vbb and change the sequence number,sq
    if mType == 'N':
        mS = 1; Vdcon1 = Vdcon; step = 0.01
        vtlgmExp = "max par('(lx7(m%s05%s)*v(g%02d05%s)-lx4(m%s05%s))/lx7(m%s05%s)-0.05')"%(mdl,sq,NO,sq,mdl,sq,mdl,sq)
    elif mType == 'P':
        mS = -1; Vdcon1 = -1*Vdcon; step = -0.01
        vtlgmExp = "min par('(lx7(m%s05%s)*v(g%02d05%s)+lx4(m%s05%s))/lx7(m%s05%s)+0.05')"%(mdl,sq,NO,sq,mdl,sq,mdl,sq)
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specVtbCNet = """

m%s05%s d%02d05%s g%02d05%s 0 b%02d05%s %s w=%su l=%su %s
Vd%02d05%s d%02d05%s 0 %s
Vg%02d05%s g%02d05%s 0 0.1
Vb%02d05%s b%02d05%s 0 %s
.dc Vg%02d05%s 0 %s %s
.meas dc vtbgm5%s_%s %s
.meas dc vtbcc5%s_%s find V(g%02d05%s) when I(Vd%02d05%s)=par('%s*%s*%s/%s')
"""%(mdl,sq,NO,sq,NO,sq,NO,sq,mdl,w,l,lodSize,NO,sq,NO,sq,Vdcon1,NO,sq,NO,sq,NO,sq,NO,sq,vbb,NO,sq,vgg,step,sq,mdl,vtlgmExp,sq,mdl,NO,sq,NO,sq,-1*mS,icon,w,l)
    return specVtbCNet


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

m%s06 d%02d06 0 0 0 %s w=%su l=%su %s
Vd%02d06 d%02d06 0 %s
.dc Vd%02d06 0 %s %s
.meas dc ioff_%s find I(m%s06) when V(d%02d06,0)=%s
"""%(mdl,NO,mdl,w,l,lodSize,NO,NO,vdoff,NO,vdoff,step,mdl,mdl,NO,vdoff)
    return specIoffCNet
#******************spec function for compact model end******************#



#******************spec function for subckt model******************#
def cggS(NO,mdl,vcgg,size_cgg):
    w = size_cgg.split('/')[0]
    l = size_cgg.split('/')[1]
    m = size_cgg.split('/')[2]
    abs_vcgg = abs(float(vcgg))
    cggSNet = """
x%s01 0 g%02d01 0 0%s %s w=%su l=%su m=%s
Vg%02d01 g%02d01 0 -1
.dc Vg%02d01 poi 7 -%.2f -1 -0.5 0 0.5 1 %.2f
.meas cgg_%s find par('lx18(x%s01%s)+lv36(x%s01%s)+lv37(x%s01%s)+lv38(x%s01%s)') when V(g%02d01)=%s
"""%(mdl,NO,addNode,mdl,w,l,m,NO,NO,NO,abs_vcgg,abs_vcgg,mdl,mdl,CMP,mdl,CMP,mdl,CMP,mdl,CMP,NO,vcgg)
    return cggSNet

def specLinS(NO,mdl,mType,vgg,size):
    if mType == 'N':
        mS = 1
        Vdcon1 = Vdcon
        step = 0.01
        vtlgmExp = "max par('(lx7(x%s02%s)*v(g%02d02)-lx4(x%s02%s))/lx7(x%s02%s)-0.05')"%(mdl,CMP,NO,mdl,CMP,mdl,CMP)
    elif mType == 'P':
        mS = -1
        Vdcon1 = -1*Vdcon
        step = -0.01
        vtlgmExp = "min par('(lx7(x%s02%s)*v(g%02d02)+lx4(x%s02%s))/lx7(x%s02%s)+0.05')"%(mdl,CMP,NO,mdl,CMP,mdl,CMP)
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specLinSNet = """

x%s02 d%02d02 g%02d02 0 0%s %s w=%su l=%su %s
Vd%02d02 d%02d02 0 %s
Vg%02d02 g%02d02 0 0.1
.dc Vg%02d02 0 %s %s
.meas dc vtlgm_%s %s
.meas dc vtlcc_%s find V(g%02d02) when I(Vd%02d02)=par('%s*%s*%s/%s')
.meas dc idlin_%s find I(x%s02%s) when V(g%02d02,0)=%s
"""%(mdl,NO,NO,addNode,mdl,w,l,lodSize,NO,NO,Vdcon1,NO,NO,NO,vgg,step,mdl,vtlgmExp,mdl,NO,NO,-1*mS,icon,w,l,mdl,mdl,CMP,NO,vgg)
    return specLinSNet

def specSatS(NO,mdl,mType,vdd,vgg,size):
    if mType == 'N':
        mS = 1; step = 0.01
    elif mType == 'P':
        mS = -1; step = -0.01
    vtsgmExp = """.probe dc SSId%02d03=deriv("sqrt(I(x%s03%s))")
.meas dc SSIdm%02d03 max par(SSId%02d03)
.meas dc Vgsm%02d03 find v(g%02d03,0) when deriv("sqrt(I(x%s03%s))")=SSIdm%02d03
.meas dc Idsm%02d03 find i(x%s03%s) when deriv("sqrt(I(x%s03%s))")=SSIdm%02d03
.meas dc SIdsm%02d03 param='sqrt(Idsm%02d03)'
.meas dc vtsgm_%s PARAM="Vgsm%02d03-SIdsm%02d03/SSIdm%02d03" """%(NO,mdl,CMP,NO,NO,NO,NO,mdl,CMP,NO,NO,mdl,CMP,mdl,CMP,NO,NO,NO,mdl,NO,NO,NO)
    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specSatSNet = """

x%s03 d%02d03 g%02d03 0 0%s %s w=%su l=%su %s
Vd%02d03 d%02d03 0 %s
Vg%02d03 g%02d03 0 0.1
.dc Vg%02d03 0 %s %s
%s
.meas dc vtscc_%s find V(g%02d03) when I(Vd%02d03)=par('%s*%s*%s/%s')
.meas dc idsat_%s find I(x%s03%s) when V(g%02d03,0)=%s
"""%(mdl,NO,NO,addNode,mdl,w,l,lodSize,NO,NO,vdd,NO,NO,NO,vgg,step,vtsgmExp,mdl,NO,NO,-1*mS,icon,w,l,mdl,mdl,CMP,NO,vgg)
    return specSatSNet

def specVtbS(NO,mdl,mType,vgg,vbb,size,sq):
    if mType == 'N':
        mS = 1; Vdcon1 = Vdcon; step = 0.01
        vtlgmExp = "max par('(lx7(x%s05%s%s)*v(g%02d05%s)-lx4(x%s05%s%s))/lx7(x%s05%s%s)-0.05')"%(mdl,sq,CMP,NO,sq,mdl,sq,CMP,mdl,sq,CMP)

    elif mType == 'P':
        mS = -1; Vdcon1 = -1*Vdcon; step = -0.01
        vtlgmExp = "min par('(lx7(x%s05%s%s)*v(g%02d05%s)-lx4(x%s05%s%s))/lx7(x%s05%s%s)+0.05')"%(mdl,sq,CMP,NO,sq,mdl,sq,CMP,mdl,sq,CMP)

    w = size.split('/')[0]
    l = size.split('/')[1]
    sa = float(size.split('/')[2])
    if sa > 0 and sa <= 10:
        lodSize = "sa=%su sb=%su"%(sa,sa)
    else:
        lodSize = ""
    specVtbSNet = """

x%s05%s d%02d05%s g%02d05%s 0 b%02d05%s%s %s w=%su l=%su %s
Vd%02d05%s d%02d05%s 0 %s
Vg%02d05%s g%02d05%s 0 0.1
Vb%02d05%s b%02d05%s 0 %s
.dc Vg%02d05%s 0 %s %s
.meas dc vtbgm5%s_%s %s
.meas dc vtbcc5%s_%s find V(g%02d05%s) when I(Vd%02d05%s)=par('%s*%s*%s/%s')
"""%(mdl,sq,NO,sq,NO,sq,NO,sq,addNode,mdl,w,l,lodSize,NO,sq,NO,sq,Vdcon1,NO,sq,NO,sq,NO,sq,NO,sq,vbb,NO,sq,vgg,step,sq,mdl,vtlgmExp,sq,mdl,NO,sq,NO,sq,-1*mS,icon,w,l)
    return specVtbSNet


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

x%s06 d%02d06 0 0 0%s %s w=%su l=%su %s
Vd%02d06 d%02d06 0 %s
.dc Vd%02d06 0 %s %s
.meas dc ioff_%s find I(x%s06%s) when V(d%02d06,0)=%s
"""%(mdl,NO,addNode,mdl,w,l,lodSize,NO,NO,vdoff,NO,vdoff,step,mdl,mdl,CMP,NO,vdoff)
    return specIoffSNet
#******************spec function for subckt model end******************#

def main():
    Vbb = raw_input("please input Vbb for simulation,use English comma as seperator, eg:-1.5,-2.5,-3.5,-4.5\n")
    #Vbb = input("please input Vbb for simulation,use English comma as seperator, eg:-1.5,-2.5,-3.5,-4.5\n")
    
    Vbb_li = Vbb.split(',')   # get a list of Vbb like ['1.0', '1.1', '1.2', '1.3']

    # the following lines help us get the specList according to the input by user
    temp_li_gm = []
    temp_li_cc = []     
    for i in range(len(Vbb_li)):
        magic_number = 50+i
        temp_li_gm.append("vtbgm"+str(magic_number)+"_"+MN)  # 得到vtbgm50_lvnemos4_1p2_lvpw
        temp_li_cc.append("vtbcc"+str(magic_number)+"_"+MN)
    specList = ["cgg_"+MN,"vtlgm_"+MN,"vtsgm_"+MN,"vtlcc_"+MN,"vtscc_"+MN,"idsat_"+MN,"idlin_"+MN,"ioff_"+MN] + temp_li_gm + temp_li_cc


    for i in device_size:
        if modelType == "S":
            cggNetlist = cggS(1,MN,vcgg,cgg_size)
            linNetlist = specLinS(1,MN,polarity,vgg,i)
            satNetlist = specSatS(1,MN,polarity,vdd,vgg,i)
            ioffNetlist = specIoffS(1,MN,polarity,vdoff,i)

            vtbNetlist = ''
            for sq in range(len(Vbb_li)):   # i is used, we should not use i to iterate
                vbb = eval(Vbb_li[sq])
                result_vb_netlist = specVtbS(1,MN,polarity,vgg,vbb,i,sq) + ls # sq is the sequence number user typed in.
                vtbNetlist += result_vb_netlist

        elif modelType == "C":
            cggNetlist = cggC(1,MN,vcgg,cgg_size)
            linNetlist = specLinC(1,MN,polarity,vgg,i)
            satNetlist = specSatC(1,MN,polarity,vdd,vgg,i)
            ioffNetlist = specIoffC(1,MN,polarity,vdoff,i)

            vtbNetlist = ''
            for sq in range(len(Vbb_li)):
                vbb = eval(Vbb_li[sq])
                result_vb_netlist = specVtbC(1,MN,polarity,vgg,vbb,i,sq) + ls
                vtbNetlist += result_vb_netlist

        netlist2 = cggNetlist + linNetlist + satNetlist + vtbNetlist + ioffNetlist    

        corner_index = 0
        for j in corner:
            netlist1 = title + ls*2 + options + ls + j + ls + temp + ls*2   #这里的j对应着每一个corner
            netlist = netlist1 + netlist2 + end
            cornertitle = cornerName[corner_index]  # 这会给我们一个“TT”, "SS"之类的字符串
            # i is the device size, like "10/10/0.23", so i.replace('/','_') can get "10_10_0.23"
            size_for_filename = i.replace('/','_')
            netlistFile = "EDR_hspice_%s_%s.sp"%(size_for_filename,cornertitle)  #this will generate a series of netlist
            with open(netlistFile, 'w') as file:
                file.write(netlist)

            listFile = "EDR_%s_%s.lis"%(size_for_filename,cornertitle)
            cmd = "hspice " + netlistFile + " > " + listFile
            os.system(cmd)

            corner_index += 1
    delFile = "rm *.ms* *.sw* *.st* *.pa*"
    os.system(delFile)

    DICT = {}
    for file in os.listdir('.'):
        if file.endswith('.lis'):
		    size = '_'.join(file.split('_')[1:3])
		    corner_na = file.split('_')[-1][0:-4]
		    KEY = size + '_' + corner_na
		    
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




