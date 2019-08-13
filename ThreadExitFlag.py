#!/usr/bin/python3
# -*- coding: UTF-8 -*-


"""WorkManage
Usage:
  workmanage runserver [-c][-b][-f][-g]
  workmanage stopserver [-c][-b][-f][-g]
  workmanage -h | --help
  workmanage --version

Options:
  -c  运行cpu测试;如果runserver 指定了选项则单别运行其中的某几项,否则全部运行
  -b  运行battery测试;如果runserver 指定了选项则单别运行其中的某几项,否则全部运行
  -f  运行fps测试;如果runserver 指定了选项则单别运行其中的某几项,否则全部运行
  -g  运行流量测试;如果runserver 指定了选项则单别运行其中的某几项,否则全部运行
  -h --help     帮助.
  -v --version     查看版本号.
"""

from docopt import docopt
import threading
import time

# arguments = docopt(__doc__, version='WorkManage 2.0')


class WorkManage(object):
    def __init__(self):
        self.arguments = docopt(__doc__, version='WorkManage 2.0')

    def runserver(self):
        while self.arguments['stopserver'] != True:
            print("服务开始运行"+time.ctime())
            print("stopserver = %s" % self.arguments['stopserver'])
            time.sleep(2)
        else:
            print("server stop")
        return self.arguments['runserver']

    def stopserver(self):
        print("服务停止运行")
        print(self.arguments['stopserver'])
        return self.arguments['stopserver']


if __name__ == '__main__':
    test = WorkManage().runserver()
