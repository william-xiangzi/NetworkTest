#!/usr/bin/python
# -*- coding: UTF-8 -*-

import configparser
import logging.config
import time

logging.config.fileConfig('./config/logger.conf')
log = logging.getLogger('系统配置')


# 程序基础配置文件；可以直接从配置文件读取系统数据
class Config(object):
    config = configparser.ConfigParser()
    config.read('./config/programconfig.conf', encoding='utf-8')

    @classmethod
    def packagename(cls):
        if cls.config.has_section('packagename'):
            name = cls.config.get('packagename', 'packagename')
            return name
        else:
            log.error('配置文件中不存在配置选项：packagename')
            return 'error'

    @classmethod
    def devices(cls):
        if cls.config.has_section('devices'):
            name = cls.config.get('devices', 'devices')
            return name
        else:
            log.error('配置文件中不存在配置选项：devices')
            return 'error'

    @classmethod
    def exitflag(cls):
        if cls.config.has_section('exit_flag'):
            flag = cls.config.get('exit_flag', 'exitflag')
            return flag
        else:
            log.error('配置文件中不存在配置选项：exit_flag')
            return 'error'


if __name__ == '__main__':

    count = 0
    while Config.exitflag() == 'True':
        print(Config.packagename())
        print(Config.devices())
        print(Config.exitflag())
        time.sleep(1)
        count += 1
        print('这是第 %d 次循环' % count)

    print('退出标志 %s' % Config.exitflag())
