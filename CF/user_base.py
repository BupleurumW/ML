from math import sqrt  

def loadData(TrainFile,TestFile):
    trainSet = {}  
    testSet = {}  
    movieUser = {}  
    u2u = {}
    itemUser = {}

    #加载训练集  
    for line in open(TrainFile):  
        (userId, itemId, rating) = line.strip().split(',')     
        trainSet.setdefault(userId,{})  
        trainSet[userId].setdefault(itemId,float(rating))  
  
        movieUser.setdefault(itemId,[])  
        movieUser[itemId].append(userId.strip())
        itemUser.setdefault(itemId,{})
        itemUser[itemId].setdefault(userId,float(rating))
    #加载测试集  
    for line in open(TestFile):   
        (userId, itemId, rating) = line.strip().split(',')     
        testSet.setdefault(userId,{})  
        testSet[userId].setdefault(itemId,float(rating))  
  
    #生成用户用户共有矩阵  
    for m in movieUser.keys():  
        for u in movieUser[m]:  
            u2u.setdefault(u,{})  
            for n in movieUser[m]:  
                if u!=n:  
                    u2u[u].setdefault(n,[])  
                    u2u[u][n].append(m)  
    return trainSet,testSet,u2u,itemUser
        
    
  
#计算一个用户的平均评分    
def getAverageRating(user):    
    average = (sum(trainSet[user].values())*1.0) / len(trainSet[user].keys())    
    return average  
  
#计算用户相似度    
def getUserSim(u2u,trainSet):  
    userSim = {}  
    # 计算用户的用户相似度    
    for u in u2u.keys(): #对每个用户u  
        userSim.setdefault(u,{})  #将用户u加入userSim中设为key，该用户对应一个字典  
        average_u_rate = getAverageRating(u)  #获取用户u对电影的平均评分  
        for n in u2u[u].keys():  #对与用户u相关的每个用户n               
            userSim[u].setdefault(n,0)  #将用户n加入用户u的字典中  
  
            average_n_rate = getAverageRating(n)  #获取用户n对电影的平均评分  
                
            part1 = 0  #皮尔逊相关系数的分子部分
            part2 = 0  #皮尔逊相关系数的分母的一部分  
            part3 = 0  #皮尔逊相关系数的分母的一部分  
            for m in u2u[u][n]:  #对用户u和用户n的共有的每个电影    
                part1 += (trainSet[u][m]-average_u_rate)*(trainSet[n][m]-average_n_rate)*1.0    
                part2 += pow(trainSet[u][m]-average_u_rate, 2)*1.0    
                part3 += pow(trainSet[n][m]-average_n_rate, 2)*1.0    
                    
            part2 = sqrt(part2)    
            part3 = sqrt(part3)    
            if part2 == 0 or part3 == 0:  #若分母为0，相似度为0  
                userSim[u][n] = 0  
            else:  
                userSim[u][n] = part1 / (part2 * part3)  
    return userSim

def ItemSimilarity(self, train = None):
    train = train or self.traindata
    itemSim = dict()
    item_user_count = dict() #item_user_count{item: likeCount} the number of users who like the item
    count = dict() #count{i:{j:value}} the number of users who both like item i and j
    for user,item in train.items(): #initialize the user_items{user: items}
        for i in item.keys():
            item_user_count.setdefault(i,0)
            item_user_count[i] += 1
            for j in item.keys():
                count.setdefault(i,{})
                if i == j:
                    continue
                count[i].setdefault(j,0)
                count[i][j] += 1
    for i, related_items in count.items():
        itemSim.setdefault(i,dict())
        for j, cuv in related_items.items():
            itemSim[i].setdefault(j,0)
            itemSim[i][j] = cuv / math.sqrt(item_user_count[i] * item_user_count[j] * 1.0)
    return itemSim
  
#寻找用户最近邻并生成推荐结果  
def getRecommendations(N,trainSet,userSim):  
    pred = {}  
    for user in trainSet.keys():    #对每个用户
        print(user+":")
        pred.setdefault(user,{})    #生成预测空列表  
        interacted_items = trainSet[user].keys() #获取该用户评过分的电影    
        average_u_rate = getAverageRating(user)  #获取该用户的评分平均分  
        userSimSum = 0  
        simUser = (sorted(userSim[user].items(),key = lambda x : x[1],reverse = True))[0:N]
        #print(simUser)
        for n, sim in simUser:
            #print(n,sim)
            average_n_rate = getAverageRating(n)  
            userSimSum += sim   #对该用户近邻用户相似度求和
            #print(userSimSum)
            for m, nrating in trainSet[n].items():    
                if m in interacted_items:
                    continue
                else:  
                    pred[user].setdefault(m,0)  
                    pred[user][m] += (sim * (nrating - average_n_rate))
        for m in pred[user].keys():
            if userSimSum == 0:
                pred[user][m] = -1
            else:
                pred[user][m] = average_u_rate + (pred[user][m]*1.0) / userSimSum  
    return pred

def predict(N,trainSet,testSet,userSim,itemUser):
    pred = {}
    for user in testSet.keys():    #对每个用户
        #print(user+":")
        pred.setdefault(user,{})    #生成预测空列表  
        interacted_items = trainSet[user].keys() #获取该用户评过分的电影    
        average_u_rate = getAverageRating(user)  #获取该用户的评分平均分  
        userSimSum = 0  
        simUser = sorted(userSim[user].items(),key = lambda x : x[1],reverse = True)[0:N]
        #print(simUser)
        flag = 0
        for n, sim in simUser:
            #print(n,sim)
            average_n_rate = getAverageRating(n)  
            userSimSum += sim   #对该用户近邻用户相似度求和
            for item,rating in testSet[user].items():
                for m, nrating in trainSet[user].items():
                    if m==item :
                        pred[user].setdefault(item,0)
                        pred[user][item] += (sim * (nrating - average_n_rate))
                    else:
                        pred[user].setdefault(item, 0)

        for m in pred[user].keys():
            if userSimSum == 0:
                pred[user][m] = -1
            else:
                pred[user][m] = average_u_rate + (pred[user][m]*1.0) / userSimSum

        for item, rating in testSet[user].items():
            if pred[user][item] == 0 or pred[user][item] == -1:
                length = 0;
                for u,r in itemUser[item].items():
                    length += 1
                    pred[user][item] += r
                pred[user][item] = pred[user][item] /length
    return pred
  
#计算预测分析准确度  
def getMAE(testSet,pred):  
    MAE = 0  
    rSum = 0  
    setSum = 0
    for i in testSet.keys():
        setSum += len(testSet[i])
    #print(setSum)
  
    for user in pred.keys():    #对每一个用户  
        for movie, rating in pred[user].items():    #对该用户预测的每一个电影
            #print(user,movie,rating)
            if user in testSet.keys() and movie in testSet[user].keys() :
                print(user,movie,rating,testSet[user][movie])
                rSum = rSum + abs(testSet[user][movie]-rating)      #累计预测评分误差
    MAE = rSum / setSum
    return MAE
  
  
if __name__ == '__main__':
    TrainFile = 'trainingData.txt'  # 指定训练集
    TestFile = 'testData5.txt'  # 指定测试集
    print('正在加载数据...')
    trainSet,testSet,u2u,itemUser = loadData(TrainFile,TestFile)
    
    print('正在计算用户间相似度...')
    userSim = getUserSim(u2u,trainSet)
    #a = dict(userSim.items())
    #print(a.items())
      
    print('正在寻找最近邻...')
    for N in (5,10):            #对不同的近邻数
        #pred = getRecommendations(N,trainSet,userSim)   #获得推荐
        pred = predict(N,trainSet,testSet,userSim,itemUser)
        mae = getMAE(testSet,pred)  #计算MAE
        print('邻居数为：N= %d 时 预测评分准确度为：MAE=%f'%(N,mae))
