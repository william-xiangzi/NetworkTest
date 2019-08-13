#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import subprocess
import time
import threading
from TestLog import log
from programconfig import Config
from Sys_Info import SystemInfo
from Excle_Operation import ExcleDataSave


class CpuOperat(object):

    @classmethod
    def cpu_totaltime(cls):
        cmd = "adb -s " + Config.devices() + " shell cat /proc/stat"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        res = output.split()

        # 无需读取总数 cpu 即为总数
        result = 0
        for info in res:
            if info.decode() == "cpu":
                user = res[1].decode()
                nice = res[2].decode()
                system = res[3].decode()
                idle = res[4].decode()
                iowait = res[5].decode()
                irq = res[6].decode()
                softirq = res[7].decode()
                result = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
        return result

    @classmethod
    def cpu_processtime(cls):
        cmd = "adb -s " + Config.devices() + " shell cat /proc/" + SystemInfo.packagepid() + "/stat"
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             stdin=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        res = output.split()

        utime = res[13].decode()
        stime = res[14].decode()
        cutime = res[15].decode()
        cstime = res[16].decode()
        result = int(utime) + int(stime) + int(cutime) + int(cstime)
        return result

    '''
    计算某进程的cpu使用率
    100*( processCpuTime2 – processCpuTime1) / (totalCpuTime2 – totalCpuTime1) (按100%计算，如果是多核情况下还需乘以cpu的个数);
    cpukel cpu几核
    pid 进程id
    '''
    @classmethod
    def cpu_rate(cls, waittime=1):
        """

        :param waittime: Cpu 数据抓取等待时长
        :return:
        """
        cpu_processtimeold = cls.cpu_processtime()
        cpu_totaltimeold = cls.cpu_totaltime()
        time.sleep(waittime)
        cpu_processtimenew = cls.cpu_processtime()
        cpu_totaltimenew = cls.cpu_totaltime()

        cpu_processtime = cpu_processtimenew - cpu_processtimeold
        cpu_totaltime = cpu_totaltimenew - cpu_totaltimeold

        cpu = cpu_processtime / cpu_totaltime
        return cpu


# 此方法为不启动线程式 Cpu 数据捕捉 可以用户Debug 调试
class Cpu(CpuOperat):
    log = log.log('CPU测试')

    @classmethod
    def data(cls):
        # 如果这些变量可以放到类方法里尽量放到类方法里 不然每次文件被导入或者被继承 类变量都会执行一遍
        cpumax = cpumin = CpuOperat.cpu_rate(waittime=1)
        cpu_writerow = 3
        cpucount = 0
        cpucountnum = 1
        while True:
            try:
                cpu = cls.cpu_rate(waittime=1)
                if cpu > cpumax:
                    cpumax = cpu
                if cpu < cpumin:
                    cpumin = cpu
                cpucount += cpu
                # cpulist.append(cpu)
                cpuaverg = cpucount / cpucountnum
                cls.log.info('当前CPU使用率 = %f' % cpu)
                cls.log.info('当前CPU使用率平均值 = %s' % cpuaverg)
                cls.log.info('当前CPU最大使用值 = %f' % cpumax)
                cls.log.info('当前CPU最小使用值 = %f' % cpumin)

                currenttime = SystemInfo.systime()
                currentactivity = SystemInfo.currentactivity()
                sys_cure = SystemInfo.cpuinfo()['cpucure']
                cpudata = [currenttime, currentactivity, cpu, sys_cure]
                ExcleDataSave.write_cpudata(row=cpu_writerow, cpudata=cpudata)

                cpucountnum += 1
                cpu_writerow += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    cls.log.error("手动暂停")
                else:
                    cls.log.error("CPU 数据抓取出错 重新运行")


# 此类用于启动 Cpu 捕获数据的线程;使用此线程前必须实例化 CpuThread 类
class CpuThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'ThreadCpuData'
        self.stopflag = True
        self.log = log.log('CPU测试')

    def run(self, waittime=1):
        """
        :param waittime: cpu_rate 数据抓取时长间隔
        :return:
        """
        self.log.info("开始线程：%s" % self.name)
        cpu_writerow = 3
        while self.stopflag:
            try:
                cpu = CpuOperat.cpu_rate(waittime=waittime)
                currenttime = SystemInfo.systime()
                currentactivity = SystemInfo.currentactivity()
                sys_cure = SystemInfo.cpuinfo()['cpucure']
                cpudata = [currenttime, currentactivity, cpu, sys_cure]
                self.log.info('当前CPU使用率 = %f' % cpu)
                ExcleDataSave.write_cpudata(row=cpu_writerow, cpudata=cpudata)
                cpu_writerow += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    self.log.error("手动暂停")
                else:
                    self.log.error("CPU 数据抓取出错 重新运行")
        self.log.info("退出线程：%s" % self.name)

    def stop(self):
        self.stopflag = False


if __name__ == '__main__':
    run = CpuThread()
    run.start()
    time.sleep(10)
    run.stop()
