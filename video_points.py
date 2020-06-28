import pandas as pd
import numpy as np
import os
import re
import time
import torch as t
"""
提取微视频知识点对应关系表：微视频知识点对应我们的详细知识点
数据源：1）石家庄提供的数据：微视频知识点 --->  详细知识点
        2）自制的中间数据：详细知识点  --->  jyw  知识点
生成目标数据：微视频知识点  ---> jyw  知识点
"""
def isNotNull(col):
    if (pd.isnull(col)):
        return False
    else:
        return True

class Dict:
    def __init__(self):
        self.v_point = 0
        self.points = 0
        self.subject = 0
        self.pointNames = ''

class Point2JywCode:
    '''什么是可打印字符？在ASCII码中规定，0~31、127这33个字符属于控制字符，
    32~126这95个字符属于可打印字符，也就是说网络传输只能传输这95个字符，'''
    def __init__(self,oldPoints):
        self.code = {}
        self.codeNum = 0

        if os.path.exists(oldPoints):
            self.readPoints_old(oldPoints)

    def readPoints(self,oldPoints):
        jywdf = pd.read_csv(oldPoints,sep='\t',engine='python')
        #point_id	parent_id	subject	name	code	code_jyw	order_num	code_jyw_str
        for index, row in jywdf.iterrows():
            row['name'] = row['code_jyw']
        self.codeNum = len(self.code)

    def readPoints_old(self,oldPoints):
        with open(oldPoints, 'r',encoding='utf-8') as file_to_read:
            line = file_to_read.readline() # skip first line
            for line in file_to_read.readlines():
                line = line.replace('\n', '')
                p_tmp = [i for i in line.split('\t')]  # 将整行数据分割处理，如果分割符是空格，括号里就不用传入参数，如果是逗号， 则传入‘，'字符。
                self.code[p_tmp[3]] = p_tmp[5] # 添加新读取的数据
            self.codeNum = len(self.code)


    def getCode(self,name,chk):
        '''jywCode = ''
        for item in name:
            if self.code.get(item) != None:
                if len(jywCode):
                    jywCode += ','
                jywCode += self.code.get(item)
            else:
                chk.write(item+'\n')'''
        jywCode = []
        code =''
        for item in name:
            code = self.code.get(item)
            if code != None and len(code):
                jywCode.append(code)
            else:
                chk.write(item+'\n')
        return ','.join(set(jywCode))

class VPointEncode:
    def __init__(self):
        # y = ['!','#','$','%','(',')','*','+','-','/',':','<','=','>','?','@','[','\',']','^','_','{','|','}','~',]
        # self.ascii_code = ['0','1','2']
        self.ascii_code = ['0','1','2','3','4','5','6','7','8','9',
                           'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                           'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                           '!','#','$','%','(',')','*','+','-','/',':','<','=','>','?','@','[',']','^','_','{','|','}','~']
        self.ascii_len = len(self.ascii_code)
        self.first = 0
        self.second = -1
        self.codeNum = 0
        self.code_set = {}

    def producePosi(self):
        self.second += 1
        if(self.second == self.ascii_len):
            self.second = 0
            self.first += 1

    def getCode(self, codeStr):
        if codeStr in self.code_set.keys():
            return self.code_set[codeStr]
        self.producePosi()
        current = self.ascii_code[self.first]+self.ascii_code[self.second]
        self.code_set[codeStr] = current
        return current

    def readCodeSet(self, oldVPoints):
        with open(oldVPoints, 'r') as file_to_read:
            for line in file_to_read.readlines():
                p_tmp = [i for i in line.split()]
                self.code_set[p_tmp[0]] = p_tmp[1]
            self.codeNum = len(self.code)

    def writeCodeSet(self,newVPoints):
        if self.codeNum == len(self.code):
            return
        with open(newVPoints, "wt") as f:
            for key, value in self.code.items():
                f.write(key + '\t' + str(value))
                f.write('\n')

class ExtractVideoPoints:
    def __init__(self, excelFile, point2Jyw, pointVBoll):
        self.regex = re.compile(r'\[(.*)\]')
        self.points = {}
        (f, ext) = os.path.splitext(excelFile)
        self.destinFileName = os.path.join('',f+'.csv')
        self.chkFileName = os.path.join('',f+'.chk')
        self.nullCol = ''

        self.df = pd.DataFrame(pd.read_excel(excelFile))
        # print(self.df.head())
        self.outdf = pd.DataFrame(None,columns=['v_point','points','subject','pointNames'])
        self.microClass = []
        flag = False;
        for item in self.df.columns:
            if item.startswith("微课"):
                flag = True
                self.microClass.append(item)
            else:
                if flag:
                    self.nullCol = item
        # 详细知识点对应菁优网的知识点
        self.pointCode = Point2JywCode(point2Jyw)
        # boll 的微课知识点，第一次创建生成，后续读取并可能追加
        self.bollVPointCode = VPointEncode()
        # if len(pointVBoll):
        #     self.bollVPointCode.readCodeSet(pointVBoll)

    def procExcel(self):
        # firstIdx = {}
        # secondIdx = {}
        subject_tree = {}
        # pointCode = PointCode(self.oldPoints)
        subjects = {"小学数学": 10, "小学语文": 11, "小学英语": 12, "小学科学": 14, "初中数学": 20, "初中物理": 21, "初中化学": 22,
                    "初中生物": 23, "初中地理": 25, "初中语文": 26, "初中英语": 27, "初中道法": 28, "初中历史": 29, "高中数学": 30,
                    "高中物理": 31, "高中化学": 32, "高中生物": 33, "高中地理": 35, "高中语文": 36, "高中英语": 37, "高中政治": 38,
                    "高中历史": 39, "高中信息": 42, "高中通用": 43}
        gradeCode = 0;
        subject = ""
        # "Pkid"	"学段名称"	"学科名称"	"年级代码"	"学科代码"	"一级ID"	"一级知识点"	"二级ID"	"二级知识点"	"三级ID"	"三级知识点"
        '''
        Pkid	学段名称	学科名称	年级代码	学科代码	一级ID	一级知识点	二级ID	二级知识点	三级ID	三级知识点
        15063	小学	数学	14	3	1403 1	百分数	1403 101	百分数的认识	1403 10101	百分数的读法
        '''
        line = 1;
        # dict.setdefault('1', 0)  # 默认值设为0
        # self.points.setdefault("1",set())
        # self.points.setdefault("1",set()).add("N1")
        # self.points.setdefault("1",set()).add("N2")
        # self.points.setdefault("1",set()).add("N2")

        for index, row in self.df.iterrows():
            # if row['一级知识点'] != '整数':
            #     continue
            subject = row['学段名称'] + row['学科名称']
            oL = Dict()
            oL.point_id = line
            if subject_tree.get(subject) == None:
                oL.subject = subjects.get(subject)
                subject_tree[subject] = oL.subject
            else:
                oL.subject = subject_tree.get(subject)
            name = ""
            if isNotNull(row['三级ID']):
                name = row['三级ID']+'#'+row['三级知识点']
            elif isNotNull(row['二级ID']):
                name = row['二级ID'] + '#'+ row['二级知识点']
            elif isNotNull(row['一级ID']):
                name = row['一级ID'] + '#'+ row['一级知识点']

            for item in self.microClass:
                if isNotNull(row[item]):
                    self.points.setdefault(row[item],set()).add(name)
            # if len(self.nullCol) and isNotNull(row[self.nullCol]):
            #     self.points.setdefault(row[self.nullCol], set()).add("")
        if len(self.nullCol):
            for item in self.df[self.nullCol]:
                if isNotNull(item):
                    self.points.setdefault(item, set()).add("")


    def outFile(self):
        # self.outdf.to_excel(self.destinFileName, index=False)
        # self.outdf.to_csv(self.destinFileName, sep="\t", index=False)
        chkVideoPoints = []
        chk = open(self.chkFileName, "wt")
        with open(self.destinFileName, "wt") as f:
            for key, value in self.points.items():
                print(key,value)
                jywCode = self.pointCode.getCode(value,chk)
                boll_vcode = self.bollVPointCode.getCode(key)
                if len(jywCode):
                    f.write('['+boll_vcode+']'+key + '\t' + jywCode+'\t' + str(value))
                    f.write('\n')
                else:
                    f.write('['+boll_vcode+']'+key + '\t' + '' + '\t' + str(value)+'\n')
                    chk.write('::'+key+'\t'+str(value)+"\n")
        chk.close()

if __name__ == "__main__":
    rootdir =  r'.\data\video_points\知识点与微课的匹配关系'
    ep = ExtractVideoPoints(rootdir+"\数学知识点对应微课5.26.xlsx",r'.\data\boll_points\小学+初中数学菁优网试题匹配关系_dst.csv','')
    # ep = ExtractPoints(rootdir+"\小学数学菁优网试题匹配关系.xlsx","")
    ep.procExcel()
    ep.outFile()

