# -*- coding: utf-8 -*-
import math
class UserBasedCF:
    def __init__(self, datafile=None):  # 构造函数初始化
        self.readData(datafile=datafile)  # 载入数据
        self.cacheData()

    def readData(self, datafile=None):
        data = []
        for line in open(datafile):
            userid, itemid, record = line.strip('\n').split(",")
            data.append((userid, itemid, float(record)))  # data列表存储用户id,电影id,得分
        self.data = data
        return data

    def cacheData(self):
        self.userItemScore = dict()  # {用户：{电影1：评分，电影2：评分2}}
        self.user_items = dict()  # {用户：set(看过的电影集合)}
        self.item_users = dict()  # {电影：set(看过该电影的用户集合)}
        # 仅仅遍历一次数据，形成三个中间结果查询字典
        for user, item, rate in self.data:
            if user not in self.userItemScore:
                self.userItemScore.setdefault(user, {})
            self.userItemScore[user][item] = int(rate)
            if item not in self.item_users:
                self.item_users.setdefault(item, set())
            self.item_users[item].add(user)
            if user not in self.user_items:
                self.user_items.setdefault(user, set())
            self.user_items[user].add(item)
        '''
        #寻找hotmovie
        hotmovie={}
        for i in self.item_users.keys():
            hotmovie.setdefault(i,len(self.item_users[i]))
        self.hotmovie=sorted(hotmovie.items(),key = lambda x : x[1],reverse = True)[0:20]
        print self.hotmovie
        '''

    def itemSimBest(self, targetMovie, k):  # 设置目标电影，与返回的最相似电影个数
        self.targetMovie = targetMovie
        # 计算每个targetmovie以外的电影与movie的相似度
        simmj = dict()  # 存电影m与j的相似度
        for j in self.item_users.keys():  # j为所有电影
            if j == targetMovie:
                continue
            umj = self.item_users[targetMovie] & self.item_users[j]  # 同时评论过电影mj的用户集合(交集)
            # print(self.item_users[targetMovie])
            # print(self.item_users[j])
            # print("umj:")
            # print(umj)
            if umj == set([]): continue  # 如果没有用户共同评论电影mj则跳出本次循环
            # 中间结果计算，计算umj中每个用户给出评分的平均值
            umjj = dict()  # umjj存对电影mj同时进行过评论的用户的平均分
            for u in umj:
                ucum = 0
                for i in self.userItemScore[u].items():
                    ucum += float(i[1])  # 所有电影得分相加
                umean = ucum / len(self.userItemScore[u])  # 该用户评分总分/评论的电影数
                umjj[u] = umean  # 用户评分平均分，加入字典
                # print(str(u)+":"+str(umjj[u]))
            # print(umjj)#与u共同评论了mj电影的用户v有····他们各自的平均评分为   {'75': 3.92, '92': 2.8545454545454545}
            # 对相似度计算的分子
            fenzi = fenmu1 = fenmu2 = 0
            for v in umj:  # i为用户
                fenzi += (self.userItemScore[v][targetMovie] - umjj[v]) * (self.userItemScore[v][j] - umjj[v])
                fenmu1 += pow(self.userItemScore[v][targetMovie] - umjj[v], 2)
                fenmu2 += pow(self.userItemScore[v][j] - umjj[v], 2)
            if fenmu1 * fenmu2 == 0:
                simmj[j] = 0
            else:
                sim = fenzi / (math.sqrt(fenmu1) * math.sqrt(fenmu2))
                simmj[j] = sim  # m与j项目相似度为sim
        # 字典排序，取出与m最相似的k个电影
        simmj = sorted(simmj.items(), key=lambda x: x[1], reverse=True)
        # print(simmj)
        # if len(simmj) < max(k):
        #     print("K值不能大于simmmj集合的元素个数————simmj集合的个数为" + str((len(simmj))))
        # simmjkDict = {}  # 存放不同k值，对应的最相似电影集合
        # for i in k:
        simmjkDict = dict(simmj[0:k])
        return simmjkDict

    def userSimBest(self, simmjkDict, simk=0.00001):
        # print("simmjkDict:")
        # print(simmjkDict)
        self.rightSimTargetuuDict = {}  # 符合条件的目标用户与其多个相似用户的相似值
        # for key in simmjkDict.keys():  # key就是topk这个列表
        simmjk = simmjkDict#[key]
        # print("simmjk:")
        # print(simmjk)
        simmjk = set(simmjk.keys())  # 准备ci
        #print(simmjk)
        userm = list(self.item_users[self.targetMovie])  # 获取评论过目标电影的用户集合
        rightSimTargetuu = {}  # 有的tagetu的ci为空集，所以需要找到ci不为空集的targetu结果如图
        for targetu in userm:  # 找到符合条件的targetu
            simtargetuu = {}  # 找到与tagetu最相似的几个用户
            for u in userm:  # 评论过目标电影的集合
                if targetu == u:
                    continue
                ci = self.user_items[targetu] & self.user_items[u] & simmjk
                # print("ci:")
                # print(ci)
                if len(ci) > 0:
                    cum = 0.0
                    for a in ci:
                        cum += pow((self.userItemScore[targetu][a] - self.userItemScore[u][a]), 2)
                    simtargetuu[u] = 1.0 - (cum * 1.0) / len(ci)
                    # print("simtargetuu[u]:")
                    # print(simtargetuu[u])
            if len(simtargetuu) != 0:
                rightSimTargetuu[targetu] = simtargetuu
        # print("rightSimTargetuu1:")
        # print(rightSimTargetuu)
        # print rightSimTargetuu
        # 因为ci设置过小，会使得有的用户相似度计算结果为负或者0这种相似度值当然不适合预测，所以需要去除奇异值
        for u in rightSimTargetuu.keys():
            for v in list(rightSimTargetuu[u]):
                # for v in rightSimTargetuu[u].keys():
                if rightSimTargetuu[u][v] < simk:
                    del rightSimTargetuu[u][v]  # 设定相似度阈值
        for u in list(rightSimTargetuu):  # 删除{‘151’：{}}这样的空值
            if rightSimTargetuu[u] == {}:
                del rightSimTargetuu[u]
        # print 'del sim dic'
        # print rightSimTargetuu
        # self.rightSimTargetuu=rightSimTargetuu
        # print("rightSimTargetuu:")
        # print(rightSimTargetuu)
        if len(rightSimTargetuu) == 0:
            print("没有匹配的相似用户，需要降低相似度阈值or增加K or 改变目标电影")
            return 0
        self.rightSimTargetuuDict = rightSimTargetuu

    def predictAndEvaluation(self):
        m = self.targetMovie
        K_MAE_Dict = {}
        # for key in self.rightSimTargetuuDict.keys():# rightSimTargetuuDict:存放不同K值下，符合条件的目标用户与其多个相似用户的相似值
        rightSimTargetuu = self.rightSimTargetuuDict#[key]
        # print(rightSimTargetuu)
        predictTargetScore = {}
        for u in rightSimTargetuu.keys():
            fenzi = fenmu = 0.0
            for v in rightSimTargetuu[u].keys():
                fenzi += rightSimTargetuu[u][v] * self.userItemScore[v][m]
                fenmu += rightSimTargetuu[u][v]

            predictTargetScore[u] = fenzi * 1.0 / fenmu
            # test result
        cum = 0.0
        rating = 0.0
        for i in predictTargetScore.keys():
            cum += predictTargetScore[i]
        if len(predictTargetScore.keys()) == 0:
            length = 0
            for u, r in self.userItemScore[self.targetMovie].items():
                length += 1
                rating += r
            rating = rating / length
        else:
            rating = cum / len(predictTargetScore.keys())
        if rating > math.floor(rating) + 0.5:
            rating = math.ceil(rating)
        else:
            rating = math.floor(rating)
        return rating

def readTestSet(testfile):
    data = []
    for line in open(testfile):
        userid, itemid, record = line.strip('\n').split(",")
        data.append((userid, itemid, float(record)))
    return data

def testModel():
    trainfile = "trainingData.txt"
    testfile = "testData4.txt"
    cf = UserBasedCF(trainfile)
    testSet = readTestSet(testfile)
    print("正在测试"+testfile+"...")
    MAE = 0
    setSum = len(testSet)
    length = setSum
    # print(testSet)
    for user,item,rating in testSet:
        simmjkDict = cf.itemSimBest(targetMovie=item, k=200)  # 求目标电影的K-Top个最相似电影
        flag = cf.userSimBest(simmjkDict, simk=0.00001)  # simk为用户相似度的阈值。根据你的相似度计算公式，用户相似度值大于0，即相似度很高，不建议修改该默认阈值
        if(flag == 0):
            setSum -= 1
            continue
        predict = cf.predictAndEvaluation()
        print(user,item,rating,predict)
        MAE += abs(predict - rating)
    # print(setSum)
    MAE = MAE / setSum
    coverage = setSum/length
    print("MAE:"+str(MAE))
    print("coverage:" + str(coverage))

if __name__ == "__main__":
    testModel()
