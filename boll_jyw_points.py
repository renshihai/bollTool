import pandas as pd
import numpy as np
import os
import re
import time
import sys
"""
说明：源数据是石家庄团队提供的文件，其中有知识点对应关系
处理方法：首先对我们的知识点进行编号，下次更新的时候会使用该编号，从而确保原编号不变，连贯性
之前是也知识点来对我们的知识点编码，可能有冲突，现改成使用“知识点ID”
"""
def isNotNull(col):
    # if (col is not np.nan and len(col) > 0):
    # if (col is not np.nan):
    if (pd.isnull(col)):
    # if (col.isna()):
        return False
    else:
        if (col is not np.nan):
            return True
        else:
            return False

class Dict:
    def __init__(self):
        self.point_id = 0
        self.parent_id = 0
        self.subject = 0
        self.name = ''
        self.code = ''
        self.code_jyw =''
        self.code_jyw_str =''
        self.order_num = 0  # 暂时用来保存当前是属于哪一级

    def do_nothing(self):
        pass

class extractCorrespondingTbl:
    def __init__(self, fileName):
        self.start = 4;
        # self.firstTree = []
        # self.secondTree = []
        # self.thirdTree = []
        self.allTree = {}
        self.fileName = fileName
        self.cdf = pd.DataFrame(pd.read_excel(self.fileName))

    # def isNotNull(self,col):
    #     if(col is not np.nan and len(col) > 0):
    #         return True
    #     else:
    #         return False

    def readTbl(self):
        regex = re.compile(r'\[(.*)\]')
        idr = r'[\d\s]+'
        # for index, row in self.cdf.iteritems():

        # print(self.cdf.shape)
        for row in range(0,self.cdf.shape[0]):
            col3 = self.cdf.iloc[row, 2]
            if (isNotNull(col3)):
                pointId = regex.findall(col3)
                # print(type(pointId))
                for col in range(self.start, self.cdf.shape[1],2):
                    colx = self.cdf.iloc[row, col]
                    if(isNotNull(colx) and re.match(idr,colx)):
                        # self.allTree.append({colx: {'id':pointId[0],'name':col3}})
                        self.allTree[colx] = {'id':pointId[0],'name':col3}
                    else:
                        break

    def getPoints(self,name):
        tmp = self.allTree.get(name,None)
        if(tmp == None):
            return ""
        else:
            return tmp.get("id")
            # return tmp.get("name")

class PointCode:
    '''什么是可打印字符？在ASCII码中规定，0~31、127这33个字符属于控制字符，
    32~126这95个字符属于可打印字符，也就是说网络传输只能传输这95个字符，'''
    def __init__(self,oldPoints):
        self.firstChar = 49
        self.secondChar = 47
        self.code = {}
        self.codeNum = 0

        if os.path.exists(oldPoints):
            self.readOldPoints(oldPoints)

    def reset(self):
        self.firstChar = 49
        self.secondChar = 47

    def readOldPoints(self,oldPoints):
        with open(oldPoints, 'r') as file_to_read:
            for line in file_to_read.readlines():
                p_tmp = [i for i in line.split()]  # 将整行数据分割处理，如果分割符是空格，括号里就不用传入参数，如果是逗号， 则传入‘，'字符。
                self.code[p_tmp[0]] = p_tmp[1] # 添加新读取的数据
            self.codeNum = len(self.code)

    def writePoints(self,fileName):
        if self.codeNum == len(self.code):
            return
        with open(fileName, "wt") as f:
            # jsObj = json.dumps(self.code)
            # f.write(jsObj)
            for key, value in self.code.items():
                f.write(key + '\t' + str(value))
                f.write('\n')

    def getCode(self,name):
        if self.code.get(name) != None:
            return self.code.get(name)
        else:
            self.secondChar += 1
            if(self.secondChar == 123):
                self.firstChar += 1
                self.secondChar = 48
            tmp = chr(self.firstChar)+chr(self.secondChar)
            self.code[name] = tmp
            # self.code[name] = format('{}#{:0>2d}{:0>2d}'.format(tmp, self.firstChar,self.secondChar))
            return self.code[name]

class ExtractPoints:
    def __init__(self, excelFile, oldPoints):
        self.regex = re.compile(r'\[(.*)\]')
        self.fileName = excelFile
        self.oldPoints = oldPoints
        self.newPoints = oldPoints
        (path, file) = os.path.split(excelFile)
        (f,e) = os.path.splitext(file)
        self.destinFileName = os.path.join(path,f+'_dst.csv')
        self.df = pd.DataFrame(pd.read_excel(self.fileName))
        print(self.df.head())
        self.outdf = pd.DataFrame(None,columns=['point_id','parent_id','subject','name','code','code_jyw','order_num','code_jyw_str'])
        knowledge = ["知识点一","知识点二","知识点三","知识点四","知识点五","知识点六","知识点七","知识点八"]
        self.knowledges = []
        for item in knowledge:
            if item in self.df.columns:
                self.knowledges.append(item)

        ft = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime())

        self.pointCode = PointCode(self.oldPoints)
        if len(oldPoints) > 0:
            self.newPoints = os.path.join(path, ft + f + ".pot")
        else:
            self.newPoints = os.path.join(path, f+".pot" )

    def getJywPoints(self,row):
        points = ''
        points_str = ''
        for item in self.knowledges:
            if isNotNull(row[item]) and len(row[item].strip()) > 0:
                if len(points) > 0:
                    points += ','
                    points_str += ','
                group = self.regex.findall(row[item])
                # print(group)
                # if(len(group) == 0):
                #     print(group)
                if len(group) == 0:
                    print('error:'+row[item])
                else:
                    points += self.regex.findall(row[item])[0]
                points_str += row[item]
        return points,points_str

    def procExcel(self):
        firstIdx = {}
        secondIdx = {}
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
        for index, row in self.df.iterrows():
            # 暂时只给了整数的对应关系 TODO
            # if row['一级知识点'] != '整数':
            #     continue
            # if index == 10:
            #     print(self.outdf.head(10))
            if index == 386:
                print(index)
            # print(index)
            # print(row['Pkid'])
            subject = row['学段名称'] + row['学科名称']
            oL = Dict()
            oL.point_id = line
            if subject_tree.get(subject) == None:
                oL.subject = subjects.get(subject)
                subject_tree[subject] = oL.subject
                # pointCode.reset()
            else:
                oL.subject = subject_tree.get(subject)
            jwyPoints,jwyPoints_str = self.getJywPoints(row)

            if firstIdx.get(row['一级ID']) == None:
                firstIdx[row['一级ID']] = line;
                oL.name = row['一级ID']+'#'+row['一级知识点']
                # if len(row['二级ID']) == 0:  在这儿把该列内容当成float了，没有函数 len
                # if len(row['二级知识点']) == 0:
                # if len(row['二级知识点']) == 0:
                col = row['二级知识点']
                # if col is np.nan or len(col) == 0:
                oL.code = self.pointCode.getCode(oL.name)
                if isNotNull(col) == False:
                    # oL.code = self.pointCode.getCode(oL.name)
                    oL.code_jyw = jwyPoints
                    oL.code_jyw_str = jwyPoints_str
                # else:
                #     oL.code = ''
                oL.order_num = 1
                oL.parent_id = 0
                oL.point_id = line
                line += 1
                # print(type(oL.__dict__))
                # print(oL.__dict__)

                self.outdf = self.outdf.append(oL.__dict__,ignore_index=True)

            if isNotNull(row['二级ID']): #and secondIdx.get(row['二级ID']) == None:
                secondIdx[row['二级ID']] = line;
                oL.name = row['二级ID']+'#'+row['二级知识点']
                # print(type(row['三级ID']))
                # print(row['三级ID'])
                # if len(row['三级ID']) == 0:
                col = row['三级知识点']
                # if col is np.nan or len(col) == 0:
                oL.code = self.pointCode.getCode(oL.name)
                if isNotNull(col) == False:
                    # oL.code = self.pointCode.getCode(oL.name)
                    oL.code_jyw = jwyPoints
                    oL.code_jyw_str = jwyPoints_str
                # else:
                #     oL.code = ''
                oL.order_num = 2
                oL.parent_id = firstIdx.get(row['一级ID'])
                oL.point_id = line
                line += 1
                self.outdf = self.outdf.append(oL.__dict__,ignore_index=True)

            # print(type(row['三级知识点']))
            col = row['三级知识点']
            if col is not np.nan and len(col) > 0:
                oL.name = row['三级ID']+'#'+row['三级知识点']
                oL.code = self.pointCode.getCode(oL.name)
                oL.parent_id = secondIdx[row['二级ID']]
                oL.point_id = line
                # oL.code_jyw = self.cp.getPoints(row['三级ID'])
                oL.code_jyw = jwyPoints
                oL.code_jyw_str = jwyPoints_str
                oL.order_num = 3
                line += 1
                self.outdf = self.outdf.append(oL.__dict__,ignore_index=True)
        self.pointCode.writePoints(self.newPoints)

    def outFile(self):
        # self.outdf.to_excel(self.destinFileName, index=False)
        self.outdf.to_csv(self.destinFileName, sep="\t", index=False)

if __name__ == "__main__":
    # test = dict();
    # print(test.__dict__)
    # list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    # for i in range(0, len(list)):
    #     com_path = os.path.join(rootdir, list[i])
    #     if com_path.endswith('知识点.xlsx'):
    #         ep = ExtractPoints(com_path)
    #         ep.procExcel()
    #         ep.outFile()

    # cp = extractCorrespondingTbl(rootdir+"\小学数学菁优网试题匹配关系.xlsx")
    # cp.readTbl()
    if len(sys.argv) < 2:
        print('用法:\n\t可执行程序名\t待处理课本\t[可选配置文件,没有表示创建]')
        sys.exit(0)

    # ep = ExtractPoints(rootdir+"\小学数学菁优网试题匹配关系.xlsx",rootdir+"\小学数学菁优网试题匹配关系.pot")

    # rootdir =  r'.\data\boll_points'
    # ep = ExtractPoints(rootdir+"\小学+初中数学知识点与菁优网的匹配.xlsx","")
    ep = ExtractPoints(sys.argv[1],"")

    # ep = ExtractPoints(rootdir + "\英语菁优网试题匹配关系.xlsx", "")
    # ep = ExtractPoints(rootdir + "\小学初中语文知识点与菁优网的匹配.xls", "")

    ep.procExcel()
    ep.outFile()

    # file = r".\data\数学知识点.xlsx"
