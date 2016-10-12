# -*- coding: utf-8 -*-

import re
import time
import datetime
import uuid
import socket
import hashlib
import threading
import logging
from config import *
from Queue import Queue
from concurrent.futures import ThreadPoolExecutor
from colorprint import ColorPrint

def str_timestamp():
    return str(int(time.time()))

logger = logging.getLogger('danmu')
logger.addHandler(logging.FileHandler('danmu.log'))
logger.setLevel(logging.DEBUG)
fetched_msg_queue = Queue()

class DouyuDanmuHandler:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.DANMU_ADDR = (ADDR_DANMU_SERVER, PORT_DANMU_SERVER[0])
        self.DANMU_AUTH_ADDR = (server_ip, int(server_port))
        self.UUID = str(uuid.uuid4()).replace('-', '')
        self.roomid = str(room_status['id'])

    def start(self):
        self.login()
        if self.state_live == 'offline':
            print u'主播已离开,请退出'
        else:
            print u'主播正在直播,获取弹幕中...'
            # 创建发送心跳socket的线程
            t = threading.Thread(target = self.keeplive)
            # 将这个线程设置为主线程杀死
            t.setDaemon(True)
            t.start()
            t_pool = ThreadPoolExecutor(config['total_thread'])
            pipeline = t_pool.submit(self.consume_msg, fetched_msg_queue)
            for i in range(config['total_thread']):
                t_pool.submit(self.fetch_msg)
            print(pipeline.result())

    def fetch_msg(self):
        while True:
            msg_recv = self.danmu_recv()
            fetched_msg_queue.put(msg_recv)

    def consume_msg(self, msg_queue):
        while True:
            msg = msg_queue.get()
            self.danmu_parse(msg)

    def danmu_parse(self, msg):
        if 'type@=' not in msg:
            logger.debug(u'收到的消息中不包含type字段:' + msg)
        elif 'type@=error' in msg:
            logger.error(u'错误消息,弹幕获取失败')
        else:
            content = msg.replace('@S','/').replace('@A=',':').replace('@=',':')
            try:
                msg_type = re.search('type:(.+?)\/', content).group(1)
                if msg_type == 'chatmsg':
                    sendid = re.search('\/uid:(.+?)\/', content).group(1) if 'uid:' in content else 'UNKNOWN'
                    name = re.search('\/nn:(.+?)\/', content).group(1) if 'nn:' in content else 'UNKNOWN'
                    letters = re.search('\/txt:(.+?)\/', content).group(1) if 'txt:' in content else 'UNKNOWN'
                    level = re.search('\/level:(.+?)\/', content).group(1) if 'level:' in content else 'UNKNOWN'
                    client_type = re.search('\/ct:(.+?)\/', content).group(1) if 'ct:' in content else "UNKNOWN"  # ct 默认值 0 web
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    output_str = u'弹幕'+'|'+name+'('+sendid+')'+'|'+level+'|'+time+':'+letters
                    ColorPrint(output_str).green()
            except Exception as e:
                logger.error(u'弹幕解析失败')

    def login(self):
        #弹幕服务器登录socket，创建一个TCP socket
        self.danmu_auth_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET表示服务器之间通信， SOCK_STREAM流式socket，for TCP
        self.danmu_auth_socket.connect(self.DANMU_AUTH_ADDR)
        self.danmu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.danmu_socket.connect(self.DANMU_ADDR)
        # 发送弹幕服务器登录信息
        self.send_auth_loginreq_msg()
        # 接收到弹幕服务器登录信息的反馈
        msg_recv = self.auth_recv()
        if STATE_OFFLINE in msg_recv:
            # 如果当前房间主播没有开播
            self.state_live = 'offline'
            room_status['live_stat'] = self.state_live
        else:
            # 主播正在直播
            self.state_live = 'online'
            room_status['live_stat'] = self.state_live
            # 提取房间信息
            self.username = re.search(REGEX_USERNAME, msg_recv).group(1)
            msg_recv = self.auth_recv()
            self.gid = re.search(REGEX_GID, msg_recv).group(1)
            self.weight = re.search(REGEX_WEIGHT, msg_recv).group(1)
            self.fans = re.search(REGEX_FANS_COUNT, msg_recv).group(1)
            self.send_qrl_msg()
            msg_recv = self.auth_recv()
            # self.send_auth_keeplive_msg()
            # msg_recv = self.auth_recv()
            self.send_danmu_loginreq_msg()
            msg_recv = self.danmu_recv()
            self.send_danmu_join_group_msg()

    def keeplive(self):
        while True:
            self.send_auth_keeplive_msg()
            self.send_danmu_keeplive_msg()
            print u'发送心跳包...'
            time.sleep(40)

    def send_auth_loginreq_msg(self):
        vk = self.get_vk()
        data = 'type@=loginreq/username@=/ct@=0/password@=/roomid@=' + self.roomid + '/devid@=' + self.UUID + '/rt@=' + str_timestamp() + '/vk@=' + vk + '/ver@=20150929/'
        msg = self.douyu_message(data)
        self.danmu_auth_socket.sendall(msg)

    def send_qrl_msg(self):
        data = 'type@=qrl/rid@=' + self.roomid + '/'
        msg = self.douyu_message(data)
        self.danmu_auth_socket.sendall(msg)

    def send_auth_keeplive_msg(self):
        data = 'type@=keeplive/tick@=' + str_timestamp() + '/vbw@=0/k@=19beba41da8ac2b4c7895a66cab81e23/'
        msg = self.douyu_message(data)
        self.danmu_auth_socket.sendall(msg)

    def send_danmu_keeplive_msg(self):
        data = 'type@=keeplive/tick@=' + str_timestamp() + '/'
        msg = self.douyu_message(data)
        self.danmu_socket.sendall(msg)

    def send_danmu_loginreq_msg(self):
        data = 'type@=loginreq/username@=' + self.username + '/password@=1234567890123456/roomid@=' + self.roomid + '/'
        msg = self.douyu_message(data)
        self.danmu_socket.sendall(msg)

    def send_danmu_join_group_msg(self):
        data = 'type@=joingroup/rid@=' + self.roomid + '/gid@=' + self.gid + '/'
        msg = self.douyu_message(data)
        self.danmu_socket.sendall(msg)

    def auth_recv(self):
        return self.parse_content(self.danmu_auth_socket.recv(4000))

    def danmu_recv(self):
        return self.parse_content(self.danmu_socket.recv(4000))

    def parse_content(self, msg_recv):
        content = msg_recv[12:-1].decode('utf-8', 'ignore')
        return content

    def get_vk(self):
        time_str = str_timestamp()
        vk = hashlib.md5(time_str + '7oE9nPEG9xXV69phU31FYCLUagKeYtsF' + self.UUID).hexdigest()
        return vk

    def douyu_message(self, data):
        length = bytearray([len(data)+9, 0x00, 0x00, 0x00])
        code = length
        magic = bytearray([0xb1, 0x02, 0x00, 0x00])
        content = bytes(data.encode('utf-8'))
        end = bytearray([0x00])
        msg = length + code + magic + content + end
        return msg

    def str_align_left(self, raw_str, max_length, fill_char):
        pass
