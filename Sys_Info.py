#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
优化思路：可以把系统的信息优化成类属性；返回类属性的字典
"""

import os
import time
import sqlite3
from programconfig import Config
from TestLog import TestLog
import subprocess


class SystemInfo(object):
    log = TestLog().log('系统信息')

    # 获取系统时间的方法
    @classmethod
    def systime(cls):
        systime = time.strftime('%H%:%M:%S', time.localtime(time.time()))
        return systime

    # 获取系统当前活跃 Activity
    @classmethod
    def currentactivity(cls):
        mcurrentfocus = os.popen('adb shell dumpsys window windows | grep mCurrent').read().split(" ")
        activity = mcurrentfocus[len(mcurrentfocus)-1].split("}")[0]
        return activity

    # 获取当前系统版本号
    @classmethod
    def androidversion(cls):
        version = os.popen('adb shell getprop ro.build.version.release').read().rstrip()
        return version

    # 设备信息
    @classmethod
    def devicesinfo(cls):
        devices = os.popen('adb shell getprop ro.product.model').read().rstrip()
        return devices

    # 设备CPU信息；CPU核数、CPU频率、CPU名称
    @classmethod
    def cpuinfo(cls):
        try:
            cpunamecmd = "adb -s {} shell cat /proc/cpuinfo".format(Config.devices())
            cpukercmd = "adb -s {} shell cat /proc/cpuinfo |grep ^processor |wc -l".format(Config.devices())

            cpuname = subprocess.Popen(cpunamecmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cpuname = str(cpuname.stdout.read()).split('Hardware', 1)[1].split(':', 1)[1]
            cpuname = cpuname[0:len(cpuname) - 3].strip()

            cpuker = subprocess.Popen(cpukercmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            cpuker = str(cpuker.stdout.read()).split()[1]
            cpuker = int(cpuker[0:len(cpuker) - 3].strip())

            cpuratelist = []
            for index in range(cpuker):
                cpuratecmd = "adb shell cat /sys/devices/system/cpu/cpu{}/cpufreq/cpuinfo_max_freq".format(index)
                cpurate = int(os.popen(cpuratecmd).read())
                cpuratelist.append(cpurate)
            cpuratemax = '{:.1f}'.format((max(cpuratelist)/1000000))+'GHz'

            return {'cpuname': cpuname, 'cpucure': cpuker, 'cpuratemax': cpuratemax}
        except Exception as e:
            cls.log.error(e)
            cls.log.error("未获取到cpu信息")

    # 获取设备可用内存大小；设备可用内存大小一般比系统RAM(物理内存)要小一些；主要耗费在系统
    @classmethod
    def meminfo(cls):
        try:
            memadb = "adb -s {} shell cat /proc/meminfo |grep MemTotal".format(Config.devices())
            meminfo = int(os.popen(memadb).read().split()[1]) / 1024 / 1024
            meminfo = '{:.2f}'.format(meminfo) + 'G'
            return meminfo
        except Exception as e:
            cls.log.error("读取系统内存信息失败")
            cls.log.error(e)

    # 安装包版本号
    @classmethod
    def packageversion(cls):
        version = os.popen('adb shell dumpsys package %s |grep versionName' % Config.packagename()).read().split('=')[1].rstrip()
        return version

    # 安装包打包编号；build号
    @classmethod
    def packageversioncode(cls):
        versioncode = os.popen('adb shell dumpsys package %s |grep versionCode' % Config.packagename()).read().split()
        versioncode = versioncode[0].split("=", 1)[1]
        return versioncode

    # 安装包首次安装时间；firstinstalltime
    @classmethod
    def firstinstalltime(cls):
        installtime = os.popen('adb shell dumpsys package %s |grep firstInstallTime' % Config.packagename()).read().split("=", 1)
        installtime = installtime[1].lstrip().rstrip()
        return installtime

    # 获取packagepid方法
    @classmethod
    def packagepid(cls):
        try:
            packagepid = os.popen('adb shell ps |grep %s' % Config.packagename())
            for index in packagepid.readlines():
                if 'io.liuliu.music:' not in index:
                    packagepid = index.strip().split()[1]
            return packagepid
        except IndexError:
            cls.log.info("读取错误：未读取到 packagepid 数据")

    # 获取packageuid方法
    @classmethod
    def packageuid(cls):
        try:
            package = \
                os.popen('adb -s %s shell ps |grep %s' % (Config.devices(), Config.packagename())).read().split(" ")[0]
            # 字符串截取坑：截取时不包含冒号后的数 3：7 的意思也就是：3，4，5，6
            packageuid = package[0:2] + package[3:7]
            return packageuid.strip()
        except IndexError as e:
            cls.log.error("读取错误：未读取到 packageuid 数据")


# 系统信息数据库操作；把电量写入sqlite数据库
# 调用该方法时需传入一个唯一的 testid 作为外键
class SysinfoDBopera(object):
    log = TestLog().log('系统信息')

    def __init__(self, testid):
        self.test = int(testid)
        # 写入数据时使用 self.dbconnect
        self.dbconnect = sqlite3.connect('./SQL/performance.db')
        # 读取数据时使用 self.db
        self.db = self.dbconnect.cursor()
        print("DB：performance.db 连接成功")

    def datawrite(self):
        try:
            self.dbconnect.execute(
                "INSERT INTO androidsysinfo"
                "(testid,systemtime,currrntactivity,androidversion,devicesinfo,packageversion,packageversioncode)"
                "VALUES ('%d', '%s', '%s', '%s', '%s', '%s', '%s')"
                % (self.test, SystemInfo.systime(), SystemInfo.currentactivity(), SystemInfo.androidversion(),
                   SystemInfo.devicesinfo(), SystemInfo.packageversion(), SystemInfo.packageversioncode()))
            print("DB-SysinfoDBopera：SysinfoDBoper-datawrite 系统信息数据写入成功")
        except:
            print("DB-SysinfoDBopera：数据写入失败")
        self.dbconnect.commit()
        print("DB-SysinfoDBopera：数据已成功提交")

    def dataread(self):
        dataread = self.db.execute("select * from androidsysinfo")
        print("DB：数据库输出")
        for row in dataread:
            print(row)


if __name__ == '__main__':
    print(SystemInfo.currentactivity())
    print(SystemInfo.androidversion())
    print(SystemInfo.devicesinfo())
    print(SystemInfo.packageversion())
    print(SystemInfo.systime())
    print(SystemInfo.packageversioncode())
    print(SystemInfo.firstinstalltime())
    print(SystemInfo.cpuinfo())
    print(SystemInfo.meminfo())
    print(SystemInfo.packagepid())
