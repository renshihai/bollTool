import pandas as pd
import os
import sys
import time
import Edition as ed
import constant as cst
import shutil
'''
试题ID编号：
    bookId + 年月日+XXXX
图片重新命名：
    time.suffix
图片格式：
    <img src="/i/eg_tulip.jpg"/>
图片目录：
    uuid/
输出：
文件1：期中测试、期末测试
文件2：试题内容.txt
'''
cst.FUN_CHARPTER = 1
cst.FUN_TEST     = 2
cst.FUN_QUESTION = 3
cst.Q   = 4
cst.A   = 5
cst.E   = 6
cst.K   = 7
cst.O   = 8 # virtual option:

def isNotNull(col):
    if (pd.isnull(col)):
        return False
    else:
        print(type(col))
        if isinstance(col,int) or len(col.strip()):
            return True
        else:
            return False

class Question:
    def __init__(self,bk_uuid,cur_date, quesNo):
        self.cate = 0
        self.origin = ''
        self.tg = []
        self.options = []
        self.answer = []
        self.key = []
        self.keyCode = []
        self.explain = []

        self.id = bk_uuid+cur_date+str(quesNo).zfill(4)

    def pictureName(self):
        pass

class ExtractQues:
    def __init__(self, inputFile, wkCodeFile):
        self.ed = ed.Edition()
        # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.date = time.strftime("%Y%m%d", time.localtime())
        # $$6	期中测试
        # $$6	期末测试
        self.quesNo = 1
        self.pictNo = 1
        self.curent = ''
        self.need = ['期中测试', '期末测试']
        self.picture = {}

        self.inputFile = inputFile
        # (path1,fileName) = os.path.split(inputFile)
        (path,ext) = os.path.splitext(inputFile)
        self.outputFile = path + '.txt'
        (self.grade,self.subject,self.edition, self.term) = self.ed.jiebaSplit(path)
        self.bk_uuid = self.ed.getEditionCode_Ques(self.edition,self.grade,self.subject, self.term)
        (path,file) = os.path.split(inputFile)
        self.srcPicPath = os.path.join(path,'pic')
        self.destPicPath = os.path.join(path, self.bk_uuid)
        self.outf = open(self.outputFile,"wt")
        if not os.path.exists(self.destPicPath):
            os.mkdir(self.destPicPath)

        self.df = pd.DataFrame(pd.read_excel(inputFile,sheet_name="试题",header=None,converters={"1"})) #names=['1','2','3','4','5','6','7','8','9','10','11','12']))
        # print(type(self.df.size))
        self.column = self.df.shape[1]
        self.BollCode = {}
        self.readWkCode(wkCodeFile)

    def readWkCode(self,wkCodeFile):
        # tdf = pd.DataFrame(pd.read_excel(wkCodeFile))
        with open(wkCodeFile, 'r') as file_to_read:
            for line in file_to_read.readlines():
                if line.startswith("最短路径问题"):
                    k = 1
                # print(line)
                line = line.replace('\n', '')
                p_tmp = line.split('\t')[0]
                self.BollCode[p_tmp[4:]] = p_tmp[1:3]
                # self.JywCode[p_tmp[0][4:]] = p_tmp[1]
            self.BollCodeNum = len(self.BollCode)
        pass

    def judgeStyle(self,row):
        test=['$$6','$$5']
        question = ['$$13','$$15']
        fun = None

        # print(type(row))
        for index in range(len(row)):
            item = row[index]
            if isNotNull(item):
                if item == '$$$':
                    fun = cst.FUN_CHARPTER
                elif item in test:
                    fun = cst.FUN_TEST
                    # detail = row[index+1]
                elif item in question:
                    fun = cst.FUN_QUESTION
                elif item == '$$Q':
                    fun = cst.Q
                elif item == '$$A':
                    fun = cst.A
                elif item == '$$E':
                    fun = cst.E
                elif item == '$$K':
                    fun = cst.K
                # if fun != None:
                return (fun, index)

    def procPic(self, pic, isAdd):
        (path, ext) = os.path.splitext(pic)
        src = os.path.join(self.srcPicPath, pic)
        dest = os.path.join(self.destPicPath, self.date+str(self.pictNo)+ext)
        shutil.copy(src,dest)
        name = os.path.join(self.bk_uuid,self.date+str(self.pictNo)+ext)
        self.picture[pic] = name
        self.pictNo += 1
        if isAdd:
            return '<img src="'+name+'">'
        else:
            return '<img tp="c" src="'+name+'">'

    # self.tg = []
    # self.options = []
    # self.answer = []
    # self.key = []
    # self.keyCode = []
    # self.explain = []
    def output(self,ques):
        self.outf.write(ques.id + "\t" + str(ques.cate) + "\t"
                        + "".join(ques.tg) + "\t" + ques.origin + "\t" + "<@#$>".join(ques.options) + "\t"
                        + "<@#$>".join(ques.answer) + "\t" + "<@#$>".join(ques.key) + "\t"+"<br>".join(ques.explain)+"\n")

    def procExcl(self):
        # print(self.df.iloc[0,1])
        old_fun = None
        detailTest = None
        origin = None
        isAdd = False
        ques = None

        for index,row in self.df.iterrows():
            print(index)
            if index == 24:
                index = index
            (fun, posi) = self.judgeStyle(row)
            if fun == cst.FUN_CHARPTER:
                pass
            elif fun == cst.FUN_QUESTION:
                pass
            elif fun == cst.FUN_TEST:
                origin = row[posi+1]
            elif fun == None:
                if row[posi+3] == 'PIC':
                    newPicName = self.procPic(row[posi],isAdd)
                    if old_fun == cst.Q:
                        if row[posi+1] == '^' and ques.cate == 2:
                            old_fun = cst.O
                        ques.tg.append(newPicName)
                    elif old_fun == cst.O:
                        ques.options.append(newPicName)
                    elif old_fun == cst.E:
                        ques.explain.append(newPicName)
                    elif old_fun == cst.A:
                        ques.answer.append(newPicName)
                    elif old_fun == cst.K:
                        ques.key.append(newPicName)
                else:
                    if not isAdd:
                        cont = '<br>'+str(row[posi])
                    else:
                        cont = str(row[posi+1])

                    if old_fun == cst.Q:
                        if row[posi+1] == '^' and ques.cate == 2:
                            old_fun = cst.O
                        ques.tg.append(cont)
                    elif old_fun == cst.O:
                        ques.options.append(cont)
                    elif old_fun == cst.E:
                        ques.explain.append(cont)
                    elif old_fun == cst.A:
                        ques.answer.append(cont)
                    elif old_fun == cst.K:
                        ques.key.append(cont)

                if row[posi+1] == '+':
                    isAdd = True
                else:
                    isAdd = False
            else:
                # if row[posi+3] == 'PIC':
                #     newPicName = self.procPic(row[posi],isAdd)

                if fun == cst.Q:
                    if ques != None:
                        self.output(ques)
                    # 生成题目ID
                    ques = Question(self.bk_uuid, self.date, self.quesNo)
                    ques.origin = origin
                    self.quesNo += 1

                    if row[posi+5] == 'PIC':
                        pass
                    ques.tg.append(row[posi+2])

                    ques.cate = int(row[posi+1])
                    if row[posi+3] == '^' and ques.cate == 2:
                        fun = cst.O
                elif fun == cst.E:
                    ques.explain.append(row[posi + 2])
                elif fun == cst.A:
                    ques.answer.append(row[posi + 2])
                elif fun == cst.K:
                    ques.key.append(row[posi + 2])

                if row[posi+3] == '+':
                    isAdd = True
                else:
                    isAdd = False
                old_fun = fun
        self.output(ques)
        self.outf.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('用法:\n\t可执行程序名\t输入文件\t知识点编码文件')
        print('说明:\n\t输入文件：待处理试题文件\n')
        sys.exit(0)
    #     e:\proj\data\tbj_excel源数据\八年级数学人教新课标上册\八年级数学人教新课标上册.xls  d:\proj\python\bollTools\data\video_points\知识点与微课的匹配关系\数学知识点对应微课5.26.csv
    # print(sys.argv[1])
    eq = ExtractQues(sys.argv[1],sys.argv[2])
    eq.procExcl()