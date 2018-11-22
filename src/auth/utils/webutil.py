#!/usr/bin/env python
#coding:utf-8

import os
import traceback
from mybase.myconf import MyConf
from mybase.mylog3 import log
from mybase.mysingleton import Singleton
from mybase.mysqlpool import MysqlPool

class WebUtil(object):
    __metaclass__ = Singleton # 单例
    def __init__(self):
        self.g_messageQ = None
        self.redis_config = {}

        _config_path = os.environ['WEB_CONFIG']
        self.init_conf( _config_path )
        self.init_mysql_config()

        self.init_log()

    def init_conf(self, conf_path):
        try:
            myconf = MyConf(conf_path)
            # 公共配置
            # LOG
            self.log_dir = os.path.normpath( myconf['LOG']['log_dir'] )
            if not os.path.exists(self.log_dir):
                print 'mkdir, log_dir:%s' % self.log_dir
                os.mkdir(self.log_dir)
            self.log_header = myconf['LOG']['log_header']
            self.log_level = myconf['LOG']['log_level']
            self.log_buf_size = int( myconf['LOG']['log_buf_size'] )
            # MYSQL
            self.mysql_host = myconf['MYSQL']['host']
            self.mysql_port = int( myconf['MYSQL']['port'] )
            self.mysql_user = myconf['MYSQL']['user']
            self.mysql_password = myconf['MYSQL']['password']
            self.mysql_db = myconf['MYSQL']['db']
            # 释放资源
            del myconf
        except:
            print traceback.format_exc()
            raise Exception('init config error')

    def init_log(self):
        try:
            # 初始化日志
            log.init(header=self.log_header, directory=self.log_dir, level=self.log_level, max_buffer=self.log_buf_size, max_line=100000)
            del self.log_header, self.log_dir, self.log_buf_size, self.log_level
            return True
        except:
            print traceback.format_exc()
            raise Exception('init log error')

    def init_mysql_config(self):
        # mysql -uroot -proot666 -h127.0.0.1 -P3306
        self.mysql_config = {
            'host': self.mysql_host,
            'port': self.mysql_port,
            'user': self.mysql_user,
            'password': self.mysql_password,
            'db': self.mysql_db, # 使用指定数据库
            'use_unicode': True,
            'charset': 'utf8', # 数据库连接编码
            'mincached': 1, # 启动时连接池中创建的的连接数.(缺省值0: 代表开始时不创建连接)
            'maxcached': 20, # 连接池中允许的闲置的最多连接数量.(缺省值0: 代表不闲置)
            'maxshared': 0, # 最大共享连接数(默认0: 代表都是专用的)如果达到最大数量, 被请求为共享的连接将会被共享使用)
            'maxconnections': 50, # 创建连接池的最大数量(默认0: 代表不限制)
            'maxusage': 0, # 单个连接的最大允许复用次数(缺省值0或False:代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
            'blocking': False, # 设置连接数到最大时的行为(默认0或False: 代表返回一个错误<toMany......>; 其他代表阻塞直到连接数减少,连接被分配)
            'setsession': None, # 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
        }
        del self.mysql_host, self.mysql_port, self.mysql_user, self.mysql_password, self.mysql_db
        """
        with MysqlPool(self.mysql_config) as p:
            rows = p.select('SELECT * FROM performance_schema.users WHERE USER=%s', ('root',))
            print rows
        """

if __name__ == "__main__":
    def Usage():
        print u"""
        python ./{0}
        """.format(__file__)
    import sys
    if len(sys.argv) == 1: Usage(), sys.exit()
    function = sys.argv[1]
    del sys.argv[1]
    eval(function)()
