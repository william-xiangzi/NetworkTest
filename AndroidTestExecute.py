#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# 性能测试思路：可以不用 while True: 让用例一直运行的方法；可以采用轮训 即每个1秒采集一次数据 写一次
# 这样的话可也以使用多线程 即让用例一直执行 知道接收到一个外部命令即停止；此方法 可以不使用 while True 实现；可以使用线程退出实现
import threading
import time
from Excle_Operation import ExcleDataSave
from FpsData import Activitymonitor
from CpuData import Cpu
from BatteryDate import BatteryAlgorithm
from NetData import PackNetData
from MemData import MemoryWrite


class FpsThread (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        Activitymonitor.monitor()
        print("退出线程：" + self.name)


class MemThread (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        MemoryWrite.memaction()
        print("退出线程：" + self.name)


class CpuThread (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        Cpu.data()
        print("退出线程：" + self.name)


class BatteryThread (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        row = 3
        while True:
            BatteryAlgorithm.battery_writedata(row=row)
            row += 1


class NetThread (threading.Thread):

    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        try:
            test = PackNetData().datawrite()
        except IOError:
            print('excle must be save')
        print("退出线程：" + self.name)


threadcpu = CpuThread(1, "threadcpu")
threadfps = FpsThread(2, "threadfps")
threadbattery = BatteryThread(3, "threadbattery")
threadnet = NetThread(4, "thrednet")
threadmem = MemThread(5, 'threadmem')


if __name__ == "__main__":
    ExcleDataSave.createxcle()
    ExcleDataSave.creat_cputable()
    ExcleDataSave.creat_memtable()
    ExcleDataSave.creat_nettable()
    ExcleDataSave.creat_batterytable()
    ExcleDataSave.creat_fpstable()
    time.sleep(2)

    threadbattery.start()  # 电量数据采集时间较长 所以放在最先运行
    threadmem.start()  # 内存数据同理 放在第二位执行
    threadcpu.start()  # Cpu 数据采集实时 可以放在任何位置
    threadnet.start()
    threadfps.start()
