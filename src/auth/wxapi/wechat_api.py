#coding:utf-8

import sys
import traceback
import time
import datetime
import pytz
import base64
import binascii
import hashlib
# 第三方库
from flask import Flask, request, redirect, jsonify, session, abort, render_template, Response
from decouple import config
# 自己的库
from mybase.mylog3 import log
from mybase.myencrypt2 import encrypt_aes, decrypt_aes
from mybase.myutil import basetype_to_str
from mybase.mysqlpool import MysqlPool, IntegrityError
from mybase.mycksum import calmd5
from mybase.myrandom import MyRandom
from auth.wxapi import wxapi
from auth.utils.webutil import WebUtil

# 全局变量
WEBUTIL = WebUtil()
g_tz = pytz.timezone('Asia/Shanghai')

TOKEN_SECRET = config('TOKEN_SECRET')
IV = config('IV')


@wxapi.before_app_first_request
def init_my_blueprint():
    pass


def get_session():
    openid, wxid = '', ''
    if session.has_key('openid'): # flask机制保证session不会被擅改!
        openid = session['openid']
        log.d( "old session: {}", session )
    if session.has_key('wxid'):
        wxid = session['wxid']
    return (openid, wxid)


# /wxapi/heartbeat
@wxapi.route('/heartbeat', methods=['GET'])
def Page_Index():
    log.d(sys._getframe().f_code.co_name)
    try:
        return "heartbeat"
    except:
        log.e(traceback.format_exc())


@wxapi.route('/hwinfo.json', methods=['POST'])
def Page_HWinfoJson():
    log.d(sys._getframe().f_code.co_name)
    # log.d( 'request url: {}', request.url )
    log.d("request form: {}", request.form.items().__str__())
    try:
        json_param = basetype_to_str(request.json)
        msgtype = json_param['msgtype']
        func = getattr(HardwareInfo, msgtype, None)
        if func:
            return func(json_param)
        else:
            log.e('unknown msgtype: {}', msgtype)
            return jsonify({"code": '系统错误'})
    except:
        log.e(traceback.format_exc())
        return jsonify({"code": '系统错误'})


class HardwareInfo(object):
    # 保存机器硬件信息
    @staticmethod
    def login_success(json_param):
        log.d(sys._getframe().f_code.co_name)
        log.d("json_param = {}", json_param)
        userinfo = json_param['userinfo']
        wxid = userinfo['wxid']
        alias = userinfo['alias']
        nickname = userinfo['nickname']
        qq = userinfo['qq']
        email = userinfo['email']
        appversion = userinfo['appversion']
        #
        hwinfo = json_param['hwinfo']
        log.d("hwinfo = {}", hwinfo)
        ##
        IMEI = hwinfo['IMEI']
        android_id = hwinfo['android_id']
        Line1Number = hwinfo['Line1Number']
        SimSerialNumber = hwinfo['SimSerialNumber']
        IMSI = hwinfo['IMSI']
        SimCountryIso = hwinfo['SimCountryIso']
        SimOperator = hwinfo['SimOperator']
        SimOperatorName = hwinfo['SimOperatorName']
        NetworkCountryIso = hwinfo['NetworkCountryIso']
        NetworkOperator = hwinfo['NetworkOperator']
        NetworkOperatorName = hwinfo['NetworkOperatorName']
        NetworkType = hwinfo['NetworkType']
        PhoneType = hwinfo['PhoneType']
        SimState = hwinfo['SimState']
        MacAddress = hwinfo['MacAddress']
        SSID = hwinfo['SSID']
        BSSID = hwinfo['BSSID']
        RELEASE = hwinfo['RELEASE']
        SDK = hwinfo['SDK']
        CPU_ABI = hwinfo['CPU_ABI']
        CPU_ABI2 = hwinfo['CPU_ABI2']
        widthPixels = hwinfo['widthPixels']
        heightPixels = hwinfo['heightPixels']
        RadioVersion = hwinfo['RadioVersion']
        BRAND = hwinfo['BRAND']
        MODEL = hwinfo['MODEL']
        PRODUCT = hwinfo['PRODUCT']
        MANUFACTURER = hwinfo['MANUFACTURER']
        cpuinfo = hwinfo['cpuinfo']
        HARDWARE = hwinfo['HARDWARE']
        FINGERPRINT = hwinfo['FINGERPRINT']
        DISPLAY = hwinfo['DISPLAY']
        INCREMENTAL = hwinfo['INCREMENTAL']
        SERIAL = hwinfo['SERIAL']
        # 计算MD5
        key = '{wxid}{heightPixels}{widthPixels}{appversion}{RELEASE}{MODEL}{BRAND}{android_id}{MANUFACTURER}{PRODUCT}{FINGERPRINT}{cpuinfo}'.format( 
                wxid=wxid, heightPixels=heightPixels, widthPixels=widthPixels, appversion=appversion, RELEASE=RELEASE, MODEL=MODEL, BRAND=BRAND, android_id=android_id,
                MANUFACTURER=MANUFACTURER, PRODUCT=PRODUCT, FINGERPRINT=FINGERPRINT, cpuinfo=cpuinfo
        )
        cksum = calmd5(key)
        try:
            with MysqlPool(WEBUTIL.mysql_config) as p:
                ret = p.execute( """INSERT INTO hardware( wxid, alias, nickname, qq, email, appversion, cksum, IMEI, android_id, Line1Number, SimSerialNumber, IMSI, SimCountryIso, SimOperator, SimOperatorName, NetworkCountryIso, NetworkOperator, NetworkOperatorName, NetworkType, PhoneType, SimState, MacAddress, SSID, BSSID, `RELEASE`, SDK, CPU_ABI, CPU_ABI2, widthPixels, heightPixels, RadioVersion, BRAND, MODEL, PRODUCT, MANUFACTURER, cpuinfo, HARDWARE, FINGERPRINT, DISPLAY, INCREMENTAL, SERIAL
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )""",
                    (wxid, alias, nickname, qq, email, appversion, cksum, IMEI, android_id, Line1Number, SimSerialNumber, IMSI, SimCountryIso, SimOperator, SimOperatorName, NetworkCountryIso, NetworkOperator, NetworkOperatorName, NetworkType, PhoneType, SimState, MacAddress, SSID, BSSID, RELEASE, SDK, CPU_ABI, CPU_ABI2, widthPixels, heightPixels, RadioVersion, BRAND, MODEL, PRODUCT, MANUFACTURER, cpuinfo, HARDWARE, FINGERPRINT, DISPLAY, INCREMENTAL, SERIAL)
                )
                p.commit()
            return jsonify({"code": ''})
        except IntegrityError:
            log.w('hardware duplicated')
            return jsonify({"code": ''})
        except Exception as e:
            raise e

    # "新设备登陆, 需要验证", 返回旧硬件信息
    @staticmethod
    def login_new_device(json_param):
        log.d(sys._getframe().f_code.co_name)
        userinfo = json_param['userinfo']
        user = userinfo['user']
        try:
            with MysqlPool(WEBUTIL.mysql_config) as p:
                rows = p.select( 'SELECT IMEI, android_id, Line1Number, SimSerialNumber, IMSI, SimCountryIso, SimOperator, SimOperatorName, NetworkCountryIso, NetworkOperator, NetworkOperatorName, NetworkType, PhoneType, SimState, MacAddress, SSID, BSSID, `RELEASE`, SDK, CPU_ABI, CPU_ABI2, widthPixels, heightPixels, RadioVersion, BRAND, MODEL, PRODUCT, MANUFACTURER, cpuinfo, HARDWARE, FINGERPRINT, DISPLAY, INCREMENTAL, SERIAL\
                        FROM hardware WHERE wxid=%s OR alias=%s OR qq=%s OR email=%s ORDER BY update_time',
                    (user, user, user, user)
                )
                if not rows:
                    log.w('no record, user: {}', user)
                    return jsonify( {} )
                row = rows[0]
                return jsonify( {"action": 'hook_hardware', "hwinfo": row} )
            return jsonify( {} )
        except Exception as e:
            raise e


@wxapi.route('/auth.json', methods=['POST'])
def Page_AuthenticJson():
    log.d(sys._getframe().f_code.co_name)
    # log.d( 'request url: {}', request.url )
    log.d("request form: {}", request.form.items().__str__())
    try:
        json_param = basetype_to_str(request.json)
        msgtype = json_param['msgtype']
        func = getattr(Authentic, msgtype, None)
        if func:
            return func(json_param)
        else:
            log.e('unknown msgtype: {}', msgtype)
            return jsonify({"code": '系统错误'})
    except:
        log.e(traceback.format_exc())
        return jsonify( {"code": '系统错误'} )


class Authentic(object):
    # UI界面简单验证
    @staticmethod
    def authentic_simple(json_param):
        log.d(sys._getframe().f_code.co_name)
        token = request.headers.get('token', None)
        device_id = request.headers.get('device-id', None)
        build_variant = request.headers.get('build-variant', None)
        real_ip = request.headers.get('X-Real-Ip', None)
        log.d( "device-id: {}, ip: {}, build-variant: {}, token: {}", device_id,  real_ip, build_variant, token)
        log.d( "json_param = {}", json_param )
        md5_token = json_param['md5_token']
        with MysqlPool(WEBUTIL.mysql_config) as p:
            rows = p.select( 'SELECT token FROM tb_toolkit_token WHERE md5_token=%s and is_enable=1',
                (md5_token,)
            )
            log.d( "rows={}", rows )
            if not rows:
                # 验证不通过
                log.w('auth_simple fail, device-id: {}, ip: {}, build-variant: {}', device_id, real_ip, build_variant)
                return jsonify({"code": '验证失败'})
            if len(rows) > 1: log.e('md5 token duplicate!')
            row = rows[0]
            # 用户token表: md5_token = MD5(token+TOKEN_SECRET); SELECT token FROM tb_toolkit_token WHERE md5_token=?
            # 计算MD5_TOKEN值, 方法1 (推荐使用):    update tb_toolkit_token set md5_token=MD5(concat(token, TOKEN_SECRET));
            # 计算MD5_TOKEN值, 方法2:   ./mycksum.py test_calmd5  "13857e53aa9cbf9e0e9fe38b01" + $TOKEN_SECRET
            user_token = row['token']
            res_md5_token = calmd5(user_token + TOKEN_SECRET)
            log.i("authentic simple success, res_md5_token: {}", res_md5_token)
            return jsonify({"code": '', "md5_token": res_md5_token})

    # 插件验证, I包
    @staticmethod
    def authentic_i(json_param):
        log.d(sys._getframe().f_code.co_name)
        token = request.headers.get('token', None)
        device_id = request.headers.get('device-id', None)
        build_variant = request.headers.get('build-variant', None)
        real_ip = request.headers.get('X-Real-Ip', None)
        log.d( "device-id: {}, ip: {}, build-variant: {}, token: {}", device_id,  real_ip, build_variant, token)
        log.d( "json_param = {}", json_param )
        key = json_param['key']
        encrypt_last_token = json_param['last_token']
        last_token = decrypt_aes(key, encrypt_last_token, iv=IV, usebase64=True)
        # I包, 不需要判断 key 与库表中不一样, 而解密后last_token需要与库表中user_token相同
        with MysqlPool(WEBUTIL.mysql_config) as p:
            rows = p.select( 'SELECT token FROM tb_toolkit_token WHERE token=%s and is_enable=1',
                (last_token,)
            )
            if not rows:
                # 验证不通过
                log.w('auth_i fail, device-id: {}, ip: {}, build-variant: {}', device_id, real_ip, build_variant)
                return jsonify({"code": '验证失败'})
            if len(rows) > 1:
                log.e('user token duplicate!')
            row = rows[0]
            user_token = row['token'].encode('utf8') # note: 必须转为utf8, 默认是Unicode! 这样才能与java端保持一致!
            # { 
                # token = Bse64( AES(data=user_token, key=当前客户随机串, initVector=IV) ),
                # last_token = Bse64( AES(data=new_last_token, key=当前客户随机串, initVector=IV) )
            # }
            # 1.
            res_token = encrypt_aes(key, user_token, iv=IV)
            log.d( 'user_token: {}, len: {}, type: {}', user_token, len(user_token), type(user_token) )
            log.d( 'key: {}', key )
            log.d( 'res_token: {}, len: {}, type: {}', repr(res_token), len(res_token), type(res_token) )
            log.d( 'raw res_token: {}', binascii.b2a_hex(res_token) )
            res_token = base64.urlsafe_b64encode( res_token )
            log.d( 'base64 res_token: {}, len: {}', res_token, len(res_token) )
            # 2.
            new_key = MyRandom.randomStr(10)
            new_last_token = calmd5( str(int(time.time())) + MyRandom.randomStr(7) )
            res_last_token = encrypt_aes(new_key, new_last_token, iv=IV)
            # log.d( 'new_last_token: {}, len: {}, type: {}', new_last_token, len(new_last_token), type(new_last_token) )
            # log.d( 'key: {}', key )
            # log.d( 'raw res_last_token: {}, len: {}, type: {}', repr(res_last_token), len(res_last_token), type(res_last_token) )
            # log.d( 'raw res_token: {}', binascii.b2a_hex(res_last_token) )
            res_last_token = base64.urlsafe_b64encode( res_last_token )
            log.d('base64 res_last_token: {}, len: {}', res_last_token, len(res_last_token))
            log.d('auth_i success, update to new token: {}', new_last_token)
            # 返回
            ret = p.insert( 'UPDATE tb_toolkit_token SET last_token=%s WHERE token=%s',
                (new_last_token, user_token)
            )
            return jsonify({"code": '', "key": new_key, "token": res_token, "last_token": res_last_token})

    # 插件验证, U包
    @staticmethod
    def authentic_u(json_param):
        log.d(sys._getframe().f_code.co_name)
        token = request.headers.get('token', None)
        device_id = request.headers.get('device-id', None)
        build_variant = request.headers.get('build-variant', None)
        real_ip = request.headers.get('X-Real-Ip', None)
        log.d( "device-id: {}, ip: {}, build-variant: {}, token: {}", device_id,  real_ip, build_variant, token)
        log.d( "json_param = {}", json_param )
        key = json_param['key']
        encrypt_last_token = json_param['last_token']
        last_token = decrypt_aes(key, encrypt_last_token, iv=IV, usebase64=True)

        log.d('upload last token: {}, device-id: {}, ip: {}, build-variant: {}', last_token, device_id, real_ip, build_variant)
        # U包, 不需要判断 key 与库表中不一样, 而解密后last_token需要与库表中user_token相同
        with MysqlPool(WEBUTIL.mysql_config) as p:
            rows = p.select( 'SELECT token FROM tb_toolkit_token WHERE last_token=%s and is_enable=1',
                (last_token,)
            )
            if not rows:
                # 验证不通过
                log.e('auth_u fail!')
                return jsonify({"code": '验证失败'})
            if len(rows) > 1:
                log.e('user token duplicate!')
            row = rows[0]
            updated_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')   # "2017-10-11 00:00:00"
            ret = p.insert( 'UPDATE tb_toolkit_token SET update_time=%s WHERE last_token=%s',
                (updated_timestamp, last_token)
            )
            user_token = row['token'].encode('utf8') # note: 必须转为utf8, 默认是Unicode! 这样才能与java端保持一致!
            # { 
                # token = Bse64( AES(data=user_token, key=当前客户随机串, initVector=IV) ),
                # last_token = Bse64( AES(data=last_token, key=当前客户随机串, initVector=IV) )
            # }
            res_token = encrypt_aes(key, user_token, iv=IV, usebase64=True)
            # new_last_token = calmd5( str(int(time.time())) + MyRandom.randomStr(7) )
            new_key = MyRandom.randomStr(10)
            res_last_token = encrypt_aes(new_key, last_token, iv=IV, usebase64=True)
            log.d( 'res_last_token: {}, len: {}', res_last_token, len(res_last_token) )
            log.d( 'auth_u success' )
            return jsonify({"code": '', "key": new_key, "token": res_token, "last_token": res_last_token})


# http://139.199.171.40/wxapi/token.json?source=lynatgz
@wxapi.route('/token.json', methods=['GET'])
def create_token():
    log.d(sys._getframe().f_code.co_name)
    try:
        source = request.args.get('source', None)
        if source not in ['qqplugin', 'lynatgz']:
            return jsonify({"code": '不支持此source值'})

        device_id = request.headers.get('device-id', None)
        build_variant = request.headers.get('build-variant', None)
        real_ip = request.headers.get('X-Real-Ip', None)
        log.d( "device-id: {}, ip: {}, build-variant: {}", device_id,  real_ip, build_variant)
        token = hashlib.md5(str(int(time.time())) + MyRandom.randomStr(7)).hexdigest()
        md5_token = calmd5(token + TOKEN_SECRET)
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        openid = 'production'
        with MysqlPool(WEBUTIL.mysql_config) as p:
            ret = p.insert( 'INSERT INTO tb_toolkit_token(openid, token, md5_token, expires_at, source) VALUES (%s, %s, %s, %s, %s)',
                (openid, token, md5_token, expires_at, source)
            )
            if not ret:
                # 记录不变, 需谨慎处理!
                log.e( 'not insert tb_toolkit_token record, openid: {}, ret: {}', openid, ret )
                return jsonify({"code": '系统错误'})
        log.i( 'insert tb_toolkit_token success, openid: {}, token: {}, md5_token: {}, ret: {}', openid, token, md5_token, ret )

        # 返回加密后token
        new_key = MyRandom.randomStr(10)
        res_token = encrypt_aes(new_key, token, iv='xiaobaizhushou', usebase64=True)
        log.d( 'res_token: {}, len: {}', res_token, len(res_token) )
        return jsonify({"code": '', "key": new_key, "token": res_token, "md5_token": md5_token})
    except:
        log.e(traceback.format_exc())
        return jsonify({"code": '系统错误'})

