#!/usr/bin/env python
# coding: utf-8

# In[14]:


import re
# user input: 
# MOSNAME eg: lvnemos4_1p2_lvpw
# PARAM_MARK eg:  _ne_1p2
# MOSNAME = 'lvnemos4_1p2_lvpw'
# PARAM_MARK = '_ne_1p2'
MOSNAME = 'lvpemos4_1p2_lvnw'
PARAM_MARK = '_pe_1p2'
LIB_FILENAME = '501per_35_VcA.lib'   # 这里需要自己改一下lib和mdl的文件名作为路径。测试阶段先取这个方式来打开文件。
MDL_FILENAME = '501per_35_VcA.mdl'


# In[15]:


###############################.lib  starts##################################################################################
###########################################################################################################################
# def get_counters(f):
#     """传入一个文件列表，如f = open('501per_35_VcA.lib').readlines()所返回的以行为单位存储的列表。"""
#     counterlist = []   # 存储所有含有标记PARAM_MARK eg:  _ne_1p2的行号
#     end_line_counterlist = []  # 存储终止行的行号
#     start_line_counterlist = []  # 存储起始行的行号
#     cornertype_counterlist = []  # 存储写有corner名字的行号

#     for counter, value in enumerate(f):
#         # 这个判断可以找出含有PARAM_MARK eg:  _ne_1p2 的行号counter
#         if PARAM_MARK in value:
#             counterlist.append(counter)

#     for c, i in enumerate(counterlist):   # c是有PARAM_MARK的行够成新列表的新计数器    
#         if c < len(counterlist)-1:  # 这个判断用于防止后面的c+1判断中数组过界
#         # 这个判断可以找到每一段终止行的行号
#             if counterlist[c+1] != (i+1):
#                 end_line_counterlist.append(i)
#             if counterlist[c-1] != (i-1):
#                 cornertype_counterlist.append(i-2)  # 向上推两行找到corner 如.lib tt_llv_corner
#                 start_line_counterlist.append(i)
                
# # [4, 34, 64, 94, 124, 154, 184, 214, 244]start_line_counterlist
# # [15, 45, 75, 105, 135, 165, 195, 225]end_line_counterlist
# # [2, 32, 62, 92, 122, 152, 182, 212, 242]cornertype_counterlist
# # counterlist是4~255  这里因为算法原因， end_line_counterlist缺失了一块，所以拿counterlist的尾巴来补齐。
#     end_line_counterlist.append(counterlist[-1])
#     return start_line_counterlist, end_line_counterlist, cornertype_counterlist


# In[16]:


###############################.lib  starts##################################################################################
###########################################################################################################################
def get_counters(f):
    # f = open('501per_35_VcA.lib').readlines()

    """传入一个文件列表，如f = open('501per_35_VcA.lib').readlines()所返回的以行为单位存储的列表。"""
    counterlist = []   # 存储所有含有标记PARAM_MARK eg:  _ne_1p2的行号
    end_line_counterlist = []  # 存储终止行的行号
    start_line_counterlist = []  # 存储起始行的行号
    cornertype_counterlist = []  # 存储写有corner名字的行号

    for counter, value in enumerate(f):
        # 这个判断可以找出含有PARAM_MARK eg:  _ne_1p2 的行号counter
        if PARAM_MARK in value:
            counterlist.append(counter)

    for c, i in enumerate(counterlist):   # c是有PARAM_MARK的行够成新列表的新计数器    
        if c < len(counterlist)-1:  # 这个判断用于防止后面的c+1判断中数组过界
        # 这个判断可以找到每一段终止行的行号
            if counterlist[c+1] != (i+1):
                end_line_counterlist.append(i)
            if counterlist[c-1] != (i-1):
                start_line_counterlist.append(i)

    # [4, 34, 64, 94, 124, 154, 184, 214, 244]start_line_counterlist
    # [15, 45, 75, 105, 135, 165, 195, 225]end_line_counterlist
    # [2, 32, 62, 92, 122, 152, 182, 212, 242]cornertype_counterlist
    # counterlist是4~255  这里因为算法原因， end_line_counterlist缺失了一块，所以拿counterlist的尾巴来补齐。
    end_line_counterlist.append(counterlist[-1])

    for counter, line in enumerate(f):
        if (".lib" in line) and (not(counter > counterlist[-1])):
            cornertype_counterlist.append(counter)


    return start_line_counterlist, end_line_counterlist, cornertype_counterlist


# In[17]:


def get_corner_stacks(s, e, c):
    """这个函数可以返回一个组装了9个文字垛的列表，不一定是9个，可以多也可以少。
    大致的输出li的构造如下：
    [".lib tt_llv_corner\n.param\n", ['文字垛'],".lib 'lvnemos4_1p2_lvpw .lib' core\n.endl tt_llv_corner\n","",[],"",......]
    要求的输入是start_line_counterlist, end_line_counterlist, cornertype_counterlist"""
    stackstart_list = []  # 字符垛开头组成的列表 
    stack_list = []      # 字符垛组成的列表
    stackend_list = []   # 字符垛结尾组成的列表 
    li = []             # 最后输出的打包列表
    for i in zip(s,e):  # 把一个个起点和终点组合成元组如（244,255），zip返回的元组的迭代器。
        start = i[0]    # 取某个元组的第一个元素为起点，第二个为终点。
        end = i[1]
        stack = f[start:end+1]  # 这是一个要copy的垛！
        stack_list.append(stack)
    for count in c:
        # 这个循环是为了提取构建出来文字堆的头部和尾部。
        corner_start = f[count]
        corner_start += '.param\n'
        corner_name = f[count][4:]
        corner_end = ".lib '%s.lib' core\n"%(MOSNAME)    # 这里把结尾的字符串替换成了用户定义的MOS管了。
        corner_end += '.endl'
        corner_end += corner_name
        corner_end += "\n\n"
        
        stackstart_list.append(corner_start)
        stackend_list.append(corner_end)
        
    for i in range(len(stack_list)):
        # 这个循环把文字堆组装打包返回出函数
        li.append(stackstart_list[i])
        li.append(stack_list[i])
        li.append(stackend_list[i])
    return li


# In[18]:


def get_lib_part(f):
    """对抽取.lib的部分进行封装，输入的是最初始读取的lib文件构成的行列表，返回的是抽取9个corner部分的列表。"""
    s, e, c = get_counters(f)    #  start_line_counterlist, end_line_counterlist, cornertype_counterlist 取首字母拆包
    li = get_corner_stacks(s, e, c)   
    li += ['\n\n']   # 这是9个corner部分的结果
    return li

# f = open('501per_35_VcA.lib').readlines()
# s, e, c = get_counters(f)    #  start_line_counterlist, end_line_counterlist, cornertype_counterlist 取首字母拆包
# li = get_corner_stacks(s, e, c)   
# li += ['\n\n']   # 这是9个corner部分的结果


# with open('9corner_test.txt', mode='w') as f:
#     for i in li:
#         f.writelines(i)
#         f.writelines('\n\n')
###############################.lib  ends##################################################################################
############################################################################################################################


# In[19]:


##############################.mdl starts#####################################################################################
############################################################################################################################
def get_mdl_content(mdl):
    """mdl是open('501per_35_VcA.mdl').readlines()返回的一个list,此函数用于抓取mdl中定位好的数据.
    列表形式返回并在结尾加了.endl core开头加了.lib core """
    # 先找到.subckt + MOSNAME作为起始，.ends +  MOSNAME作为终止，记录两个行号。
    for counter, line in enumerate(mdl):
        if (MOSNAME in line) and ('.subckt' in line):
            line_number_start = counter
        if (MOSNAME in line) and ('.ends' in line):
            line_number_end = counter

    rawdata = mdl[line_number_start:line_number_end+1]   # 初次筛取出之间的文本
    for counter, line in enumerate(rawdata):
        if '.model' in line:         # 找到 .model作为初始
            line_number_newstart = counter

    mydata = ['.lib core\n'] + rawdata[line_number_newstart:-1]+['.endl core']  # 舍弃了最后一行的".ends" ,后面加上自己的.endl core。
    return mydata


# In[20]:


def get_cleaned_data_list(line):
    """返回去除_mis的变量后的字符串组成的列表,以及匹配出来字符串的列表，用于后续的行输出替换过程。"""
    #例如使用 temp = "+vth0 = '0.499064+ dvth0_ne_1p2 + dvth0_ne_1p2_mis'  lvth0 = '-5.359379E-8 + dlvth0_ne_1p2_mis'  pvth0 = '-4.455343E-15 + dpvth0_ne_1p2'"
    temp = line
    li = []
    while True:
        #这个循环吧_mis全部找出来
        start = 0
        if temp.find('_mis') == -1:
            break
        else:
            start = temp.find('_mis')+4+1
            match = temp[:temp.find('_mis')+4+1]
            temp = temp[start:]
            li.append(match)  # 全部加进匹配的List里面。
    cleaned_data_list = []
    for i in li:
        # 对匹配出来的li做遍历，如果有一个+符号是一种处理逻辑，有多个+符合是另一种处理逻辑。
        count = 0
        for character in i:
            if character == '+':
                count += 1
        if count != 1:
            drop_point = i.rfind('+')  # drop point
            data = i[:drop_point].strip() + "'"
            cleaned_data_list.append(data)
        else:
            drop_point = i.rfind('+')  # drop point
            data = i[:drop_point].replace("'"," ")
            cleaned_data_list.append(data)
    matched_data_list = li
    return cleaned_data_list,matched_data_list


# In[21]:


def get_mis_cleaned_mdl(mydata):
    """将mdl清晰去掉mis参数以后返回list，输入是一个未清洗的文本list。"""
    newmdl = []
    for line in mydata:
        if '_mis' in line: # 找到含有_mis参数的行
            c, m = get_cleaned_data_list(line) # c是清洗以后的文字，m是清洗前匹配到的文字。
            for i in zip(c,m):  # 组包
                line = line.replace(i[1],i[0])  # 行内替换
                newmdl.append(line)
        else:
            newmdl.append(line)
    return newmdl    


# In[70]:


def get_cf_cleaned_mdl(without_mis):
    # import re
    # 下面这几个注释是测试时候用的，可以得出结果
#     s1 = "+ckappas = 0.6                      ckappad = 0.6                      cf = '5E-11*pre_layout_sw'"
#     s2 = "+cf = '0 + 4.5E-11*pre_layout_sw'                  clc = 1E-7                    cle = 0.6"
#     pat = re.compile(r"cf.*\'")  # cf开头，后续接任意字符，逗号结尾
#     pat.findall(s1)  # ["cf = '5E-11*pre_layout_sw'"]
#      # 逗号开头，空格出现任意次，0出现任意次，空格出现任意次，+号出现任意次，空格出现任意次，（要提取的任意字符），*号出现一次
#     pat1 = re.compile(r"\'\s*0*\s*\+*\s*(.*)\*") 
#     pat1.findall(s1)
#     pat.findall(s2)    
    p = re.compile(r"\'\s*0*\s*\+*\s*(.*)\*")
#     p = re.compile(r"\'0*\s*\+*\s*(.*)\*") # 找到 5E-11  在真实情况里面'  0 + ....'这个0前面还有空格，在notepad里看不见，需要
# 用python的控制台print才可以看到，以后degug要注意！
    p1 = re.compile(r"cf.*\'")  # cf开头，后续接任意字符，逗号结尾。找到["cf = '5E-11*pre_layout_sw'"]

    without_cf = []
    for line in without_mis:
        if 'cf' in line:  # 找到有cf的那行        
            digit = p.findall(line)[0]
            digit_for_sub = 'cf =' + digit  # cf = 5E-11
            line = p1.sub(digit_for_sub, line) # 用cf = 5E-11替换"cf = '5E-11*pre_layout_sw'"
            without_cf.append(line)
#             print(line)  #测试用
        else:
            without_cf.append(line)
    #清除mdl部分出现的空行
    without_cf_and_blank = []
    for line in without_cf:
        if line.strip() == "":
            continue
        else:
            without_cf_and_blank.append(line)
    return without_cf_and_blank


# In[23]:


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
    for line in mydata:
    #     print(pattern.sub(r'\1', line))
        line = pattern.sub(r'\1', line)
        without_all_params.append(line)
        
    return without_all_params


# In[11]:


# # 处理.lib文件的代码
# f = open('501per_35_VcA.lib').readlines()
# lib_part = get_lib_part(f)

# # 处理.mdl文件的代码
# mdl = open('501per_35_VcA.mdl').readlines()
# mydata = get_mdl_content(mdl)
# without_mis = get_mis_cleaned_mdl(mydata)  # 没有MIS参数的mdl列表。
# without_cf = get_cf_cleaned_mdl(without_mis)  # 没有CF参数的mdl列表
# without_all_params = get_allparams_cleaned_mdl(mydata)  # 没有全部参数的mdl列表

##############################.mdl ends#####################################################################################
############################################################################################################################


# In[73]:


##############################main function part#####################################################################################
############################################################################################################################
# 处理.lib文件的代码
# f = open('501per_35_VcA.lib').readlines()  # 这个读取文件的部分可以改成自动查找.lib结尾的
f = open(LIB_FILENAME).readlines()  # 这个读取文件的部分可以改成自动查找.lib结尾的
lib_part = get_lib_part(f)

# 处理.mdl文件的代码
# mdl = open('501per_35_VcA.mdl').readlines()  # 这个可以改成自动查找.mdl结尾的
mdl = open(MDL_FILENAME).readlines()  # 这个可以改成自动查找.mdl结尾的
mydata = get_mdl_content(mdl)
without_mis = get_mis_cleaned_mdl(mydata)  # 没有MIS参数的mdl列表。
without_cf = get_cf_cleaned_mdl(without_mis)  # 没有CF参数的mdl列表
# 为了保留cf的参数，先把cf的处理以后得到的就是纯数字
without_all_params = get_allparams_cleaned_mdl(without_cf)  # 没有全部参数的mdl列表 


# 汇总部分
corners_without_cf_mis = lib_part + without_cf

libfilename = MOSNAME + '.lib'
pmfilename = MOSNAME + '.pm'

with open(libfilename, mode='w') as f:
    for line in corners_without_cf_mis:
        f.writelines(line)
        
with open(pmfilename, mode='w') as f:
    for line in without_all_params:
        if line.strip() == "":
            continue
        if '.lib core' in line:
            continue
        if '.endl core' in line:
            continue
        f.writelines(line)

