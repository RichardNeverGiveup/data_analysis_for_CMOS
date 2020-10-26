#!/usr/bin/env python
# coding: utf-8

# In[44]:


# 两个文件名作为输入。
# LIB_FILENAME = "lvnemos4_1p2_lvpw.lib"
LIB_FILENAME = "lvpemos4_1p2_lvnw.lib"   # 这是已经修改好model参数的子lib
# TOTAL_LIB_FILENAME = "501per_76_VcA.lib"   # 这是总的model的lib
TOTAL_LIB_FILENAME = "501per_35_VcA.lib"   # 这是总的model的lib


# In[7]:


import re


# In[30]:


#***************************子Lib文件处理部分***************************************************************************
def get_sonlib_dict(LIB_FILENAME):
    f = open(LIB_FILENAME).readlines()

    line_numb_list = []
    corner_name_list = []
    for line_numb, line in enumerate(f):
    #     if ('.lib' in line) and (not('core' in line)):   # 不好用
        if '.lib' in line:
    #         print(line_numb, line)   # 打印有.lib的行号和行内容用于debug
            # .lib tt_llv_corner 和 .lib 'lvnemos4_1p2_lvpw.lib' core的行号都会被加进去，取这两个号码之间行为参数行。
            line_numb_list.append(line_numb) 
            corner_name = line.split()[1]   # 这个split是根据.lib和 tt_llv_corner中间的空格进行分割，我们要的返还的第二部分。
            # .lib 'lvnemos4_1p2_lvpw.lib' core上述分割会取【1】这个部分会得到'lvnemos4_1p2_lvpw.lib'这个东西，
            # 我们不再判断一下，如果里面如果corner_name里面没有.lib了，那就是我们要的，添加进corner_name_list里面。
            if not(".lib" in corner_name):  #  
                corner_name_list.append(corner_name)

    # 找到所有含.lib的行，最后一个会有.lib core，把它剔除了。        
    corner_name_list = corner_name_list[:-1] 
    line_numb_list = line_numb_list[:-1]

    param_everycorner_list = []  #里面存放的一系列元组，元祖内容的是每个corner+号参数的首尾行号。
    # 因为行号是两两配对，配成的行号对之间的原始f的行就是我们要后续抽取的参数部分
    for i in range(0, len(line_numb_list), 2): 
    #     print(line_numb_list[i], line_numb_list[i+1])   # this is the indice of the lines of params.
        # 这个循环用于找到.lib tt_llv_corner到.lib 'lvnemos4_1p2_lvpw.lib' core之间的首个含有+号的行
    #     print(line_numb_list[i],line_numb_list[i+1])  # 用于debug
        for newcount, line in enumerate(f[line_numb_list[i]: line_numb_list[i+1]]):
            if '+' in line:
    #             print(newcount+line_numb_list[i]) #newcount+line_numb_list[i]就是在原始f中每个corner第一个+号开始的行号。
    #             print(line)  #用于debug
                line_number_of_first_param_in_everycorner = newcount+line_numb_list[i]
                line_tuple_of_param = (line_number_of_first_param_in_everycorner, line_numb_list[i+1])
    #             print(line_tuple_of_param)# 这个元组是某个corner内+号开头到+号结尾部分参数的元组。
                param_everycorner_list.append(line_tuple_of_param) # 添加到列表里面。
                break

    param_dict = {}  # 构建一个字典，键是corner的名字，值就是那一堆+号的参数。
    for i in range(len(corner_name_list)):  
        corner_name = corner_name_list[i]
        start = param_everycorner_list[i][0] # 取元组的首个元素
        end = param_everycorner_list[i][1]
        param_lines = f[start:end]
    #     print(param_lines)
        param_dict[corner_name] = param_lines
    
    return param_dict
#***************************子Lib文件处理部分***************************************************************************


# In[42]:


#***************************总Lib文件处理部分***************************************************************************
# import re
def get_matched_start_end_in_totallib(TOTAL_LIB_FILENAME, cornerName, mostype):
    endmark_for_totallib = re.compile(r".lib\s*statistical")
    f_toatal = open(TOTAL_LIB_FILENAME).readlines()

    # reg_content = "\+.*?" + "_ne_3p3" # mostype  #测试用_ne_3p3，_lvp_pb，_zc是mostype
    reg_content = "\+.*?" + mostype   #************ mostype 是一个输入
    startmark_foronetypemos_incorner = re.compile(reg_content)  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_ne_3p3")  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_pe_3p3")  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_zc")  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_pe_1p2")   #这个在测试的时候报告没找到！！！

    corner_start = 0 # 初始化变量
    corner_end = 0
    end_of_f_total_inuse = 0 # 初始化变量

    # 拿到了只含有corner部分的总lib
    for count, line in enumerate(f_toatal):
        if endmark_for_totallib.match(line):
    #         print(line)
    #         print(count)
            end_of_f_total_inuse = count
    f_toatal_inuse = f_toatal[:end_of_f_total_inuse]  

    # 找到了总的corner的起点
    for count, line in enumerate(f_toatal_inuse):
        # 这个"tt_lv_corner" in line后续要用字典里面的键来替代  #********这里是一个输入cornerName eg"tt_lv_corner"
        if (cornerName in line) and (".lib" in line):
    #         print(line)
            corner_start = count
        if (cornerName in line) and (".endl" in line):
    #         print(line)
            corner_end = count

    count = 0 # 子lib和总lib匹配了多少行，进行计数。非0则提醒总lib文件里没有匹配到对应的参数！
    matchedlinenumberlist = []
    for linenumber, line in enumerate(f_toatal_inuse[corner_start: corner_end]): # 这里用corner_start会带来一个问题！！！
        # 初始化匹配到了0行
        if startmark_foronetypemos_incorner.match(line):
            count += 1
            # 如果匹配到了含有"\+.*?_ne_3p3"的行就记录下来行号
    #         print(line)
    #         print(corner_start + linenumber)
    # 注意这里我们要的是对应于原始f的行号，所以要用corner_start + linenumber！！！！！！
            matchedlinenumberlist.append(corner_start + linenumber)  # [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]

    if count == 0:
        print("您要从子lib替换到总lib的%s的MOS类型%s在总lib的参数文件里没有找到！！！"%(cornerName, mostype))
        return (-1,-1) # 以这个作为没找到的标志传回到主函数。
    else:
        print("您要从子lib的%s的MOS类型%s替换到总lib的参数共有%d行"%(cornerName, mostype, count))
        matchedlinenumber_start = matchedlinenumberlist[0]
        matchedlinenumber_end = matchedlinenumberlist[-1]
        return matchedlinenumber_start, matchedlinenumber_end  # 17, 28

#***************************子Lib文件处理部分***************************************************************************    


# In[45]:


param_dict = get_sonlib_dict(LIB_FILENAME)

reg_mostype = re.compile(r"\+.*?(_.*?)\s* =")

f_toatal = open(TOTAL_LIB_FILENAME).readlines()
for k in param_dict.keys():
    firstline = param_dict[k][0]
    mostype = reg_mostype.findall(firstline)[0]
    cornerName = k
    start, end = get_matched_start_end_in_totallib(TOTAL_LIB_FILENAME, cornerName, mostype)
    if start == -1:
        print("fail to update!!!fail to update!!!fail to update!!!")
    else:
        if len(param_dict[k]) == (end+1-start):
            print("子文件中欲替换行数=母文件中匹配行数，更新成功！接下来为您替换母文件的第%d到%d行"%(start,end))
        # 成功更新，用处理子文件函数返回的字典里面的值来替换总文件里面对应行号的值。
            f_toatal[start:end+1] = param_dict[k]
#             print(start,end+1)
        else:
            print("子文件和母文件欲替换行号不等，更新失败！！！")
            


# In[ ]:




