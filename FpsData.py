#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import time
import threading
from programconfig import Config
from TestLog import log
from Excle_Operation import ExcleDataSave
from Sys_Info import SystemInfo


# 帧率数据抓取
class Gfxinfo(object):

    log = log.log('帧率测试')

    def __init__(self):
        pass

    @classmethod
    def getgfxdata(cls):
        gfxdataclean = os.popen('adb -s %s shell dumpsys gfxinfo %s'
                                % (Config.devices(), Config.packagename())).readlines()
        cls.log.debug(gfxdataclean)

        # 清洗列表中数据；把 \n 都清洗掉;清洗好后的数据放入 gfxdata
        gfxdata = []
        for index in range(len(gfxdataclean)):
            if gfxdataclean[index] != '\n':
                gfxdata.append(gfxdataclean[index].strip())

        totalframesrendered = ''
        jankyframes = ''
        framesactivity = ''
        dictkeycount = 1
        dictframes = {}
        for index in range(len(gfxdata)):
            # totalframesrendered：总计渲染了多少帧
            if 'Total frames rendered' in gfxdata[index]:
                totalframesrendered = gfxdata[index].split(':')[1]
                cls.log.debug('总计渲染页面totalframesrendered = %s' % totalframesrendered)

            # Janky frames 掉帧率；渲染时间在 16.67 ms以上的帧
            if 'Janky frames' in gfxdata[index]:
                jankyframes = gfxdata[index].split(':')[1]
                cls.log.debug('掉帧率 jankyframes = %s' % jankyframes)

            # 读取帧率详细时间数据；
            if ('io.liuliu.music/' in gfxdata[index]) and ('Draw' in gfxdata[index+1]):
                # 找到 io.liuliu.music 后根据展示规则 判断文档下一行是否存在 Draw 如果存在则进入d分析逻辑
                # 根据读取的数据判断 Draw、Process、Execute 分别的 index 保证数据准确性
                framesactivity = gfxdata[index].split('/')[1].strip()
                cls.log.info('帧率测试：开始计算 index = %d' % index)
                gfxdetailed = gfxdata[index+1].split('\t', 4)
                drawindex = gfxdetailed.index('Draw')
                processindex = gfxdetailed.index('Process')
                executeindex = gfxdetailed.index('Execute')
                # 判断是否有详细的帧率时间数据；需要在 Draw 下判断才符合规则
                # 读取共有多少行帧率时间数据；
                startpersecgfxtime = index + 2
                isbaddata = 'false'
                persecgfxcollect = []
                while isbaddata == 'false':
                    if ('io.liuliu.music' not in gfxdata[startpersecgfxtime]) \
                            and ('View hierarchy' not in gfxdata[startpersecgfxtime]):
                        persecgfx = gfxdata[startpersecgfxtime].split('\t', 4)
                        drawtime = float(persecgfx[drawindex])
                        processtime = float(persecgfx[processindex])
                        executetime = float(persecgfx[executeindex])
                        persecgfxcollect.append([drawtime, processtime, executetime])
                        startpersecgfxtime += 1
                    else:
                        isbaddata = 'true'
                        cls.log.info('帧率测试：数据读取完成或无帧率详细数据 index = %d' % startpersecgfxtime)

                # 判断 persecgfxcollect 是否为空；如果 persecgfxcollect 无数据则不向字典写数据
                if len(persecgfxcollect) != 0:
                    dictframes[dictkeycount] = persecgfxcollect
                    dictkeycount += 1

        return totalframesrendered, jankyframes, dictframes, framesactivity


# 帧率时间计算；统计两个数据：每一个activity的 janky frames、每个activity 的平均时长
class FramesTime(object):

    log = log.log('帧率测试')

    def __init__(self):
        pass

    @classmethod
    def timecount(cls):
        framedetail = Gfxinfo.getgfxdata()
        cls.log.debug('Frames字段有%d个数据' % len(framedetail[2]))
        if len(framedetail[2]) > 0:
            for index in framedetail[2]:
                cls.log.info('当前页面 Activity: %s' % framedetail[3])
                cls.log.debug('当前数据 %d: %s' % (index, framedetail[2][index]))
                # 计算 Activity 的janky frames
                frames = FramesTime.framescounter(listtest=framedetail[2][index])
                cls.log.info(frames)
                return [frames, framedetail[3]]

        else:
            cls.log.error('帧率测试：帧率数据错误,不存在详细帧率数据；len(framedetail[2]) = %d' % len(framedetail[2]))

    # 写一个公共方法用于计算 list的和节省代码
    @classmethod
    def framescounter(cls, listtest):
        sumlist = 0
        frameslist = []
        jankycount = 0

        # 计算二位数组的和；并且把二维数组中每个数组的和放到一个新 list 里
        try:
            if len(listtest) != 0:
                for index in listtest:
                    sumlist += sum(index)
                    frameslist.append(sum(index))
            else:
                cls.log.error('framescounter error：数据错误；传入的list 为空')
        except TypeError:
            cls.log.error('framescounter error：数据错误；传入数据为非list')

        # 计算掉帧率算法；统计掉帧的帧数;同时清洗数据,所有数据四舍五入保留整数,用于 统计帧率渲染时间百分比排名
        listclean = []
        for index in frameslist:
            if index >= 16.67:
                jankycount += 1
            listclean.append('{:.0f}'.format(index))

        # 统计帧率渲染时间百分比排名;放到一个字典中
        framespercentdict = {}
        for cleanindex in listclean:
            count = listclean.count(cleanindex)
            if cleanindex not in framespercentdict:
                framespercentdict[cleanindex] = count
        framespercentlist = sorted(framespercentdict.items(), key=lambda item: item[1], reverse=True)
        framespercent = framespercentlist[0:3]

        # 帧率百分比计算；计算完成后分别把帧率计算时间和百分比放入字典
        percentdict = {}
        for percentindex in framespercent:
            perframespercent = int(percentindex[1]) / len(frameslist)
            percentdict[percentindex[0]] = '{:.2%}'.format(perframespercent)

        jankyframespercent = '{:.2%}'.format(jankycount / len(frameslist))
        listaverage = '{:.2f}'.format(sumlist / len(listtest))
        listmax = '{:.2f}'.format(max(frameslist))
        listmin = '{:.2f}'.format(min(frameslist))
        return {'timesum': sumlist, 'framecount': len(frameslist), 'timeaverage': listaverage,
                'timemax': listmax, 'timemin': listmin, 'jankyframespercent': jankyframespercent,
                'timepercent': percentdict}


# 监控当前activity是否变化；如果变化则返回最新的activity；如果未变化则返回false
class Activitymonitor(object):
    log = log.log('帧率测试')

    @classmethod
    def monitor(cls):
        row = 3
        while True:
            try:
                framesdata = FramesTime.timecount()
                ExcleDataSave.write_fpsdata(row=row, framesdata=framesdata)
                time.sleep(3)
                row += 1
            except Exception as err:
                if err is KeyboardInterrupt:
                    cls.log.info('手动暂停')
                else:
                    cls.log.error("帧率测试运行出错 重新开始运行")


class FpsThread (threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.name = 'ThreadFpsData'
        self.stopflag = True
        self.log = log.log('帧率测试')

    def run(self, waittime=2):
        self.log.info("开始线程:%s" % self.name)
        fps_writerow = 3
        while self.stopflag:
            try:
                framesdata = FramesTime.timecount()
                ExcleDataSave.write_fpsdata(row=fps_writerow, framesdata=framesdata)
                fps_writerow += 1
                time.sleep(waittime)
            except Exception as err:
                if err is KeyboardInterrupt:
                    self.log.info('手动暂停')
                else:
                    self.log.error("帧率测试运行出错 重新开始运行")
        self.log.info("结束线程:%s" % self.name)

    def stop(self):
        self.stopflag = False


if __name__ == '__main__':
    Activitymonitor.monitor()
