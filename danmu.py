# -*- coding: utf-8 -*-
from douyu import Douyu
from config import config

def command():
    dy = Douyu(url = config["room_url"])
    dy.start()

def main():
    command()

if __name__ == '__main__':
    main()
