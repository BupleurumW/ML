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
            data.append((userid, itemid, float(record)))  # data列表存储用户id,物品id,得分
        self.data = data
        return data

    def cacheData(self):
        self.userItemScore = dict()  # {用户：{物品1：评分，物品2：评分2}}
        self.user_items = dict()  # {用户：set(看过的物品集合)}
        self.item_users = dict()  # {物品：set(看过该物品的用户集合)}
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

    def itemSimBest(self, targetMovie, k):  # 设置目标物品，与返回的最相似物品个数
        self.targetMovie = targetMovie
        # 计算每个targetmovie以外的物品与movie的相似度
        simmj = dict()  # 存物品m与j的相似度
        for j in self.item_users.keys():  # j为所有物品
            if j == targetMovie:
                continue
            umj = self.item_users[targetMovie] & self.item_users[j]  # 同时评论过目标物品和物品j的用户交集
            if umj == set([]): continue  # 如果没有用户共同评论物品j和目标物品则跳出本次循环
            # 中间结果计算，计算umj中每个用户给出评分的平均值
            umjj = dict()  # umjj存对物品mj同时进行过评论的用户的平均分
            for u in umj:
                ucum = 0
                for i in self.userItemScore[u].items():
                    ucum += float(i[1])  # 所有物品得分相加
                umean = ucum / len(self.userItemScore[u])  # 该用户评分总分/评论的物品数
                umjj[u] = umean  # 用户评分平均分
            # 对相似度计算
            child = mother1 = mother2 = 0
            for v in umj:  # i为用户
                child += (self.userItemScore[v][targetMovie] - umjj[v]) * (self.userItemScore[v][j] - umjj[v])
                mother1 += pow(self.userItemScore[v][targetMovie] - umjj[v], 2)
                mother2 += pow(self.userItemScore[v][j] - umjj[v], 2)
            if mother1 * mother2 == 0:
                simmj[j] = 0
            else:
                sim = child / (math.sqrt(mother1) * math.sqrt(mother2))
                simmj[j] = sim  # m与j项目相似度为sim
        # 字典排序，取出与m最相似的k个物品
        simmj = sorted(simmj.items(), key=lambda x: x[1], reverse=True)
        simmjkDict = dict(simmj[0:k])
        return simmjkDict

    def userSimBest(self, simmjkDict, simk=0.00001):
        self.rightSimTargetuuDict = {}  # 符合条件的目标用户与其多个相似用户的相似值
        simmjk = simmjkDict
        simmjk = set(simmjk.keys())  # 准备ci
        userm = list(self.item_users[self.targetMovie])  # 获取评论过目标物品的用户集合
        rightSimTargetuu = {}  # 有的tagetu的ci为空集，所以需要找到ci不为空集的targetu
        for targetu in userm:  # 找到符合条件的targetu
            simtargetuu = {}  # 找到与tagetu最相似的几个用户
            for u in userm:  # 评论过目标物品的集合
                if targetu == u:
                    continue
                ci = self.user_items[targetu] & self.user_items[u] & simmjk
                if len(ci) > 0:
                    cum = 0.0
                    for a in ci:
                        cum += pow((self.userItemScore[targetu][a] - self.userItemScore[u][a]), 2)
                    simtargetuu[u] = 1.0 - (cum * 1.0) / len(ci)
            if len(simtargetuu) != 0:
                rightSimTargetuu[targetu] = simtargetuu
        # 因为ci设置过小，会使得有的用户相似度计算结果为负或者0这种相似度值当然不适合预测，所以需要去除奇异值
        for u in rightSimTargetuu.keys():
            for v in list(rightSimTargetuu[u]):
                if rightSimTargetuu[u][v] < simk:
                    del rightSimTargetuu[u][v]  # 设定相似度阈值
        for u in list(rightSimTargetuu):
            if rightSimTargetuu[u] == {}:
                del rightSimTargetuu[u]
        if len(rightSimTargetuu) == 0:
            # print("没有匹配的相似用户，需要降低相似度阈值or增加K or 改变目标物品")
            return 0
        self.rightSimTargetuuDict = rightSimTargetuu

    def predictAndEvaluation(self):
        m = self.targetMovie
        rightSimTargetuu = self.rightSimTargetuuDict
        predictTargetScore = {}
        for u in rightSimTargetuu.keys():
            child = mother = 0.0
            for v in rightSimTargetuu[u].keys():
                child += rightSimTargetuu[u][v] * self.userItemScore[v][m]
                mother += rightSimTargetuu[u][v]

            predictTargetScore[u] = child * 1.0 / mother

        cum = 0.0
        rating = 0.0
        for i in predictTargetScore.keys():
            cum += predictTargetScore[i]
        if len(predictTargetScore.keys()) == 0:
            print("没找到")
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
    # testfile = ["testData1.txt","testData2.txt","testData3.txt","testData4.txt","testData5.txt"]
    testfile = "testData5.txt"
    cf = UserBasedCF(trainfile)
    print("正在测试" + testfile + "...")
    MAE = [0,0,0,0,0,0,0]
    coverage = [0,0,0,0,0,0,0]
    # l = len(testfile)
    k = [100,125,150,180,200,220,250]
    l = len(k)
    for i in range(l):
        testSet = readTestSet(testfile)
        # print("正在测试"+testfile+"...")
        setSum = len(testSet)
        length = setSum
        # print(testSet)
        for user,item,rating in testSet:
            simmjkDict = cf.itemSimBest(targetMovie=item, k=k[i])  # 求目标物品的K-Top个最相似物品
            flag = cf.userSimBest(simmjkDict, simk=0.00001)  # simk为用户相似度的阈值
            if(flag == 0):
                setSum -= 1
                continue
            predict = cf.predictAndEvaluation()
            # print(user,item,rating,predict)
            MAE[i] += abs(predict - rating)
        # print(setSum)
        MAE[i] = MAE[i] / setSum
        coverage[i] = setSum/length
        # print("K = "+str(k[i])+"时：")
        # print("MAE:"+str(MAE[i]))
        # print("coverage:" + str(coverage[i]))
    print(k)
    print(MAE)
    print(coverage)
    # f = open('5.txt', 'w')
    # f.write(str(k))
    # f.write("\n")
    # f.write(str(MAE))
    # f.write("\n")
    # f.write(str(coverage))
    # f.close()

if __name__ == "__main__":
    testModel()
