#!/usr/bin/env python
#coding:utf-8

from flask import Blueprint
 
# 在wxapi/__init__.py定义是为了在main.py 中使用 from wxapi import wxapi
wxapi = Blueprint(name = 'wxapi',
        import_name = __name__, # 模块名
        template_folder='templates', # 指定模板路径, (相对路径或绝对路径)
        static_folder='static', # 指定静态文件前缀, 默认为static. (相对路径或绝对路径)
        static_url_path='' # 指定静态文件存放路径
        )
import wechat_api
