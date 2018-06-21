#-*- coding: utf-8 -*-
# 绘制结果图
import matplotlib.pyplot as plt
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['SimHei']

k = [100, 125, 150, 180, 200, 220, 250]
MAE = [0.8878348214285714, 0.8797434526990914, 0.859538784067086, 0.8442708333333333, 0.8296875, 0.8348958333333333, 0.8375]
coverage = [0.9294605809128631, 0.9704356846473029, 0.9896265560165975, 0.995850622406639, 0.995850622406639, 0.995850622406639, 0.995850622406639]

x = range(len(k))
y = MAE
y1 = coverage
# plt.plot(x, y, marker='o', mec='r', mfc='w', label=u'MAE')
# # plt.ylim(0.82, 0.89)
plt.plot(x, y1, marker='*', ms=10, label=u'coverage')
plt.ylim(0.9, 0.999999999)
plt.legend()  # 让图例生效
plt.xticks(x, k, rotation=45)
plt.margins(0)
plt.subplots_adjust(bottom=0.15)
plt.xlabel(u"选取的相似电影数")  # X轴标签
plt.ylabel(u"测试值")  # Y轴标签
plt.title("testData5")  # 标题
plt.show()
# plt.savefig("1.png")  # 保存图