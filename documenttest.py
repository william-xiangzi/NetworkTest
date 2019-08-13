#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import os
import sys
import time

# os.mkdir(path='./Datafile/Nature/')


class hanshutest(object):
    nowtime = time.strftime('%H%:%M:%S', time.localtime(time.time()))

    def test(self):
        print("Now is in test")

    def diaoyong(self):
        # print(self.__reduce__())
        # print(self.__init__())

        test = self.__class__
        print(test)

    @classmethod
    def diaoyong3(cls):
        print(cls.nowtime)


print(hanshutest().__reduce__())

test = hanshutest()


for index in range(10):
    print(hanshutest.diaoyong3())
    time.sleep(5)
