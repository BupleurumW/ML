def dealdata(filename):
    # 从数据集中获得原始数据
    adult_raw = pd.read_csv(filename, header=None)
    # print(len(adult_raw))
    # 添加标题
    adult_raw.rename(columns={0: 'age', 1: 'workclass', 2: 'fnlwgt', 3: 'education', 4: 'education_number',
                              5: 'marriage', 6: 'occupation', 7: 'relationship', 8: 'race', 9: 'sex',
                              10: 'capital_gain', 11: 'apital_loss', 12: 'hours_per_week', 13: 'native_country',
                              14: 'income'}, inplace=True)
    # 清理数据，删除缺失值
    adult_cleaned = adult_raw.dropna()

    # 属性数字化
    adult_digitization = pd.DataFrame()
    target_columns = ['workclass', 'education', 'marriage', 'occupation', 'relationship', 'race', 'sex',
                      'native_country',
                      'income'] #需要数字化的列名
    for column in adult_cleaned.columns:
        if column in target_columns:
            unique_value = list(enumerate(np.unique(adult_cleaned[column])))
            dict_data = {key: value for value, key in unique_value} # 转换成字典：{属性：index}
            adult_digitization[column] = adult_cleaned[column].map(dict_data)#获取属性的index
        else:
            adult_digitization[column] = adult_cleaned[column]
    adult_digitization.to_csv("data_cleaned.csv", index=None)