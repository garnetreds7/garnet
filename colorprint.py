# -*- coding: utf-8 -*-

import sys
import ctypes

STD_OUTPUT_HANDLE = -11

FOREGROUND_BLUE = 0x01
FOREGROUND_GREEN = 0x02
FOREGROUND_RED = 0x04


class ColorPrint:

    def __init__(self, content):
        self.content = content
        self.colorhandler = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

    def set_cmd_color(self, color, handle):
        ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)

    def reset_color(self):
        self.set_cmd_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE, self.colorhandler)

    def green(self):
        self.set_cmd_color(FOREGROUND_GREEN, self.colorhandler)
        print self.content
        self.reset_color()

    def red(self):
        self.set_cmd_color(FOREGROUND_RED, self.colorhandler)
        print self.content
        self.reset_color()

    def blue(self):
        self.set_cmd_color(FOREGROUND_BLUE, self.colorhandler)
        print self.content
        self.reset_color()
