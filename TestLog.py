#!/usr/bin/python
# -*- coding: UTF-8 -*-

import logging.config


class TestLog(object):
    def __init__(self):
        logging.config.fileConfig('./config/logger.conf')

    def log(self, testmoudle):
        log = logging.getLogger(testmoudle)
        return log


log = TestLog()

if __name__ == '__main__':

    for i in range(10):
        log.log('测试测试').info(i)



