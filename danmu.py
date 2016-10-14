# -*- coding: utf-8 -*-

from douyu import Douyu
from zhanqi import Zhanqi
from config import config

def command():
    platform = raw_input('Enter Platform:1.Douyu 2.Zhanqi:')
    # config['platform'] = platform if len(platform)==1 and platform in '12' else '2'
    config['platform'] = platform if len(platform)==1 and platform in '12' else None
    room = raw_input(u'Enter Room ID:') if config['platform']!=None else None
    # room = '9527'

    if config['platform'] == '1':
        config['platform'] = 'douyu'
        config['room_url'] = room
        dy = Douyu(url = config['room_url'])
        dy.start()
    elif config['platform'] == '2':
        config['platform'] = 'zhanqi'
        config['room_url'] = room
        xm = Zhanqi(url = config['room_url'])
        xm.start()
    else:
        print u'平台选择错误,正在退出...'

def main():
    command()

if __name__ == '__main__':
    main()
