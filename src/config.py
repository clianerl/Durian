#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    该类用于获取config配置文件参数
"""
import os
import logging
import traceback
from .log import logger
from .util import config_path
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


class Config(object):
    """
    用于获取配置文件属性
    """
    def __init__(self, level1=None, level2=None):
        self.level1 = level1
        self.level2 = level2
        if level1 is None and level2 is None:
            return
        config = ConfigParser()
        config.read(config_path)
        value = None
        try:
            value = config.get(level1, level2)
        except Exception as e:
            traceback.print_exc()
            logger.critical("./configs file configure failed. {u}\nError: {e}".format(u='https://github.com/DurianCoder/Durian', e=e.message))
        self.value = value


