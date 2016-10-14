# -*- coding: utf-8 -*-

import re
import json
import urllib
import urllib2
import logging
from config import *
from danmuhandler import *

logger = logging.getLogger('filelog')

def json_value(raw_json):
    try:
        v_json = json.loads(raw_json)
    except ValueError as e:
        return False
    return v_json

class Douyu:

    def __init__(self, url):
        if DOUYU_INDEX not in url:
            url = DOUYU_INDEX + url
        self.url = url
        logger.debug(u'Live room address: '+self.url)

    def start(self):
        server_ip, server_port = self.get_info(self.url)
        if server_ip == False or server_port == False:
            print u"房间信息读取错误"
        else:
            print u"弹幕服务器登录地址："+server_ip+":"+server_port
            self.get_danmu(server_ip, server_port)

    def get_info(self, url):
        html = urllib2.urlopen(url).read().decode()
        room_info = re.search(REGEX_ROOM_INFO, html).group(1)
        server_info = re.search(REGEX_SERVER_INFO, html).group(1)
        format_room_info = json_value(room_info)
        format_server_info = json_value(server_info)

        if format_room_info!=False and format_server_info!=False:
            room = room_status
            room['id'] = format_room_info['room_id']
            room['name'] = format_room_info['room_name']
            room['gg_show'] = format_room_info['room_gg']['show']
            room['owner_uid'] = format_room_info['owner_uid']
            room['owner_name'] = format_room_info['owner_name']
            room['room_url'] = format_room_info['room_url']
            room['near_show_time'] = format_room_info['near_show_time']
            room['tags'] = []
            room_all_tags = format_room_info['all_tag_list']
            if room_all_tags != None:
                if format_room_info['room_tag_list'] != None:
                    tags_size = len(format_room_info['room_tag_list'])
                    for i in range(0, tags_size):
                        room['tags'].append(room_all_tags[format_room_info['room_tag_list'][i]]['name'])
                else:
                    print u'房间无标签'
            servers = json_value(urllib.unquote(format_server_info["server_config"]))
            server_ip = servers[0]['ip']
            server_port = servers[0]['port']
            return server_ip, server_port
        else:
            return False, False

    def get_danmu(self, server_ip, server_port):
        client = DouyuDanmuHandler(server_ip, server_port)
        client.start()
