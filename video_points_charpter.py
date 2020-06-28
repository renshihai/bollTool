import pandas as pd
import numpy as np
import os
import re
import time
import jieba
import sys
import base64
import json
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

class WkVideo:
    def __init__(self, jsonTbl,grade,subject):
        self.wkUrl = {}
        self.fileExt = ''
        self.notFind = []
        self.readTbl(jsonTbl,grade,subject)

    def readTbl(self, jsonTbl,grade,subject):
        phase = "小学"
        subjectConst = {"语文":"yuwen","英语":"yingyu","数学":"shuxue","物理":"wuli","化学":"huaxue","生物":"shengwu","地理":"dili","历史":"lishi","政治":"zhengzhi"}
        xiaoxue = ["一年级","二年级","三年级","四年级","五年级","六年级"]
        with open(jsonTbl,'r',encoding='utf-8') as f:
            all_sub = json.loads(f.read().replace('\ufeff\n','').replace("\n",""))
            content = all_sub["content"]    # is array
            for item in content:
                if item['subject'].startswith(subjectConst[subject]):
                    # self.wkUrl = item["map"]
                    if grade in xiaoxue:
                        phase = "小学"
                    else:
                        phase = "初中"
                    self.fileExt = item['fileExt']
                    for oneMap in item["map"]:
                        if oneMap["res"].startswith(phase):
                            self.wkUrl.setdefault(oneMap["title"],[]).append(oneMap["res"])

    def getUrl(self, point):
        # pass
        if point in self.wkUrl.keys():
            return self.wkUrl[point]
        else:
            self.notFind.append(point)
            return ""


class Edition:
    def __init__(self):
        # come from: jyw  math
        '''北京出版社
北京师范大学出版社
长春出版社
福建教育出版社
河北教育出版社
湖北教育出版社
湖南教育出版社
湖南少年儿童出版社
江苏凤凰教育出版社
教育科学出版社
接力出版社
科学普及出版社
青岛出版社
清华大学出版社
人民教育出版社
山东教育出版社
山东科学技术出版社
陕西旅游出版社
上海教育出版社
四川教育出版社
外语教学与研究出版社
西南师范大学出版社
译林出版社
语文出版社'''
        self.edition_old={'人教版':'01','北师大版':'02','华师大版':'03','浙教版':'04','湘教版':'05','苏科版':'06','冀教版':'07',
                  '沪科版':'08','北京课改版':'09','鲁教五四版':'10','沪教版':'11','青岛版':'12','人教五四版':'13',
                  '人教新版':'14','北师大新版':'15','华师大新版':'16','苏科新版':'17','湘教新版':'18','青岛新版':'19',
                  '浙教新版':'20','冀教新版':'21','沪科新版':'22','鲁教五四新版':'23','北京课改新版':'24',
                  '沪教新版':'25','人教五四新版':'27'}
        # 以下顺序是跟数据库sys_constant一致的
        self.editionDetail = {'人民教育出版社': '01', '北京师范大学出版社': '02', '北京出版社': '03', '长春出版社': '04', '福建教育出版社': '05',
                        '河北教育出版社': '06', '湖北教育出版社': '07', '湖南教育出版社': '08', '湖南少年儿童出版社': '09', '江苏凤凰教育出版社': '10',
                        '教育科学出版社': '11', '接力出版社': '12', '科学普及出版社': '13', '青岛出版社': '14', '清华大学出版社': '15',
                        '山东教育出版社': '16', '山东科学技术出版社': '17', '陕西旅游出版社': '18', '上海教育出版社': '19', '四川教育出版社': '20',
                        '外语教学与研究出版社': '21', '西南师范大学出版社': '22', '译林出版社': '23', '语文出版社': '24'}
        self.editions = {'人教版': '01', '北师大版': '02', '北京出版社': '03', '长春出版社': '04', '福建教育出版社': '05',
                        '河北教育出版社': '06', '湖北教育出版社': '07', '湖南教育出版社': '08', '湖南少年儿童出版社': '09', '江苏凤凰教育出版社': '10',
                        '教育科学出版社': '11', '接力出版社': '12', '科学普及出版社': '13', '青岛出版社': '14', '清华大学出版社': '15',
                        '山东教育出版社': '16', '山东科学技术出版社': '17', '陕西旅游出版社': '18', '上海教育出版社': '19', '四川教育出版社': '20',
                        '外语教学与研究出版社': '21', '西南师范大学出版社': '22', '译林出版社': '23', '语文出版社': '24'}

        self.grades={'一年级':'01','二年级':'02','三年级':'03','四年级':'04','五年级':'05','六年级':'06','七年级':'07','八年级':'08',
               '九年级':'09','高一':'10','高二':'11','高三':'12'}
        self.subjects={'数学':'0','物理':'1','化学':'2','生物':'3','地理':'5','语文':'6','英语':'7','道法':'8','历史':'9'}
        self.terms= {'上册':'1','下册':'2','全一册':'3'}
        self.scode = ''

    def getEditionCode(self, editiion, grade, subject, term, other):
        e = self.editions.get(editiion)
        gstr = self.grades.get(grade)
        sstr = self.subjects.get(subject)
        t = self.terms.get(term)
        # gint = int(gstr)

        # if gint > 9:
        #     self.scode = '3' + sstr
        # elif gint > 6:
        #     self.scode = '2' + sstr
        # else:
        #     self.scode = '1' + sstr
        self.scode = sstr
        #  科目+教材版本+年级+学期
        return self.scode+e+gstr+t

class VPointCode:
    '''什么是可打印字符？在ASCII码中规定，0~31、127这33个字符属于控制字符，
    32~126这95个字符属于可打印字符，也就是说网络传输只能传输这95个字符，'''
    def __init__(self,vPoints):
        self.BollCode = {}
        self.JywCode = {}
        self.pointsNull = []
        self.BollCodeNum = 0

        if os.path.exists(vPoints):
            self.readPoints(vPoints)

    def readPoints(self,vPoints):
        with open(vPoints, 'r') as file_to_read:
            for line in file_to_read.readlines():
                if line.startswith("最短路径问题"):
                    k = 1
                print(line)
                line = line.replace('\n', '')
                p_tmp = line.split('\t')
                self.BollCode[p_tmp[0][4:]] = p_tmp[0][1:3]
                self.JywCode[p_tmp[0][4:]] = p_tmp[1]
            self.BollCodeNum = len(self.BollCode)

    def getBollCode(self, vpoint):
        if vpoint in self.BollCode.keys():
            return self.BollCode.get(vpoint)
        else:
            self.pointsNull.append(vpoint)
            return ''

    def getJywCode(self, vpoint):
        if vpoint in self.JywCode.keys():
            return self.JywCode.get(vpoint)
        else:
            # self.pointsNull.append(vpoint)
            return ''

class VideoPointsCharpter:
    def __init__(self, excelFile, vPoints, urlFile):
        self.regex = re.compile(r'\[(.*)\]')
        self.tupu = {}  #图谱信息
        self.all_nodes = {} #章节信息
        # self.wkPoints = {}  #
        self.wkNullPointBoll = []
        (path,file) = os.path.split(excelFile)
        (f, ext) = os.path.splitext(excelFile)
        self.destinFileName = os.path.join('',f+'_charpter.txt')
        self.tupuFileName = os.path.join('',f+'_tupu.txt')
        self.jiaocaiFileName = os.path.join('',f+'_book.txt')
        self.cardFileName = os.path.join('',f+'_card.txt')
        self.chkFileName = os.path.join('',f+'.chk')
        self.rule = re.compile('^[A-Z]{1}')
        # 根据文件名获取该书的信息：
        # 人教版七年级数学上册_XXX(知识图谱).xlsx
        result = re.search('_(.*?)[\(\（]', file)
        # 2012年12月第1版2012年12月第1次印刷
        self.update = result.group(1).replace('第','').replace('版','')

        temp = file.split('_')
        ret = jieba.cut(temp[0], cut_all=False)
        xret = "#".join(ret).split('#')
        self.edition = xret[0]
        self.grade = xret[1]
        self.subject = xret[2]
        self.term = xret[3]

        self.ed = Edition()
        self.bookId = self.ed.getEditionCode(self.edition, self.grade, self.subject, self.term, self.update)

        self.dftp = pd.DataFrame(pd.read_excel(excelFile,sheet_name='知识图谱'))
        self.dfkp = pd.DataFrame(pd.read_excel(excelFile,sheet_name='知识卡片'))

        # print(self.dftp.head())
        if '节' in self.dftp.columns:
            self.exsit_section = True
        else:
            self.exsit_section = False
        self.outdf = pd.DataFrame(None,columns=['v_point','points','subject','pointNames'])

        self.pointCode = VPointCode(vPoints)
        self.wkVideo = WkVideo(urlFile, self.grade,self.subject)

    def parseContent(self, content,pattern):
        # pattern =
        result = re.findall(pattern, content)
        return result

    def replaceFormula(self,content):
        constFraction = '''<span class="MathJye" mathtag="math" style="whiteSpace:nowrap;wordSpacing:normal;wordWrap:normal">
        <table cellpadding="-1" cellspacing="-1" style="margin-right:1px">
        <tr><td style="border-bottom:1px solid black">分子</td></tr>
        <tr><td>分母</td></tr></table>
        </span>'''

        fracLst = self.parseContent(content, '\$(.*?)\$')
        for item in fracLst:
            # $frac{35}{100}$
            fraction = self.parseContent(content, '\{.*?\}')
            oneFraction = constFraction.replace("分子",fraction[0]).replace("分母",fraction[1])
            content = content.replace(item, oneFraction)
        # $sqrt{根号下内容}$
        # # $\sqrt[3]{2}$
        return content

    def procKnowledgeCard(self):
        '''<img alt="菁优网" src="data:image/jpeg;base64,'''
        '''分数的处理办法
        <span class="MathJyeSpan">
        <table class="MathJyeTbl">
        <tr><td style="border-bottom:1px solid black">分子</td></tr>
        <tr><td>分母</td></tr></table>
        </span>
        --------------------------------------------------------------------------------------------------
        destination:
        <span class="MathJye" mathtag="math" style="whiteSpace:nowrap;wordSpacing:normal;wordWrap:normal">
        <table cellpadding="-1" cellspacing="-1" style="margin-right:1px">
        <tr><td style="border-bottom:1px solid black">分子</td></tr>
        <tr><td>分母</td></tr></table>
        </span>
        '''
        test ='''掌握有关10的加减法的计算方法，并能正确计算。
1.圆的面积：圆形物体所占平面的大小或圆形物体表面的大小。
2.圆的面积计算公式：如果用S表示圆的面积，r表示圆的半径，那么圆的面积计算公式是：S=πr<sup>2</sup>。

1.百分数的意义
像$frac{30}{100}$、$frac{35}{100}$、$frac{75}{100}$等分母是100的分数，还可以写成30%，50%，75%。像30%，50%，75%…这样的数叫做百分数，表示一个数是另一个数的百分之几。百分数也叫百分比、百分率。

1.达标率是指达标学生的人数占学生总人数的百分之几。达标率的计算公式：达标率＝$frac{达标学生人数}{学生总人数}$×100%。
2.发芽率是指发芽的种子数占实验种子总数的百分之几。种子发芽率的计算公式：发芽率＝$frac{发芽种子数}{实验种子总数学生总人数}$×100%。'''
        # lst = self.parseContent(test, '\$(.*?)\$')

        matchUrl = '"(.*?)"'
        with open(self.cardFileName, "wt") as fcard:
            for index,row in self.dfkp.iterrows():
                klg = row['知识点']
                url = self.wkVideo.getUrl(klg)
                # self.wkPoints[klg] = str(index+1)
                code = self.pointCode.getBollCode(klg)
                jywCode = self.pointCode.getJywCode(klg)

                if len(code) == 0:
                    code = "NONE"
                content = row['【基础须知】'].replace("\n","<br>")
                # 处理分数：
                # fracLst = self.parseContent(content, '\$(.*?)\$')

                # <img url="8和9的组成-001.png">
                imgLst = self.parseContent(content,'<img[^>]*>')
                for item in imgLst:
                    fn = re.search(matchUrl, item).group(0)
                    (path, ext) = os.path.splitext(eval(fn))
                    # fileName = r".\data\video_points_charpter\pic"+"\\"+eval(fn)
                    fileName = r".\data\video_points_charpter\pic"+"\\"+self.edition+"\\"+self.grade+"\\"+self.subject+"\\"+eval(fn)
                    with open(fileName, 'rb') as f:
                        base64_data = base64.b64encode(f.read())
                        content = content.replace(item, "<img src=\"data:image/"+ext[1:]+";base64,"+base64_data.decode()+"\"/>")
                fcard.write(str(index+1)+"\t"+klg+"\t")
                fcard.write(code+"\t"+jywCode+"\t"+self.bookId+"\t"+self.update+"\t")
                fcard.write(content+"\t")
                # fcard.write(json.dumps(url,ensure_ascii=False)+"\n")
                url_tmp = ['{}{}'.format(a, self.wkVideo.fileExt) for a in url]
                fcard.write("#".join(url_tmp)+"\n")

    def getWkCode(self,name):
        lineStr = ''
        if name in self.wkPoints:
            lineStr = self.wkPoints[name]
        else:
            self.wkNullPointBoll.append(name)
        return lineStr

    def getCorrespondRelation(self, src):
        # src = src.replace('<D>',r'",<D>"').replace('<R>',r'",<R>"').replace('<N>',r'","')
        spliteResult = src.split('<')
        # result = []
        result = ""
        lineStr = ''
        for item in spliteResult:
            if len(item):
                # oneItem = {}
                if self.rule.match(item) is None:
                    vname = item
                    # lineStr = self.pointCode.getBollCode(vname,'wk:')
                    # lineStr = self.wkPoints[vname]
                    # lineStr = self.getWkCode(vname)
                    lineStr = self.pointCode.getBollCode(vname)
                else:
                    style = item[0:1]
                    name = item[2:]
                    # lineStr = self.pointCode.getBollCode(name,'wk:')
                    # lineStr = self.getWkCode(name)
                    lineStr = self.pointCode.getBollCode(name)
                    if style == 'N':
                        vname = name
                    else:
                        vname = '<'+style+'>'+name
                # oneItem['name'] = vname
                # oneItem['id'] = lineStr
                if len(result):
                    result += ','
                result += '{"name":"'+vname+'","code":"'+lineStr+'"}'
                # print(str(oneItem))
                # result.append(str(oneItem))
        # print(str(result))
        return '['+result+']'

    def procExcel(self):
        column = ['第一列','第二列','第三列']
        line = 1;
        '''章	第一列	第二列	第三列'''
        charpter =''
        # section = ''
        sectionNode = []
        # if self.exsit_section:
        for index, row in self.dftp.iterrows():
            curCharpter = row['章']
            # curSection = row['节']

            if isNotNull(curCharpter):
                charpter = curCharpter
                self.all_nodes.setdefault(charpter,[])
                if len(sectionNode):
                    self.tupu[line] = sectionNode
                    line += 1
                    sectionNode = []

            if self.exsit_section and isNotNull(row['节']):
                section = row['节']
                # self.all_nodes.setdefault(charpter, []).append(section)
                # oneItem = {}
                # oneItem['Name'] = section
                # oneItem['No'] = str(line)
                # self.all_nodes.setdefault(charpter, []).append(str(line) + ':' + section)
                # self.all_nodes.setdefault(charpter, []).append(oneItem)
                self.all_nodes.setdefault(charpter, []).append(section)
                if len(sectionNode):
                    self.tupu[line] = sectionNode
                    line += 1
                    sectionNode = []

            # knRow = {}
            knRowStr = ''
            if isNotNull(row[column[0]]):
                # knRow["K1"] = self.getCorrespondRelation(row[column[0]])
                knRowStr = '"K1":'+self.getCorrespondRelation(row[column[0]])
            if isNotNull(row[column[1]]):
                # item = self.getCorrespondRelation(row[column[1]])
                # knRow["K2"] = self.getCorrespondRelation(row[column[1]])
                if len(knRowStr):
                    knRowStr += ','
                knRowStr += '"K2":'+self.getCorrespondRelation(row[column[1]])
            if isNotNull(row[column[2]]):
                # item = self.getCorrespondRelation(row[column[2]])
                # knRow["K3"] = self.getCorrespondRelation(row[column[2]])
                if len(knRowStr):
                    knRowStr += ','
                knRowStr += '"K3":'+self.getCorrespondRelation(row[column[2]])
            sectionNode.append('{'+knRowStr+'}')
            # sectionNode.append(json.dumps(knRow,ensure_ascii=False))
            # sectionNode.append(knRow)

    def outFile(self):
        # self.outdf.to_excel(self.destinFileName, index=False)
        # self.outdf.to_csv(self.destinFileName, sep="\t", index=False)
        chkVideoPoints = []
        charpter_list = []
        # 输出错误信息到文件：
        with open(self.chkFileName,"wt") as f:
            if len(self.pointCode.pointsNull):
                f.write("1、注意，下面这些微课的知识点没有对应到菁优网的知识点：请检查：\n")
            for item in self.pointCode.pointsNull:
                f.write("\t"+item+"\n")

            if len(self.wkNullPointBoll):
                f.write("2、注意，下面这些微课的知识点没有对应的知识点卡片：请检查：\n")
            for item in self.wkNullPointBoll:
                f.write("\t"+item+"\n")

            if len(self.wkVideo.notFind):
                f.write("3、注意，下面这些微课的知识点没有对应的微视频：请检查：\n")
            for item in self.wkVideo.notFind:
                f.write("\t"+item+self.wkVideo.fileExt+"\n")

        with open(self.jiaocaiFileName, "w+") as f:
            f.write(self.bookId + "\t")
            f.write(self.update + "\t")
            f.write(self.edition+self.grade+self.subject+self.term+self.update + "\t")
            f.write(self.ed.editions.get(self.edition) + "\t"+self.edition+"\t")
            f.write(self.ed.grades.get(self.grade) + "\t"+self.grade+"\t")
            f.write(self.ed.terms.get(self.term) + "\t"+self.term+"\t")
            f.write(self.ed.scode + "\t"+self.subject+"\t")
            f.write("\n")

        with open(self.destinFileName, "wt") as f:
            line = 1;
            for key, value in self.all_nodes.items():
                oneCharpter = {}
                oneCharpter["Name"] = key
                if len(value) == 0:
                    oneCharpter["No"] = line
                    line += 1
                else:
                    section = []
                    for itm in value:
                        node = {}
                        node["Name"] = itm
                        node["No"] = line
                        line += 1
                        section.append(node)
                    oneCharpter["Child"] = section
                charpter_list.append(oneCharpter)
            print(str(charpter_list))
            f.write(self.bookId+"\t"+self.update+"\t")
            f.write(json.dumps(charpter_list,ensure_ascii=False))

        with open(self.tupuFileName, "wt") as f:
            for key, value in self.tupu.items():
                xxx = ''
                for kitem in value:
                    if len(xxx):
                        xxx += ','
                    xxx += kitem
                f.write(str(key)+"\t"+self.bookId+"\t"+self.update+"\t["+xxx+"]\n")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('用法:\n\t可执行程序名\t输入文件\t配置文件')
        print('说明:\n\t输入文件：待处理知识图谱文件\n\t配置文件:内容为我们微课知识点编码')
        sys.exit(0)

    # src = '人教版七年级数学上册_2014.1.1(知识图谱).xlsx'
    # result = re.search('_(.*?)\(',src)
    # print(result.group(1))
    # ep = VideoPointsCharpter("\知识图谱_源数据_sample.xlsx",r'.\data\boll_points\小学数学菁优网试题匹配关系.pot')
    '''
    d:\proj\python\bollTools\data\video_points_charpter\人教版一年级数学上册_2014.10.02（知识图谱知识卡片）.xlsx  d:\proj\python\bollTools\data\video_points\知识点与微课的匹配关系\数学知识点对应微课5.26.csv
    d:\proj\python\bollTools\data\video_points_charpter\人教版七年级数学上册_XXX(知识图谱).xlsx  d:\proj\python\bollTools\data\video_points\知识点与微课的匹配关系\数学知识点对应微课5.26.csv
    d:\proj\python\bollTools\data\kn_config_tbl.json 
    
    '''
    ep = VideoPointsCharpter(sys.argv[1],sys.argv[2],r"d:\proj\python\bollTools\data\kn_config_tbl.json")
    # ep.pointCode = VPointCode(sys.argv[2])
    # ep.wkVideo = WkVideo(r"d:\proj\python\bollTools\data\kn_config_tbl.json", ep.grade,ep.subject)
    ep.procKnowledgeCard()
    ep.procExcel()
    ep.outFile()

