# -*- coding: utf-8 -*-

import re
import json
import time
import base64
import urllib2
import logging
import requests
from config import *
from zhanqihandler import *

logger = logging.getLogger('filelog')

class Zhanqi:

    def __init__(self, url):
        if XIONGMAO_INDEX not in url:
            url = ZHANQI_INDEX + url
        self.url = url
        logger.debug(self.url)

    def start(self):
        server_ip, server_port, danmu_data = self.get_url_info(self.url)
        if server_ip == False or server_port == False:
            print u'解析弹幕服务器地址失败...'
            logger.error(u'解析弹幕服务器地址失败...')
        else:
            logger.debug(server_ip+':%d'%server_port)
            client = ZhanqiDanmuHandler(server_ip, server_port, danmu_data).start()

    def get_url_info(self, url):

        html = urllib2.urlopen(url).read().decode()
        info = re.search('oRoom = ({.+?});[\s]*?window.bClose', html).group(1)
        format_info = self.json_value(info)

        if format_info != False:
            danmu_server_url = 'http://www.zhanqi.tv/api/public/room.viewer'
            danmu_get_params = {
                'uid': format_info['uid'],
                '_t' : int(time.time()/60),
            }
            # logger.debug(danmu_get_params)
            danmu_server_info = requests.get(danmu_server_url, danmu_get_params).json()
            danmu_server_info['id'] = format_info['id']
            # logger.debug(danmu_server_info)

            data = {
                'roomid'        : int(danmu_server_info['id']),
                'gid'           : danmu_server_info['data']['gid'],
                'sid'           : danmu_server_info['data']['sid'],
                'ssid'          : danmu_server_info['data']['sid'],
                'timestamp'     : danmu_server_info['data']['timestamp'],
                'uid'           : 0,
                'cmdid'         : 'loginreq',
                'fhost'         : 'zhanqi.tool',
                'develop_date'  : '2015-06-07',
                'nickname'      : '',
                'thirdaccount'   : '',
                't'             : 0,
                'fx'            : 0,
                'ver'           : 2,
                'vod'           : 0,
            }

            # data = {
            #     'roomid'        : int(danmu_server_info['id']),
            #     'gid'           : danmu_server_info['data']['gid'],
            #     'sid'           : danmu_server_info['data']['sid'],
            #     'ssid'          : danmu_server_info['data']['sid'],
            #     'timestamp'     : danmu_server_info['data']['timestamp'],
            #     'uid'           : 0,
            #     'cmdid'         : 'loginreq',
            #     'fhost'         : '',
            #     # 'develop_date'  : '2015-06-07',
            #     'nickname'      : '',
            #     'thirdaccount'  : '',
            #     'tagid'         : 0,
            #     't'             : 0,
            #     'fx'            : 0,
            #     'ver'           : 12,
            #     'hideslv'       : 0,
            #     'ajp'           : 0,
            # }

            servers = format_info['flashvars']['Servers']
            servers = self.json_value(base64.b64decode(servers))['list'][0]
            return servers['ip'], servers['port'], data
        else:
            return False, False, None

    def json_value(self, raw_json):
        try:
            v_json = json.loads(raw_json)
        except ValueError as e:
            logger.error('To json occured error: '+raw_json)
            return False
        return v_json
