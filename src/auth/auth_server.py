#coding:utf-8

import os
import traceback
# Web框架库
from flask import Flask, request, redirect, jsonify, session, abort, render_template
from auth.wxapi import wxapi
from auth.utils.webutil import WebUtil

app = Flask(
    __name__,
    # template_folder='templates', # 指定模板路径, (相对路径或绝对路径)
    # static_folder='static', # 指定静态文件前缀, 默认为static. (相对路径或绝对路径)
    # static_url_path='' # 指定静态文件存放路径
)
app.register_blueprint(wxapi, url_prefix='/wxapi') # 注册蓝图, 并指定前缀

# 多进程处理, 分发时, 不同密码可能加密session时会有问题. 待验证
# TODO 待修改调试模式, 不然页面修改不能实时同步
app.debug = True # 调试模式

# 设置会话密钥
app.secret_key = 'Er!css0n@guanjia.group'

if __name__ == '__main__':
    # 多线程才能解决Broken pipe问题, 参考: https://stackoverflow.com/questions/12591760/flask-broken-pipe-with-requests
    # 以下代码因在__main__中, 并不是gunicorn的入口代码, 所以只针对脱离gunicorn启动测试生效
    app.run(host='0.0.0.0', port=80, threaded=True)
