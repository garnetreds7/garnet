# -*- coding: utf-8 -*-

import re
import time
import json
import socket
import logging
import datetime
import threading
from struct import pack
from colorprint import ColorPrint

logger = logging.getLogger('filelog')

class ZhanqiDanmuHandler:
    def __init__(self, server_ip, server_port, danmu_server_data):
        self.server_ip = server_ip
        self.server_port = server_port
        self.data = danmu_server_data
        self.DANMU_AUTH_ADDR = (self.server_ip, self.server_port)

    def start(self):
        self.login()
        t_heart = threading.Thread(target = self.keeplive)
        t_heart.setDaemon(True)
        t_heart.start()
        t_danmu = threading.Thread(target = self.get_danmu)
        t_danmu.setDaemon(True)
        t_danmu.start()
        t_heart.join()
        t_danmu.join()

    def login(self):
        self.danmu_auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.danmu_auth_socket.settimeout(5)
        self.danmu_auth_socket.connect(self.DANMU_AUTH_ADDR)
        self.send_auth_loginreq_msg()

    def send_auth_loginreq_msg(self):
        data = json.dumps(self.data, separators=(',',':'))
        msg = b'\xbb\xcc' + b'\x00'*4 + pack('i', len(data)) + b'\x10\x27' + data.encode('ascii')
        # logger.debug(msg)
        self.danmu_auth_socket.sendall(msg)

    def recv_auth_msg(self):
        recv_socket = self.danmu_auth_socket.recv(1024)
        # logger.debug(recv_socket.decode('utf-8', 'ignore'))

    def keeplive(self):
        while True:
            msg = b'\xbb\xcc' + b'\x00'*8 + b'\x59\x27'
            self.danmu_auth_socket.sendall(msg)
            time.sleep(5)

    def get_danmu(self):
        while True:
            try:
                context = self.danmu_auth_socket.recv(1024)
                msg = re.search(b'\x10\x27({[^\x00]*})\x0a', context).group(1).decode('utf8', 'ignore')
                msg = json.loads(msg)
                if msg['cmdid'] == 'chatmessage':
                    name = msg['fromname']
                    content = msg['content']
                    level = msg['level'] if msg.has_key('level') else 0
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ip = msg['ip']
                    output_str = u'弹幕'+'|'+name+'('+ip+')'+'|Lv.'+str(level)+'|'+time+':'+content
                    ColorPrint(output_str).green()
            except Exception as e:
                logger.error(u'弹幕解析失败')
