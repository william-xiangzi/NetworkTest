#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time
import sqlite3
import threading
from Sys_Info import SystemInfo
from programconfig import Config
from TestLog import log
from Excle_Operation import ExcleDataSave


class BatteryStats(object):
    log = log.log('电量测试')

    @classmethod
    def batterydata(cls):
        level = ''
        temperature = ''
        usbpowered = ''
        # 根据UID获取对应的电量消耗
        battery = os.popen('adb -s %s shell dumpsys battery' % (Config.devices())).readlines()
        # 按行读取电量数据；如果该行存在对应关键字则开始读取 level和temperature 数据
        for output in battery:
            if 'USB powered' in output:
                usbpowered = output.split(":", 1)
                cls.log.debug("设备是否充电 ： %s" % usbpowered[1].split("\n", 1)[0].split(" ", 1)[1])
            if 'level' in output:
                level = output.split(":", 1)
                cls.log.debug("设备当前电量 ： %d" % int(level[1]))
            if 'temperature' in output:
                temperature = output.split(":", 1)
                cls.log.debug("设备当前温度 ： %d" % int(temperature[1]))
        return int(level[1]), int(temperature[1]), usbpowered[1].split("\n", 1)[0].split(" ", 1)[1]

    @classmethod
    def batterystatsdata(cls):
        # 数据 return 顺序：totalbattery, batterycapacity, cpubattery, wifibattery, sensorbattery, camerabattery
        # 防止 battery 文件不能被实时更新；每次写数据前先判断文件是否存在；存在则删除之前文件，不存在则不做操作
        if os.path.exists('./Datafile/log/battery.txt'):
            os.popen('rm -rf ./Datafile/log/battery.txt')
            time.sleep(0.3)
            cls.log.debug("文件 battery.txt 已被成功清除")
        else:
            cls.log.error("文件：battery.txt 不存在")

        # 保存 battery.txt 至脚本本地目录；
        try:
            os.popen('adb -s %s shell dumpsys batterystats >./Datafile/log/battery.txt' % (Config.devices()))
            time.sleep(0.5)
            if os.path.exists('./Datafile/log/battery.txt'):
                cls.log.debug("文件 battery.txt 已成功写入本地")
        except (IOError, Exception):
            cls.log.error("读取电量状态数据错误；battery.txt 存储失败")

        # 获取电池总电量：Capacity
        try:
            time.sleep(0.5)
            cmd = "cat ./Datafile/log/battery.txt |grep -E 'Capacity|capacity'"
            batterycapacity = int(os.popen(cmd).read().split(',', 1)[0].split(" ")[5])
            cls.log.info("电池容量为 %d mAh" % batterycapacity)
        except(IndexError, IOError):
            batterycapacity = 1

        # 电量的详细消耗数据写入 batterystatsdata后按照空格分割；分别读取
        batterystatsdata = os.popen('cat ./Datafile/log/battery.txt |grep Uid|grep %s' % SystemInfo.packageuid()).read().split(" ")
        totalbattery = 0.0
        # 判断UID是否存在；存在的话根据UID读取总体电量消耗 totalbattery
        if SystemInfo.packageuid()+':' in batterystatsdata:
            totalbatteryindex = batterystatsdata.index(SystemInfo.packageuid() + ':')+1
            totalbattery = float(batterystatsdata[totalbatteryindex])
            cls.log.info("当前应用消耗电量 %f" % totalbattery)
            cls.log.info("当前应用消耗电量百分比：%s" % '{:.2%}'.format(totalbattery / batterycapacity))
        else:
            cls.log.error("电量数据不存在 totalbattery=%s" % totalbattery)

        # 判断CPU、WiFi、sensor、camera 是否存在；存在的话则写入，不存在的话则报错
        cpubattery = 0.0
        wifibattery = 0.0
        sensorbattery = 0.0
        camerabattery = 0.0
        for output in batterystatsdata:
            if 'cpu' in output:
                cpubattery = float(output.split('=', 2)[1])
                cls.log.info("当前CPU电量消耗 %f" % cpubattery)

            if 'wifi' in output:
                wifibattery = float(output.split('=', 2)[1])
                cls.log.info("当前WIFI电量消耗 %f" % wifibattery)

            if 'sensor' in output:
                sensorbattery = float(output.split('=', 2)[1])
                cls.log.info("当前硬件电量消耗 %f" % sensorbattery)

            if 'camera' in output:
                camerabattery = float(output.split('=', 2)[1])
                cls.log.info("当前相机电量消耗 %f" % camerabattery)

        # batterycapacity 数据如果取不到时可能会造成问题；目前给默认值1 得到 totalbattery 本身
        batterydict = {'batterycapacity': batterycapacity, 'totalbattery': totalbattery,
                       'percent': '{:.2%}'.format(totalbattery / batterycapacity), 'cpubattery': cpubattery,
                       'wifibattery': wifibattery, 'sensorbattery': sensorbattery, 'camerabattery': camerabattery}
        return batterydict


class BatteryAlgorithm(object):
    os.popen('adb -s %s shell dumpsys batterystats --reset' % (Config.devices()))
    print('电量测试：电量数据已重置')

    # 每隔一段时间统计一次电量;需要传入一个row 值;电量算法存在问题 同理CPU算法同样存在问题 写法中不可以再加等待时间 不然会造成数据抓取不准确
    @classmethod
    def battery_writedata(cls, row, waittime=10):
        battery_detaildata = BatteryStats.batterystatsdata()
        current_power = battery_detaildata['totalbattery']

        time.sleep(waittime)
        battery_sysdata = BatteryStats.batterydata()
        temperature = int(battery_sysdata[1]) // 10
        currenttime = SystemInfo.systime()
        currentactivity = SystemInfo.currentactivity()
        batterycapacity = battery_detaildata['batterycapacity']
        new_power = battery_detaildata['totalbattery']
        power_persecond = new_power - current_power
        batterydata = [currenttime, batterycapacity, currentactivity, temperature, new_power, power_persecond]
        ExcleDataSave.write_batterydata(row=row, batterydata=batterydata)


class BatteryThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'ThreadBatteryData'
        self.stopflag = True
        self.log = log.log('电量测试')

    def run(self, waittime=10):
        self.log.info("开始线程:%s" % self.name)
        bat_writerow = 3
        while self.stopflag:
            try:
                BatteryAlgorithm.battery_writedata(row=bat_writerow, waittime=waittime)
                bat_writerow += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    self.log.info('手动暂停')
                else:
                    self.log.error("电量数据运行出错 重新开始运行")
        self.log.info("结束线程:%s" % self.name)

    def stop(self):
        self.stopflag = False


if __name__ == '__main__':
    BatteryAlgorithm()
    battery_writerow = 3
    while True:
        BatteryAlgorithm.battery_writedata(row=battery_writerow)
        battery_writerow += 1
