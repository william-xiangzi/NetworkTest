#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import threading
from programconfig import Config
from Excle_Operation import ExcleDataSave
from Sys_Info import SystemInfo
from TestLog import log
import subprocess
import re
import time


class MemoryInfo(object):

    # 获取应用内存信息 meminfo[1]
    @staticmethod
    def get_processmem():
        result = subprocess.getoutput('adb shell "dumpsys meminfo ' + Config.packagename() + ' | grep TOTAL"')
        meminfo = result.split("\n")[0].split(" ")
        for i in range(len(meminfo) - 1, -1, -1):
            if meminfo[i] == "":
                meminfo.pop(i)
        return [meminfo[1], meminfo[2], meminfo[3]]

    # 获取系统内存信息
    @staticmethod
    def get_sysmem():
        result = subprocess.getoutput('adb shell "cat /proc/meminfo"')
        temp = result.split("\n")
        for i in range(len(temp) - 1, -1, -1):
            if temp[i] == "":
                temp.pop(i)
        info = {}
        for istr in temp:
            tem = istr.split(":")
            key = tem[0]
            value = val = re.search('\d+', istr).group()
            info[key] = value
        total = str(int(int(info["MemTotal"]) / 1024)) + "Mb"
        free = str(int(int(info["MemFree"]) / 1024)) + "Mb"
        available = str(int(int(info["MemAvailable"]) / 1024)) + "Mb"
        return [total, free, available]


class MemoryWrite(object):
    log = log.log('内存测试')

    @staticmethod
    def memdata_write(row=3):
        process_memory = (int(MemoryInfo.get_processmem()[0]) // 2014)
        sys_memory = MemoryInfo.get_sysmem()[0]
        currenttime = time.strftime('%H%:%M:%S', time.localtime(time.time()))
        currentactivity = SystemInfo.currentactivity()
        memdata = [currenttime, currentactivity, process_memory, sys_memory]
        ExcleDataSave.write_memdata(row=row, memdata=memdata)
        return process_memory

    @classmethod
    def memaction(cls):
        row = 3
        while True:
            try:
                process_mem = MemoryWrite.memdata_write(row=row)
                cls.log.info("内存数据写入成功 应用内存: %s" % process_mem)
                time.sleep(6)
                row += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    cls.log.info('手动暂停')
                else:
                    cls.log.error("内存测试出错 重新运行")


class MemThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'ThreadMemData'
        self.stopflag = True
        self.log = log.log('内存测试')

    def run(self, waittime=2):
        self.log.info("开始线程：" + self.name)
        mem_writerow = 3
        while self.stopflag:
            try:
                process_mem = MemoryWrite.memdata_write(row=mem_writerow)
                self.log.info("内存数据写入成功 应用内存: %s" % process_mem)
                time.sleep(waittime)
                mem_writerow += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    self.log.info('手动暂停')
                else:
                    self.log.error("内存测试出错 重新运行")
        self.log.info("退出线程：" + self.name)

    def stop(self):
        self.stopflag = False


if __name__ == "__main__":
    MemoryWrite.memaction()
