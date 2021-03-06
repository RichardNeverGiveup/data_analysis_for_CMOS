#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
#*******************************************************
# user input: 
# MOSNAME eg: lvnemos4_1p2_lvpw
# MOSTYPE eg:  _ne_1p2
# LIB_FILENAME = '501per_35_VcA.lib'   
# MDL_FILENAME = '501per_35_VcA.mdl'
#********************************************************
MOSNAME = '_llv_rvtp'
MOSTYPE = '_llv_rvtp'
LIB_FILENAME = 'trident_1d2_mos.lib'   # 这里需要自己改一下lib和mdl的文件名作为路径。测试阶段先取这个方式来打开文件。
MDL_FILENAME = 'trident_1d2_mos.mdl'


# In[2]:


def get_dict_of_lib(LIB_FILENAME):
    """输入LIB的文件名，返回各个CORNER名为键，其对应的行内容为值的字典。"""
    f = open(LIB_FILENAME).readlines()

    for line_number, line in enumerate(f):
        if ".lib statistical_mc" in line:
            end_of_corners_in_lib = line_number        
    print("初步定位到总LIB的第%d行之前的内容为LIB需要分裂出的内容。"%end_of_corners_in_lib)
    
    list_of_corners_star2end_tuples = []
    for line_number, line in enumerate(f[:end_of_corners_in_lib]):
        if ".lib" in line:
            single_corner_start = line_number
        if ".endl" in line:
            single_corner_end = line_number
            list_of_corners_star2end_tuples.append((single_corner_start, single_corner_end))

    corner_param_dict = {}
    for t in list_of_corners_star2end_tuples:
        key = f[t[0]].split()[1] # tt_llv_corner  as key
        value = f[t[0]:t[1]+1]
        corner_param_dict[key] = value
        print("%s已经存入字典，其内容对应行号为%d到%d"%(key, t[0], t[1]))
        
    return corner_param_dict


# In[3]:


def get_dict_of_single_mostype_dict_of_lib(corner_param_dict):
    """紧接着corner_param_dict = get_dict_of_lib(LIB_FILENAME)后面调用，传入含有多个MOSTYPE的LIB字典。
    输出只剩一种MOSTYPE的字典。"""
    reg_content = "\+.*?" + MOSTYPE + "\s*="
    mark_foronetypemos_incorner = re.compile(reg_content)

    single_mostype_corner_param_dict = {}
    print("和你输入的MOSTYPE匹配的每个CORNER的首行和尾行如下！")
    for k in corner_param_dict:
        v = corner_param_dict[k]
        new_v = []
        for line in v:
            if mark_foronetypemos_incorner.search(line):
                new_v.append(line)
        single_mostype_corner_param_dict[k] = new_v
        
        print(new_v[0], new_v[-1])
    print("********************************************************************************************************")
    return single_mostype_corner_param_dict


# In[4]:


def get_final_lib_part(MOSNAME, single_mostype_corner_param_dict):
    final_lib_part = []
    for k in single_mostype_corner_param_dict:
        cornerfirstline = ".lib " + k + "\n"
        cornersecondline = ".param" + "\n"
        cornersecondlastline = ".lib '" + MOSNAME + ".lib' core" + "\n"
        cornerlastline = ".endl " + k + "\n\n"


        final_lib_part.append(cornerfirstline)
        final_lib_part.append(cornersecondline)
        for line in single_mostype_corner_param_dict[k]:
            final_lib_part.append(line)
        final_lib_part.append(cornersecondlastline)
        final_lib_part.append(cornerlastline)

    return final_lib_part


# In[5]:


#corner_param_dict = get_dict_of_lib(LIB_FILENAME)
#get_dict_of_single_mostype_dict_of_lib(corner_param_dict)


# In[6]:


def get_blank_striped_mdl(MDL_FILENAME, MOSNAME):
    """输出是去除了空行的mdl内容。"""
    f = open(MDL_FILENAME).readlines()

    content_temp_start = '.subckt\s*' + MOSNAME + "\s"
    regex_temp_start = re.compile(content_temp_start)

    content_temp_end = '.ends\s*' + MOSNAME + "\s"
    regex_temp_end = re.compile(content_temp_end)

    for line_number, line in enumerate(f):
        if regex_temp_start.search(line):
            print("定位到总MDL文件的第%d行作为临时起始行"%line_number)
            temp_start = line_number
      

        if regex_temp_end.search(line):
            print("定位到总MDL文件的第%d行作为临时终止行"%line_number)
            temp_end = line_number
            tuple_of_linenumber_for_mdl_in_use = (temp_start, temp_end)

    temp_start = tuple_of_linenumber_for_mdl_in_use[0] #  '.subckt\s*'的行号
    temp_end = tuple_of_linenumber_for_mdl_in_use[1]   #  '.ends\s*'的行号

    mdl_in_use = f[temp_start: temp_end+1]   
    for line_number, line in enumerate(mdl_in_use):
        if ".model" in line:
            newstart = line_number
            
            mdl_content = mdl_in_use[newstart:]
            
            startlinenumberinoriginalmdl = newstart + temp_start  # '.model'在'.subckt\s*'和'.ends\s*'之间的行号
            print("定位到总MDL文件的第%d行作为真正的起始行"%startlinenumberinoriginalmdl)


    blank_striped_mdl_content = []
    for line_number, line in enumerate(mdl_content):
        if line.strip() == "":
            print("第%d行是空行。"%(startlinenumberinoriginalmdl + line_number ))
            continue
        blank_striped_mdl_content.append(line)
    blank_striped_mdl_content
    print("根据你输入的MOSNAME:%s,将从原总MDL中复制第%d行到第%d行。"%(MOSNAME, startlinenumberinoriginalmdl, temp_end))
    print("********************************************************************************************************")

    return blank_striped_mdl_content


# In[7]:


def clean_all_mis_in_one_line(line):
    """利用从右向左的机制去一直去除_mis参数，返回除去干净了的Line。"""
    while True:
        if '_mis' in line:
            startof_mis = line.rfind('_mis') # 从右向左，找到了_mis的位置
            startof_plus_nexttomis = line[:startof_mis].rfind('+')  # 找到了第一个紧靠mis左边的+号
            startof_equal_nexttomis = line[:startof_mis].rfind('=') # 找到了第一个紧靠mis左边的=号
            remain = line[startof_equal_nexttomis:startof_plus_nexttomis] #第一个紧靠mis左边的=号到 mis直接的字符，用于判断是纯数字了，还是数字+参数的格式
            # remain 是这样的 "= '0.35 + deta0_ne_1p2 "
            original = line[startof_equal_nexttomis:startof_mis+5] #把含_mis'这部分原始的取出来，如"= '0.35 + deta0_ne_1p2 + deta0_ne_1p2_mis'"
            if '+' in remain:
                for_replacement = remain.strip() + "'"
            else:
                for_replacement = remain.strip().replace("'","")

            line = line.replace(original, for_replacement)
        else:
            break
    return line


# In[8]:


####################测试去除每行中MIS的代码####################################################################################
##################################################################################################################################
# line = "+pnfactor = -3E-14             eta0 = '0.35 + deta0_ne_1p2 + deta0_ne_1p2_mis'  peta0 = '-1.81E-15 + dpeta0_ne_1p2'"
# line = "+pnfactor = -3E-14             eta0 = '0.35 + deta0_ne_1p2_mis'  peta0 = '-1.81E-15 + dpeta0_ne_1p2'"
# line = "+pnfactor = '0.39 + pnf_ne_1p2_mis'   eta0 = '0.35 + deta0_ne_1p2_mis'  peta0 = '-1.81E-15 + dpeta0_ne_1p2'"
# while True:
#     if '_mis' in line:
#         startof_mis = line.rfind('_mis') # 从右向左，找到了_mis的位置
#         startof_plus_nexttomis = line[:startof_mis].rfind('+')  # 找到了第一个紧靠mis左边的+号
#         startof_equal_nexttomis = line[:startof_mis].rfind('=') # 找到了第一个紧靠mis左边的=号
#         remain = line[startof_equal_nexttomis:startof_plus_nexttomis] #第一个紧靠mis左边的=号到 mis直接的字符，用于判断是纯数字了，还是数字+参数的格式
#         # remain 是这样的 "= '0.35 + deta0_ne_1p2 "
#         original = line[startof_equal_nexttomis:startof_mis+5] #把含_mis'这部分原始的取出来，如"= '0.35 + deta0_ne_1p2 + deta0_ne_1p2_mis'"
#         if '+' in remain:
#             for_replacement = remain.strip() + "'"
#         else:
#             for_replacement = remain.strip().replace("'","")

#         line = line.replace(original, for_replacement)
#     else:
#         break
# line
##################################################################################################################################
##################################################################################################################################


# In[9]:


def get_mis_cleaned_mdl(raw_mdl):
    mis_cleaned_mdl = []
    print("开始去除MIS参数**********************************************************************************************")
    for line in raw_mdl:
        if '_mis' in line:        
            
            print(line)
            line = clean_all_mis_in_one_line(line)
            print(line)
            
        mis_cleaned_mdl.append(line)
    print("去除MIS参数结束**********************************************************************************************")
    return mis_cleaned_mdl


# In[10]:


# #########测试cf去除效果################################################################################################
# #######################################################################################################################
# line = "+cf = '0 + 4.5E-11*pre_layout_sw'                  clc = 1E-7                    cle = 0.6"
# line = "+clc = 1E-7         cle = 0.6           cf = '0 + 4.5E-11*pre_layout_sw'"
# line = "+clc = 1E-7         cf = '0 + 4.5E-11*pre_layout_sw          cle = 0.6 '"

# print(line)
# startof_cf = line.find('cf')
# startof_pre = line.find("*pre_layout_sw")
# startof_equal = line[:startof_pre].rfind('=')
# startof_plus = line[:startof_pre].rfind('+')

# for_replacement = "=" + line[startof_plus:startof_pre].replace('+',"").strip()  # 得到 '=4.5E-11'
# orginal = line[startof_equal:startof_pre+len("*pre_layout_sw'")]  # 得到 "= '0 + 4.5E-11*pre_layout_sw'" 
# line = line.replace(orginal, for_replacement)
# print(line)
# #######################################################################################################################


# In[11]:


def get_cf_cleaned_mdl(mis_cleaned_mdl):
    cf_cleaned_mdl = []
    print("开始去除CF参数**********************************************************************************************")
    for line in mis_cleaned_mdl:
        if "cf" in line:
            print("替换前的行为：")
            print(line)
            startof_cf = line.rfind('cf')
            startof_pre = line.rfind("pre_layout_sw")
            startof_equal = line[:startof_pre].rfind('=')
            startof_plus = line[:startof_pre].rfind('+')

            for_replacement = "=" + line[startof_plus:startof_pre].replace('+',"").replace('*',"").strip()  # 得到 '=4.5E-11'
            
            original = line[startof_equal:startof_pre+len("pre_layout_sw'")]  # 得到 "= '0 + 4.5E-11*pre_layout_sw'" 
            print("我们要替换CF行的表达式是%s。"%for_replacement)
            print("原始未替换的CF对应的表达式是%s。"%original)
            line = line.replace(original, for_replacement)
            print("替换后的行为：")
            print(line)
        cf_cleaned_mdl.append(line)
    cf_cleaned_mdl = cf_cleaned_mdl[:-1]       # 去掉最后一个 .ends lvnemos4_1p2_lvpw
    print("去除CF参数结束**********************************************************************************************")
    return cf_cleaned_mdl


# In[12]:


############用于测试替换cf的代码################################################################################################
##################################################################################################################################
# line = "+cf = '0 + 4.5E-11*pre_layout_sw'                  clc = 1E-7                    cle = 0.6 "
# startof_cf = line.find('cf')
# startof_pre = line.find("*pre_layout_sw")
# startof_equal = line.find('=')
# startof_plus = line[startof_cf:startof_pre].find('+')
# for_replacement = "=" + line[startof_plus:startof_pre].replace('+',"").strip()  # 得到 '=4.5E-11'
# orginal = line[startof_equal:startof_pre+len("*pre_layout_sw'")]  # 得到 "= '0 + 4.5E-11*pre_layout_sw'" 
# line.replace(orginal, for_replacement)
##################################################################################################################################
##################################################################################################################################


# In[13]:


def get_allparams_cleaned_mdl(mydata):
    """输入是被定位出来的含有出事model内容的mdl列表，称为mydata。输出被正则替换掉全部参数的mdl列表"""
# 这一段注释是测试代码，用于验证正则表达式
# pattern = re.compile(r"\'([-]*[0-9.E]*\-*\d*)[+-]*.*?\'")  # 这是当初为钟灿写的正则，我现在也看不太懂了。
# for line in mydata:
#     if "'" in line:
#         print(line)
#         print(pattern.findall(line))

    pattern = re.compile(r"\'([-]*[0-9.E]*\-*\d*)[+-]*.*?\'")  # 这是当初为钟灿写的正则，我现在也看不太懂了。
    without_all_params = []
    print("现在执行替换全部MDL参数的函数**************************************************************************************")
    print("所有的含义参数的行内容如下*****************************************************************************************")
    for line in mydata:
        if pattern.search(line):
            print(line)
    #     print(pattern.sub(r'\1', line))
        line = pattern.sub(r'\1', line)
        without_all_params.append(line)
    #without_all_params = without_all_params[:-1]   # 去掉最后一个 .ends lvnemos4_1p2_lvpw
    print("********************************************************************************************************************")
    return without_all_params


# In[14]:


def get_final_lib(final_lib_part, cf_cleaned_mdl):
    lib_core_part = []
    lib_core_part.append(".lib core\n")
    for line in cf_cleaned_mdl:    
        lib_core_part.append(line)
    lib_core_part.append(".endl core\n")
    lib_core_part
    final_lib = final_lib_part + lib_core_part

    return final_lib


# In[15]:


###########处理LIB的部分#########################################################################
corner_param_dict = get_dict_of_lib(LIB_FILENAME)
single_mostype_corner_param_dict = get_dict_of_single_mostype_dict_of_lib(corner_param_dict)
final_lib_part = get_final_lib_part(MOSNAME, single_mostype_corner_param_dict)
###########处理MDL的部分####################################################################
raw_mdl = get_blank_striped_mdl(MDL_FILENAME,MOSNAME)
mis_cleaned_mdl = get_mis_cleaned_mdl(raw_mdl)
cf_cleaned_mdl = get_cf_cleaned_mdl(mis_cleaned_mdl)
allparams_cleaned_mdl = get_allparams_cleaned_mdl(cf_cleaned_mdl)
############################################################################################
final_lib = get_final_lib(final_lib_part, cf_cleaned_mdl)

libfilename = MOSNAME + '.lib_NEW'
pmfilename = MOSNAME + '.pm_NEW'

with open(libfilename, mode='w') as f:
    for line in final_lib:
        f.writelines(line)
with open(pmfilename, mode='w') as f:
    for line in allparams_cleaned_mdl:
        f.writelines(line)

input("输入任意键退出！")

