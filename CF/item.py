from item_based import Item_based_CF

def data_read():
    test = "testData5.txt"
    train = "trainingData.txt"
    train_X = []
    test_X = []
    with open(test, 'r') as f:
        lines = f.readlines()
        for each in lines:
            p = each.split(',')
            new = [int(p[0]), int(p[1]), int(p[2])]
            test_X.append(new)

    with open(train, 'r') as f:
        lines = f.readlines()
        for each in lines:
            p = each.split(',')
            new = [int(p[0]), int(p[1]), int(p[2])]
            train_X.append(new)

    return train_X,test_X
#
train_X,test_X=data_read()
a=Item_based_CF(train_X)
a.test(test_X)
