#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sqlite3


connect = sqlite3.connect('./SQL/performance.db')
print('数据库：performance.db 创建成功')
connect.close()