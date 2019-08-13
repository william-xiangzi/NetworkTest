#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time
import threading
from Excle_Operation import ExcleDataSave
from programconfig import Config
from TestLog import log


class PackNetData(object):
    log = log.log('流量测试')

    # 读取数据的方法；最后输出 rx_packagenetdata 接收、下行数据的总和 ；tx_packagenetdata 发送、上行数据 的总和;
    # 并且记录数据读取的时间 self.datatime；需要获取对应数据时需要先执行此方法
    # 目前此方法不足是 无法从外部获取对应数据总和；优化方法 需要把数据写到 return里
    # 暂时：如果要获取 上行和下行数据 需要先调用此方法
    @classmethod
    def dataread(cls):
        # 根据包名 获取到包对应的 UID
        packageuid = int(os.popen('adb -s %s shell ps |grep %s' % (Config.devices(), Config.packagename()))
                         .read().split(" ")[0].split('a', 1)[1]) + 10000
        cls.log.debug("packageuid = %d" % packageuid)
        # 根据包对应UID 找到对应的网络数据；并且读取出来用字符串分割方法按行分割；
        packagenetdata = os.popen('adb -s %s shell cat /proc/net/xt_qtaguid/stats |grep %d'
                                  % (Config.devices(), packageuid)).read().splitlines()
        tx_packagenetdata = 0
        rx_packagenetdata = 0
        for dataread in packagenetdata:
            packnetdata = dataread.split(" ")
            if (int(packnetdata[3]) == packageuid) and (packnetdata[1] == 'wlan0'):
                cls.log.debug(packnetdata)
                tx_packagenetdata += int(packnetdata[7])
                rx_packagenetdata += int(packnetdata[5])
        return [tx_packagenetdata, rx_packagenetdata]

    # 把读取写入 excle；rx_packagenetdata 接收、下行数据的总和 ；tx_packagenetdata 发送、上行数据 的总和;
    @classmethod
    def datawrite(cls, writeexcle_row=3, waittime=2):
        old_txnetdata = PackNetData.dataread()[0]
        old_rxnetdata = PackNetData.dataread()[1]
        time.sleep(waittime)
        currenttime = time.strftime('%H%:%M:%S', time.localtime(time.time()))
        new_txnetdata = PackNetData.dataread()[0]
        new_rxnetdata = PackNetData.dataread()[1]
        # tx_sec_data 上行数据 rx_sec_data 下行数据
        tx_sec_data = '{:.2f}'.format((new_txnetdata - old_txnetdata) / 1024)
        cls.log.info("平均上行流量: %skb" % tx_sec_data)
        rx_sec_data = '{:.2f}'.format((new_rxnetdata - old_rxnetdata) / 1024)
        cls.log.info("平均下行流量: %skb" % rx_sec_data)
        txnetdata = [currenttime, new_txnetdata, tx_sec_data]
        rxnetdata = [currenttime, new_rxnetdata, rx_sec_data]
        ExcleDataSave.write_netdata(row=writeexcle_row, txnetdata=txnetdata, rxnetdata=rxnetdata)


class NetThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'ThreadNetData'
        self.stopflag = True
        self.log = log.log('流量测试')

    def run(self, waittime=1):
        self.log.info("开始线程：" + self.name)
        net_writerow = 3
        while self.stopflag:
            try:
                PackNetData.datawrite(writeexcle_row=net_writerow, waittime=waittime)
                net_writerow += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    self.log.error("手动暂停")
                else:
                    self.log.error("Net数据抓取出错 重新运行")
        self.log.info("退出线程：" + self.name)

    def stop(self):
        self.stopflag = False


if __name__ == '__main__':
    PackNetData.datawrite()
