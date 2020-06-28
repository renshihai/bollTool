import pandas as pd
import numpy as np
import os
import re
import time
import jieba
import sys
"""
提取带章节微视频知识点对应关系表：微视频知识点对应我们的详细知识点
数据源：1）石家庄提供的数据：微视频知识图谱
        2）自制的中间数据：详细知识点  --->  jyw  知识点
生成目标数据：微视频知识点  ---> jyw  知识点
"""
'''
章节	第一列	第二列	第三列
准备课	数一数	比一比	
位置	位置		
1～5的认识和加减法	1-5的认识	0的认识	有关0的加减法
	1-5的书写		
	第几		
	比大小		
	分和合	5以内的加减法	
	1-5的认识<N>1-5的书写<N>第几<N>比大小<N>分和合		
'''

def isNotNull(col):
    if (pd.isnull(col)):
        return False
    else:
        if len(col.strip()):
            return True
        else:
            return False

class Edition:
    def __init__(self):
        # come from: jyw  math
        self.editions={'人教版':'01','北师大版':'02','华师大版':'03','浙教版':'04','湘教版':'05','苏科版':'06','冀教版':'07',
                  '沪科版':'08','北京课改版':'09','鲁教五四版':'10','沪教版':'11','青岛版':'12','人教五四版':'13',
                  '人教新版':'14','北师大新版':'15','华师大新版':'16','苏科新版':'17','湘教新版':'18','青岛新版':'19',
                  '浙教新版':'20','冀教新版':'21','沪科新版':'22','鲁教五四新版':'23','北京课改新版':'24',
                  '沪教新版':'25','人教五四新版':'27'}

        self.grades={'一年级':'1','二年级':'2','三年级':'3','四年级':'4','五年级':'5','六年级':'6','七年级':'7','八年级':'8',
               '九年级':'9','高一':'10','高二':'11','高三':'12'}
        self.subjects={'数学':'0','物理':'1','化学':'2','生物':'3','地理':'5','语文':'6','英语':'7','道法':'8','历史':'9'}
        self.terms= {'上册':'1','下册':'2','全一册':'3'}

class Node:
    def __init__(self):
        self.Name=""
        self.No = 0
        self.Child=[]

class VPointCode:
    '''什么是可打印字符？在ASCII码中规定，0~31、127这33个字符属于控制字符，
    32~126这95个字符属于可打印字符，也就是说网络传输只能传输这95个字符，'''
    def __init__(self,vPoints):
        self.code = {}
        self.codeNum = 0

        if os.path.exists(vPoints):
            self.readPoints(vPoints)

    def readPoints(self,vPoints):
        with open(vPoints, 'r') as file_to_read:
            for line in file_to_read.readlines():
                line = line.replace('\n', '')
                p_tmp = line.split('\t')[0]
                self.code[p_tmp[4:]] = p_tmp[1:3]
            self.codeNum = len(self.code)

    def getCode(self,name,chk):
        jywCode = ''
        for item in name:
            if self.code.get(item) != None:
                if len(jywCode):
                    jywCode += ','
                jywCode += self.code.get(item)
            else:
                chk.write(item+'\n')
        return jywCode

class VideoPointsCharpter:
    def __init__(self, excelFile, vpoint):
        self.regex = re.compile(r'\[(.*)\]')
        self.points = {}
        self.all_nodes = {}
        (path,file) = os.path.split(excelFile)
        (f, ext) = os.path.splitext(excelFile)
        self.destinFileName = os.path.join('',f+'.csv')
        self.chkFileName = os.path.join('',f+'.chk')
        self.rule = re.compile('^[A-Z]{1}')
        # 根据文件名获取该书的信息：
        # 人教版一年级数学上册（知识图谱知识卡片）.xlsx
        ret = jieba.cut(file, cut_all=False)
        xret = "#".join(ret).split('#')
        self.edition = xret[0]
        self.grade = xret[1]
        self.subject = xret[2]
        self.term = xret[3]
        self.update = xret[4]

        self.df = pd.DataFrame(pd.read_excel(excelFile))
        # print(self.df.head())
        if '节' in self.df.columns:
            self.exsit_section = True
        else:
            self.exsit_section = False
        self.outdf = pd.DataFrame(None,columns=['v_point','points','subject','pointNames'])
        self.pointCode = VPointCode(vpoint)

    def getCorrespondRelation(self, src):
        # src = src.replace('<D>',r'",<D>"').replace('<R>',r'",<R>"').replace('<N>',r'","')
        spliteResult = src.split('<')
        result = []
        for item in spliteResult:
            if len(item):
                if self.rule.match(item) is None:
                    result.append(item)
                else:
                    style = item[0:1]
                    name = item[2:]
                    if style == 'N':
                        result.append(name)
                    else:
                        result.append('<'+style+'>'+name)
        return result

    def procExcel(self):
        column = ['第一列','第二列','第三列']
        line = 1;
        '''章	第一列	第二列	第三列'''
        charpter =''
        # section = ''
        sectionNode = []
        # knRow = {}
        for index, row in self.df.iterrows():
            curCharpter = row['章']
            curSection = row['节']

            if isNotNull(curCharpter):
                charpter = curCharpter
                self.all_nodes.setdefault(charpter,[])
                if len(sectionNode):
                    self.points[line-1] = sectionNode
                    sectionNode = []

            if isNotNull(curSection):
                section = curSection
                # self.all_nodes.setdefault(charpter, []).append(section)
                self.all_nodes.setdefault(charpter, []).append(str(line) + ':' + section)
                if len(sectionNode):
                    self.points[line-1] = sectionNode
                    sectionNode = []
                line += 1

            knRow = {}
            if isNotNull(column[0]):
                knRow["K1"] = self.getCorrespondRelation(row[column[0]])
            if isNotNull(row[column[1]]):
                item = self.getCorrespondRelation(row[column[1]])
                knRow["K2"] = item
            if isNotNull(row[column[2]]):
                item = self.getCorrespondRelation(row[column[2]])
                knRow["K3"] = item
            sectionNode.append(knRow)


    def outFile(self):
        # self.outdf.to_excel(self.destinFileName, index=False)
        # self.outdf.to_csv(self.destinFileName, sep="\t", index=False)
        chkVideoPoints = []
        chk = open(self.chkFileName, "wt")
        with open(self.destinFileName, "wt") as f:
            for key, value in self.all_nodes.items():
                jywCode = self.pointCode.getCode(value,chk)
                if len(jywCode):
                    f.write(key + '\t' + jywCode+'\t' + str(value))
                    f.write('\n')
                else:
                    f.write(key + '\t' + 'None' + '\t' + str(value)+'\n')
                    chk.write('::'+key+'\t'+str(value)+"\n")

        chk.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('用法:\n\t可执行程序名\t输入文件\t配置文件')
        print('说明:\n\t输入文件：待处理知识图谱文件\n\t配置文件:内容为我们微课知识点编码')
        sys.exit(0)
    # ep = VideoPointsCharpter("\知识图谱_源数据_sample.xlsx",r'.\data\boll_points\小学数学菁优网试题匹配关系.pot')
    ep = VideoPointsCharpter(sys.argv[1],sys.argv[2])
    ep.procExcel()
    ep.outFile()

