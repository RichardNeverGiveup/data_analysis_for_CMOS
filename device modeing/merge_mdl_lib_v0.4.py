#!/usr/bin/env python
# coding: utf-8

# In[1]:


# # 两个文件名作为输入。
# # LIB_FILENAME = "lvnemos4_1p2_lvpw.lib"
# # LIB_FILENAME = "lvpemos4_1p2_lvnw.lib"   # 这是已经修改好model参数的子lib
# LIB_FILENAME = "_lvpemos4_3p3_lvnw_zch.lib"
# # TOTAL_LIB_FILENAME = "501per_76_VcA.lib"   # 这是总的model的lib
# TOTAL_LIB_FILENAME = "501per_35_VcA.lib"   # 这是总的model的lib


# In[2]:


import re


# In[3]:


#***************************子Lib文件处理部分***************************************************************************

# 只能处理这种_pe_3p3一个类型的多个corner，不能_pe_3p3,_ne_3p3,...多个类型多个corner！！！虽然返回的是各个corner之间的值，
# 理论上允许子文件里可以一个corner里面多个MOSTYPE存进字典里，但是后面对接的函数没有实现处理一个corner多个MOSTYPE的接口！！！

def get_sonlib_dict(LIB_FILENAME):
    f = open(LIB_FILENAME).readlines()
    
    line_numb_list = []
    corner_name_list = []
    for line_numb, line in enumerate(f):
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
    
        # 循环每对.lib tt_llv_corner到.lib 'lvnemos4_1p2_lvpw.lib' core之间，都重新产生一次这个列表，覆盖掉无所谓，因为
        # 里面的数据每次循环都已经处理添加到了param_everycorner_list里面。
        param_startline_to_endline_per_corner = [] 
        
        # 这个循环遍历了从 .lib tt_llv_corner到 .lib 'lvnemos4_1p2_lvpw.lib' core之间的行
        #之前由于没考虑中间会有空行或者其他的情况，出现了不匹配的bug。
        for newcount, line in enumerate(f[line_numb_list[i]: line_numb_list[i+1]]):
            if '+' in line:
#********************************************************************************************************************************
# 老的实现方式。逻辑考虑不周全出现了bug。
#     #             print(newcount+line_numb_list[i]) #newcount+line_numb_list[i]就是在原始f中每个corner第一个+号开始的行号。
#     #             print(line)  #用于debug
#                 line_number_of_first_param_in_everycorner = newcount+line_numb_list[i]
#                 line_tuple_of_param = (line_number_of_first_param_in_everycorner, line_numb_list[i+1])
#     #             print(line_tuple_of_param)# 这个元组是某个corner内+号开头到+号结尾部分参数的元组。
#                 param_everycorner_list.append(line_tuple_of_param) # 添加到列表里面。
#                 break
#********************************************************************************************************************************
                paramline = newcount+line_numb_list[i]  # 每一个有+号的行对于原始f的行号
                param_startline_to_endline_per_corner.append(paramline) # 存入这个列表里面
        start = param_startline_to_endline_per_corner[0]
        end = param_startline_to_endline_per_corner[-1] + 1 # 按照旧的后续接口的实现方式，是要+1
        line_tuple_of_param = (start, end)
        param_everycorner_list.append(line_tuple_of_param)
                
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


# In[4]:


#***************************总Lib文件处理部分***************************************************************************
# import re
def get_matched_start_end_in_totallib(TOTAL_LIB_FILENAME, cornerName, mostype):
    endmark_for_totallib = re.compile(r".lib\s*statistical")
    f_total = open(TOTAL_LIB_FILENAME).readlines()

    # reg_content = "\+.*?" + "_ne_3p3" # mostype  #测试用_ne_3p3，_lvp_pb，_zc是mostype
    reg_content = "\+.*?" + mostype + "\s*="   #************ mostype 是一个输入，用结尾的空格和等号来进一步判断。
    startmark_foronetypemos_incorner = re.compile(reg_content)  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_ne_3p3")  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_pe_3p3")  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_zc")  # 这个_ne_3p3后续可替换
    # startmark_foronetypemos_incorner = re.compile(r"\+.*?_pe_1p2")   #这个在测试的时候报告没找到！！！

    corner_start = 0 # 初始化变量
    corner_end = 0
    end_of_f_total_inuse = 0 # 初始化变量

    # 拿到了只含有corner部分的总lib
    for count, line in enumerate(f_total):
#****************************************************************************************************************
#         之前这种match的用法很危险，只有开头和正则匹配才会返回，不然就算内部有对于的字符串返回也是None
#         if endmark_for_totallib.match(line):
#****************************************************************************************************************
        if endmark_for_totallib.search(line):
    #         print(line)
    #         print(count)
            end_of_f_total_inuse = count
    f_total_inuse = f_total[:end_of_f_total_inuse]  

    # 找到了总的corner的起点
    for count, line in enumerate(f_total_inuse):
        # 这个"tt_lv_corner" in line后续要用字典里面的键来替代  #********这里是一个输入cornerName eg"tt_lv_corner"
        if (cornerName in line) and (".lib" in line):
    #         print(line)
            corner_start = count
        if (cornerName in line) and (".endl" in line):
    #         print(line)
            corner_end = count

    count = 0 # 子lib和总lib匹配了多少行，进行计数。0则提醒总lib文件里没有匹配到对应的参数！
    matchedlinenumberlist = []
    for linenumber, line in enumerate(f_total_inuse[corner_start: corner_end]): # 这里用corner_start会带来一个问题！！！
        # 初始化匹配到了0行
        if startmark_foronetypemos_incorner.search(line):
            count += 1
            # 如果匹配到了含有"\+.*?_ne_3p3"的行就记录下来行号
    #         print(line)
    #         print(corner_start + linenumber)
    # 注意这里我们要的是对应于原始f的行号，所以要用corner_start + linenumber！！！！！！
            matchedlinenumberlist.append(corner_start + linenumber)  # [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
    print("************************************************************************************************************")
    print("*************************总LIB文件替换函数相关提示**********************************************************")
    if count == 0:        
        print("您要从子lib替换到总lib的%s的MOS类型%s在总lib的参数文件里没有找到！！！"%(cornerName, mostype))
        return (-1,-1) # 以这个作为没找到的标志传回到主函数。
    else:
        print("您要从子lib的%s的MOS类型%s替换到总lib的参数在总lib共有%d行"%(cornerName, mostype, count))
        matchedlinenumber_start = matchedlinenumberlist[0]
        matchedlinenumber_end = matchedlinenumberlist[-1]
        return matchedlinenumber_start, matchedlinenumber_end  # 17, 28

#***************************子Lib文件处理部分***************************************************************************    


# In[5]:


#***************************总Lib文件处理部分（要求输入一个f_total）**************************************************************
# import re
def get_matched_start_end_in_totallib_input_f_total_version(f_total, TOTAL_LIB_FILENAME, cornerName, mostype):
    endmark_for_totallib = re.compile(r".lib\s*statistical")
#     f_total = open(TOTAL_LIB_FILENAME).readlines()

    # reg_content = "\+.*?" + "_ne_3p3" # mostype  #测试用_ne_3p3，_lvp_pb，_zc是mostype
    reg_content = "\+.*?" + mostype + "\s*="   #************ mostype 是一个输入
    startmark_foronetypemos_incorner = re.compile(reg_content)  # 这个_ne_3p3后续可替换


    corner_start = 0 # 初始化变量
    corner_end = 0
    end_of_f_total_inuse = 0 # 初始化变量

    # 拿到了只含有corner部分的总lib
    for count, line in enumerate(f_total):
#****************************************************************************************************************
#         之前这种match的用法很危险，只有开头和正则匹配才会返回，不然就算内部有对于的字符串返回也是None
#         if endmark_for_totallib.match(line):
#****************************************************************************************************************
        if endmark_for_totallib.search(line):
    #         print(line)
    #         print(count)
            end_of_f_total_inuse = count
    f_total_inuse = f_total[:end_of_f_total_inuse]  

    # 找到了总的corner的起点
    for count, line in enumerate(f_total_inuse):
        # 这个"tt_lv_corner" in line后续要用字典里面的键来替代  #********这里是一个输入cornerName eg"tt_lv_corner"
        if (cornerName in line) and (".lib" in line):
    #         print(line)
            corner_start = count
        if (cornerName in line) and (".endl" in line):
    #         print(line)
            corner_end = count

    count = 0 # 子lib和总lib匹配了多少行，进行计数。0则提醒总lib文件里没有匹配到对应的参数！
    matchedlinenumberlist = []
    for linenumber, line in enumerate(f_total_inuse[corner_start: corner_end]): # 这里用corner_start会带来一个问题！！！
        # 初始化匹配到了0行
        if startmark_foronetypemos_incorner.search(line):
            count += 1
            # 如果匹配到了含有"\+.*?_ne_3p3"的行就记录下来行号
    #         print(line)
    #         print(corner_start + linenumber)
    # 注意这里我们要的是对应于原始f的行号，所以要用corner_start + linenumber！！！！！！
            matchedlinenumberlist.append(corner_start + linenumber)  # [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
#     print("************************************************************************************************************")
#     print("*************************总LIB文件替换函数相关提示**********************************************************")
    if count == 0:        
#         print("您要从子lib替换到总lib的%s的MOS类型%s在总lib的参数文件里没有找到！！！"%(cornerName, mostype))
        return (-1,-1) # 以这个作为没找到的标志传回到主函数。
    else:
#         print("您要从子lib的%s的MOS类型%s替换到总lib的参数在总lib共有%d行"%(cornerName, mostype, count))
        matchedlinenumber_start = matchedlinenumberlist[0]
        matchedlinenumber_end = matchedlinenumberlist[-1]
        return matchedlinenumber_start, matchedlinenumber_end  # 17, 28

#***************************子Lib文件处理部分***************************************************************************    


# In[6]:


def get_corner_updated_totalfile(LIB_FILENAME, TOTAL_LIB_FILENAME):
    """返回更新了corner的文件列表"""
    param_dict = get_sonlib_dict(LIB_FILENAME)

    reg_mostype = re.compile(r"\+.*?(_.*?)\s* =") # 准备自动抓取出MOSTYPE

    f_total = open(TOTAL_LIB_FILENAME).readlines()
    # 这个循环会便利字典里面的每一个corner，然后更新f_total这个列表
    for k in param_dict.keys():
        firstline = param_dict[k][0]
        mostype = reg_mostype.findall(firstline)[0] # 从返回的子LIB字典里每个键（corner）对应的值的第一行自动抓取出MOSTYPE
        cornerName = k     # tt_lv_corner这是键，也就是cornerName
#***************这是一个逻辑疏漏，不应该直接调用函数了，因为这每次返回的都是原始总LIB里面对应的start和end***********************
#***************如果在遍历字典的过程里因为某个corner行多出来了几行，则会出现错位！！！******************************************
#         start, end = get_matched_start_end_in_totallib(TOTAL_LIB_FILENAME, cornerName, mostype)
#*******************************************************************************************************************************

# *******这次调用，我们不要利用它的返回值，我们只是利用其函数内部的打印输出提示信息！因为我们要记录*****************************
# *******总LIB原文件里面对于的corner的行号，这样我们检查的时候也方便去原文件里面查找！******************************************
        get_matched_start_end_in_totallib(TOTAL_LIB_FILENAME, cornerName, mostype)
# ******************************************************************************************************************************

# ********因为这里个调用的函数每次输入了一个f_total，这个f_total是更新变化的，动态反应了字典每个值加进去后总文件里面的行********
# *******通常如果子LIB里面没有新增参数行的话，起始位置是不会变化的**************************************************************
        start, end = get_matched_start_end_in_totallib_input_f_total_version(f_total, TOTAL_LIB_FILENAME, cornerName, mostype)
# ******************************************************************************************************************************    
        if start == -1:
            print("fail to update!!!fail to update!!!fail to update!!!")
        else:
            if len(param_dict[k]) == (end+1-start):
                print("子文件中欲替换行数=母文件中匹配行数，更新成功！接下来为您替换母文件的第%d到%d行"%(start,end))
            # 成功更新，用处理子文件函数返回的字典里面的值来替换总文件里面对应行号的值。
                f_total[start:end+1] = param_dict[k] # 这里把f_totall给更新了
#                 f_total[start:end+1] = ['for test\n'] * (end+1-start) # 这段代码测试用
    #             print(start,end+1)
            else:
            #***********************这部分逻辑很难搞，这意味着新子LIB里面的参数和原始的总LIB的参数行数不同************
            #***********************意味着有新添加的参数在子LIB里面，不能直接简单替换列表切片了***********************
                print("Causion!子文件和母文件欲替换行号不等，更新提醒，请确定子LIB该部分是否存在增删参数行！！！")
                print("Causion!子文件对应corner对应MOSTYPE下共有%d行参数"%len(param_dict[k]))
                print("正在把子LIB替换进主LIB............")
                f_total = f_total[:start] + param_dict[k] +  f_total[end+1:]
                print("替换成功！")
#         print(len(param_dict[k]))
    return f_total


# In[7]:


#****************处理总MDL部分的代码*****************************************************************************************
#***********因为子LIB文件只有一个MDL，不用在遍历，所以这里我们不用写那个需要输入f_mdl作为函数输入的变体函数******************
#*********但是要注意这里子LIB这部分MDL替换进入总MDL里面以后，可能总MDL行数变化了*********************************************
#*********在生成的COPY副本文件里面行数如果变化了，再继续后续其他子LIB替换的时候可能出错**************************************
#*********所以再传下一个子LIB的时候要把上次替换得到的COPY文件名字修改成总MDL的名字，接着跑脚本！*****************************
def get_totalfile_linenumber_for_substitution(LIB_FILENAME,TOTAL_LIB_FILENAME):
    """找出总MDL里面'.model'和'.ends\s*'位置作为返回值"""
    MOSNAME = LIB_FILENAME.split('.')[0]
    TOTAL_MDL_FILENAME = TOTAL_LIB_FILENAME.split('.')[0] + '.mdl'

    content_temp_start = '.subckt\s*' + MOSNAME + "\s"
    regex_temp_start = re.compile(content_temp_start)

    content_temp_end = '.ends\s*' + MOSNAME + "\s"
    regex_temp_end = re.compile(content_temp_end)

    f_mdl = open(TOTAL_MDL_FILENAME).readlines()

    temp_start = 0  # '.subckt _lvpemos4_3p3_lvnw_zch 'line number
    temp_end = 0    # '.ends _lvpemos4_3p3_lvnw_zch' line number
    for count, line in enumerate(f_mdl):
        if regex_temp_start.search(line):
    #         print(count, line)
            temp_start = count
        if regex_temp_end.search(line):
            temp_end = count
    #         print(count, line)

    model_line_number = 0
    for count, line in enumerate(f_mdl[temp_start:temp_end]): 
        if '.model' in line:
            model_line_number = count + temp_start
    #         print(model_line_number, line)   # '.model PE.all PMOS' line number
    return model_line_number, temp_end  # 返回总的mdl文件里面的起始和结尾


# In[8]:


def get_blank_striped_small_lib_for_totalMDL(LIB_FILENAME):
    """把子LIB里面MDL部分的行去除空行后返回"""
    f_lib_small = open(LIB_FILENAME).readlines()
    regex_lib_small_start = re.compile(r".model\s*")
    regex_lib_small_end = re.compile(r".endl\s*core")

    lib_small_start = 0
    lib_small_end = 0

    for count, line in enumerate(f_lib_small):
        if regex_lib_small_start.search(line):
    #         print(count, line)
            lib_small_start = count
        if regex_lib_small_end.search(line):
    #         print(count, line)
            lib_small_end = count

    blankstripedlines = []  # 保存子lib里清除了空行以后要替换到母mdl里面的行
    for count, line in enumerate(f_lib_small[lib_small_start: lib_small_end+1]):# ***** 包头包尾作为规范！！！！******
        if line.strip() == "":
            blanklinenumber = count + lib_small_start
            print("************************************************************************************************************")
            print("*************************总MDL文件替换函数相关提示**********************************************************")
            print("在子lib的MDL部分里面存在空行，行号为%d"%blanklinenumber)
            continue
        blankstripedlines.append(line)
    tip = '''
子lib里面要替换到主mdl文件的总行数为%d。
行计数从.model到.endl core，不含任何空白行。
之前出现的空白行将被程序自动摘除，不会存入主文件。
摘除不会修改子lib的原文件，后续请自行检查子文件空行问题！
    '''%len(blankstripedlines)
    print(tip)
    return blankstripedlines

#**********************测试用****************************************************************************************************
#*********************************************************************************************************************************
# f_lib_small = open(LIB_FILENAME).readlines()
# regex_lib_small_start = re.compile(r".model\s*")
# regex_lib_small_end = re.compile(r".endl\s*core")

# lib_small_start = 0
# lib_small_end = 0

# for count, line in enumerate(f_lib_small):
#     if regex_lib_small_start.search(line):
# #         print(count, line)
#         lib_small_start = count
#     if regex_lib_small_end.search(line):
# #         print(count, line)
#         lib_small_end = count

# blankstripedlines = []  # 保存子lib里清除了空行以后要替换到母mdl里面的行
# for count, line in enumerate(f_lib_small[lib_small_start: lib_small_end+1]):
#     if line.strip() == "":
#         blanklinenumber = count + lib_small_start
#         print("在子lib里面存在空行，行号为%d"%blanklinenumber)
#         continue
#     blankstripedlines.append(line)
# tip = '''
# 子lib里面要替换到主mdl文件的总行数为%d。
# 行计数从.model到.endl core，不含任何空白行。
# 之前出现的空白行将被程序自动摘除，不会存入主文件。
# 摘除不会修改子lib的原文件，后续请自行检查子文件空行问题！
# '''%len(blankstripedlines)
# # print(tip)
# blankstripedlines
# print(len(blankstripedlines))
#*********************************************************************************************************************************


# In[9]:


#****************************************************************************************************************
# 测试两个不同正则匹配效果的代码
# test = "+cf =3.04E-11                 clc = 0                       cle = 0.6 "
# # p = re.compile(r"\s*(cf\s*=.*?)\s\w")
# p = re.compile(r"\s*(cf\s*=\s*[0-9.E]*\-*\d*)")
# p.findall(test)
#****************************************************************************************************************
#****************************************************************************************************************
# 测试cf替换功能的代码
# p_for_cf = re.compile(r"\s*(cf\s*=\s*[0-9.E]*\-*\d*)")
# line = '+clc = 0         cf =3.04E-11                   cle = 0.6'
# line = '+cf =3.04E-11                 clc = 0                       cle = 0.6'
# if p_for_cf.search(line):
#     print(line)
#     cf = p_for_cf.findall(line)[0]
#     print(cf)
#     cf_value = cf.split('=')[1]
#     print(cf_value)
#     newcf = 'cf = 0 + ' + cf_value + '*pre_layout_sw'
#     print(newcf)
#     newline = line.replace(cf, newcf)
#     print(newline)
#****************************************************************************************************************
def get_cf_replaced_small_lib_for_totalMDL(LIB_FILENAME):
    """会调用get_blank_striped_small_lib_for_totalMDL这个函数，需要输入LIB_FILENAME。得到的是调整好了的cf参数组成的列表。"""
    p_for_cf = re.compile(r"\s*(cf\s*=\s*[0-9.E]*\-*\d*)")
    
#老的实现方式会让函数跑完多一行,跑出来两个cf**************************************************************************  
#************************************************************************************************************* 
    cf_replaced_small_lib = []
    for line in get_blank_striped_small_lib_for_totalMDL(LIB_FILENAME):
        if p_for_cf.search(line):
            cf = p_for_cf.findall(line)[0]
            cf_value = cf.split('=')[1]
            newcf = "cf = '0 + " + cf_value + "*pre_layout_sw'"
            newline = line.replace(cf, newcf)
            cf_replaced_small_lib.append(newline)
            continue    # 少写了这个致命的continue！！！！
        cf_replaced_small_lib.append(line)
    return cf_replaced_small_lib
#************************************************************************************************************* 
#!!!为什么在这里函数跑完结果会多出了一行？？？？？
# print(len(get_cf_replaced_small_lib_for_totalMDL(LIB_FILENAME)))
# get_cf_replaced_small_lib_for_totalMDL(LIB_FILENAME)


# In[10]:


def get_compact_totalmdl(TOTAL_LIB_FILENAME, LIB_FILENAME):
    """因为从子lib过来的都是已经去除了空行的，这边不知道总MDL里面是不是有空行，需要去除空行，并且计算一下长度。"""
    TOTAL_MDL_FILENAME = TOTAL_LIB_FILENAME.split('.')[0] + '.mdl'
    start, end = get_totalfile_linenumber_for_substitution(LIB_FILENAME, TOTAL_LIB_FILENAME)
    f_mdl = open(TOTAL_MDL_FILENAME).readlines()
    total_mdl_without_blank = []
    for line in f_mdl[start: end+1]:
        if line.strip() == "":
            continue
        total_mdl_without_blank.append(line)
#     return len(mdl_without_blank)
    return total_mdl_without_blank
#*******************测试用**********************************************************************************************
#*************************************************************************************************************************
# TOTAL_MDL_FILENAME = TOTAL_LIB_FILENAME.split('.')[0] + '.mdl'
# start, end = get_totalfile_linenumber_for_substitution(LIB_FILENAME,TOTAL_LIB_FILENAME)
# f_mdl = open(TOTAL_MDL_FILENAME).readlines()
# mdl_without_blank = []
# for line in f_mdl[start: end+1]:
#     if line.strip() == "":
#         continue
#     mdl_without_blank.append(line)
# mdl_without_blank
#*************************************************************************************************************************


# In[11]:


def write_new_total_MDL(TOTAL_LIB_FILENAME, LIB_FILENAME):
    """会在当前文件夹中写一个新的MDL文件，以COPY命名结尾。"""
    TOTAL_MDL_FILENAME = TOTAL_LIB_FILENAME.split('.')[0] + '.mdl' # 需要输入TOTAL_LIB_FILENAME， LIB_FILENAME
    TOTAL_MDL_FILENAME_OUTPUT = TOTAL_MDL_FILENAME + '_COPY'

    f_total_mdl = open(TOTAL_MDL_FILENAME).readlines()

    small_mdl = get_cf_replaced_small_lib_for_totalMDL(LIB_FILENAME)
    total_mdl_without_blank = get_compact_totalmdl(TOTAL_LIB_FILENAME, LIB_FILENAME)
    # 用于替换的总MDL的起点和重点序号
    start, end = get_totalfile_linenumber_for_substitution(LIB_FILENAME, TOTAL_LIB_FILENAME)


    if len(small_mdl) == len(total_mdl_without_blank):
        print("去除空行后，子LIB里面MDL部分的行数为%d。"%len(small_mdl))
        print("去除空行后，总LIB里面MDL部分的行数为%d。"%len(total_mdl_without_blank))
        print("去除空行后，子LIB里面MDL部分的行数和总MDL里面的行数相同，可以进行替换。")
        print("将要替换总MDL的%d行到%d行"%(start, end))

        end_of_substitution = start + len(small_mdl) - 1 # 要减去最后一个endl core的那行所以-1

    #     small_mdl[0] = "为了测试做替换！"
    #     small_mdl[-2] = "为了测试做替换！"
    #     print(end_of_substitution)
        f_total_mdl[start: end_of_substitution] = small_mdl[:-1]
        f_total_mdl[end_of_substitution: end] = ['\n'] * (end - end_of_substitution)#把空余的行填空白行。
    #     f_total_mdl[end_of_substitution: end] = ['\n实验'] * (end - end_of_substitution)
        print("当前%sMDL部分进入到总MDL的替换已完成！"%(LIB_FILENAME))

#         with open(TOTAL_MDL_FILENAME_OUTPUT, mode='w') as f:
#             for line in f_total_mdl:
#                 f.writelines(line)

    else:
        print("去除空行后，子LIB里面MDL部分的行数为%d。"%len(small_mdl))
        print("去除空行后，总LIB里面MDL部分的行数为%d。"%len(total_mdl_without_blank))
        print("Causion!!!去除空行后，子LIB里面MDL部分的行数和总MDL里面的行数不相同，请校验是否增删了参数行！！！")
    # f_total_mdl
        end_of_substitution = start + len(small_mdl) - 1 
        f_total_mdl = f_total_mdl[:start] + small_mdl[:-1] + ['\n'] * (end - end_of_substitution) + f_total_mdl[end:]
        
        
        
        print("当前%sMDL部分进入到总MDL的替换已完成！"%(LIB_FILENAME))
    
    with open(TOTAL_MDL_FILENAME_OUTPUT, mode='w') as f:
        for line in f_total_mdl:
            f.writelines(line)    
    


# In[12]:


def write_new_total_LIB(TOTAL_LIB_FILENAME, LIB_FILENAME):
    """在当前文件夹书写生成一个命名以COPY结尾的总LIB文件。"""
    TOTAL_LIB_FILENAME_OUTPUT = TOTAL_LIB_FILENAME + '_COPY'

    # 存储了已经替换了corner的总文件
    after_corner_merge_totalfile = get_corner_updated_totalfile(LIB_FILENAME, TOTAL_LIB_FILENAME)

    with open(TOTAL_LIB_FILENAME_OUTPUT, mode='w') as f:
        for line in after_corner_merge_totalfile:
            f.writelines(line)    
    # after_corner_merge_totalfile


# In[ ]:


if __name__ == "__main__":

    LIB_FILENAME = "_lvpemos4_3p3_lvnw_zch.lib"
    TOTAL_LIB_FILENAME = "501per_76_VcA.lib"   # 这是总的model的lib
    #     TOTAL_LIB_FILENAME = "501per_35_VcA.lib"   # 这是总的model的lib
    write_new_total_LIB(TOTAL_LIB_FILENAME, LIB_FILENAME)
    write_new_total_MDL(TOTAL_LIB_FILENAME, LIB_FILENAME)
    a = input("输入任意值停止！")

