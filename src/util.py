#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import hashlib
import random
import string
from xml.etree import ElementTree
import logging
from .log import logger

# 获取项目、扫描结果、日志、配置等文件路径
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
os.chdir(project_path)
result_path = os.path.join(project_path, "result")
log_path = os.path.join(project_path, "logs")
config_path = os.path.join(project_path, "config")
rules_path = os.path.join(project_path, "rules")


def to_bool(value):
    """Converts 'something' to boolean. Raises exception for invalid formats"""
    if str(value).lower() in ("on", "yes", "y", "true", "t", "1"):
        return True
    if str(value).lower() in ("off", "no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def save_json_to_file(filename, data):
    """
    将data转化为json格式化写入filename
    :param filename:
    :param data:
    :return:
    """
    with open(filename, "w+") as f:
        f.write(json.dumps(data, ensure_ascii=False, sort_keys=False, indent=4))


def clear_directory(path, max_num):
    """
    当path路径下文件超过max_num个，清空文件
    :param path:
    :param max_num:
    :return:
    """
    logger.info("result path == {p}".format(p=path))
    logger.info("result max_num == {m}".format(m=max_num))
    files = os.listdir(path)
    file_nums = len(files)
    logger.info("result files size == {s}".format(s=file_nums))
    if file_nums > int(max_num):
        logger.info("result下文件大于{s}个，清空...".format(s=max_num))
        for f in files:
            result_file = os.path.join(path, f)
            if os.path.isfile(result_file):
                os.remove(os.path.join(path, f))
    else:
        logger.info("result file nums < 5   ...")
        pass


def md5(content):
    """
    MD5 Hash
    :param content:
    :return:
    """
    content = content.encode('utf8')
    return hashlib.md5(content).hexdigest()


def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    """choice是获取chars的任意一个元素，_代表迭代但不访问"""
    return ''.join(random.choice(chars) for _ in range(size))


def get_sid(target):
    """根据输入的target经过MD5加密，末尾加上5位随机数"""
    target = md5(target)[:5]
    sid = "{pre}{sid}{r}".format(pre="s",sid=target,r=random_generator())
    return sid.lower()


def read_rule(filename):
    """读取xml file,返回json字符串"""
    path = os.path.join(rules_path, filename)
    try:
        tree = ElementTree.parse(path)
        return tree.getroot()
    except Exception as e:
        logger.critical("xml file {f} read error:{m}".format(f=filename,m=e.message))
        return None


# 判断文件f的line_num行上面是否有写文档注释
# todo 将文档注释标识符写入配置文件提高代码通用性，将方法写到util.py中
def read_before_line(f, fun_line_num):
    f = open(f, "r")
    line_num = int(fun_line_num)
    # readlines()互斥锁
    file_list = f.readlines()

    while line_num > 1:
        # 索引减一
        line_num -= 1
        # 访问上一行减一
        line_content = file_list[line_num - 1].strip()
        if line_content == '':
            continue
        # elif line_content[:7] == "virtual":
        #     # 相关联的比较简短的多个虚函数，一起写注释
        #     continue
        elif line_content.endswith('*/') or line_content[:2] == "//":
            return True
        else:
            # 没有文档注释
            return False
    return False


