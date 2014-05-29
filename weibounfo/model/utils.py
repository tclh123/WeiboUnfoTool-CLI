# coding=utf-8

from datetime import datetime


def weibo_date(string):
    return datetime.strptime(string,"%a %b %d %H:%M:%S +0800 %Y")
