#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import logging
from xml.etree import ElementTree
from .log import logger
from .util import rules_path, to_bool

# Match-Mode
mm_find_extension = 'find-extension'
mm_function_param_controllable = 'function-param-controllable'
mm_regex_param_controllable = 'regex-param-controllable'
mm_regex_only_match = 'regex-only-match'
match_modes = [
    mm_regex_only_match,
    mm_regex_param_controllable,
    mm_function_param_controllable,
    mm_find_extension
]


class Rule(object):
    """
        rules规则文件类
    """
    def __init__(self):
        self.rules_path = rules_path

    @property
    def languages(self):
        """
        Get all languages
        :return:
        {
            'php':{
                'chiefly': 'true',
                'extensions':[
                    '.php',
                    '.php3',
                    '.php4',
                    '.php5'
                ]
            }
        }
        """
        language_extensions = {}
        xml_languages = read_xml('languages.xml')
        if xml_languages is None:
            logger.critical('languages read failed!!!')
            return None
        for language in xml_languages:
            l_name = language.get('name').lower()
            l_chiefly = 'false'
            if language.get('chiefly') is not None:
                l_chiefly = language.get('chiefly')
            language_extensions[l_name] = {
                'chiefly': l_chiefly,
                'extensions': []
            }
            for lang in language:
                l_ext = lang.get('value').lower()
                language_extensions[l_name]['extensions'].append(l_ext)
        return language_extensions

    def rules(self, rules=None):
        """
        Get all rules
        如果rules不为空，加载rules规则，否则加载全部
        :return: dict
        """
        vulnerabilities = []
        files = []
        extension = '.xml'
        if rules != "None" and len(rules) > 0:
            rules = rules.split(",")
            for sr in rules:
                if re.match(r'^(cvi|CVI)-\d{6}(\.xml)?', sr.strip()):
                    if extension not in sr:
                        sr += extension
                    files.append(sr)
                    logger.info("sr == " + sr)
        else:
            all_files = os.listdir(self.rules_path)
            for f in all_files:
                if re.match(r'^(cvi|CVI)-\d{6}(\.xml)?', f.strip()):
                    files.append(f)
            logger.info("规则文件总个数：{n}".format(n=len(files)))
        for vulnerability_name in files:
            # VN: CVI-190001.xml
            v_path = os.path.join(self.rules_path, vulnerability_name.replace('cvi', 'CVI'))
            if vulnerability_name.lower()[0:7] == 'cvi-999' or 'cvi' not in v_path.lower():
                logger.debug('filter dep rules')
                continue
            if os.path.isfile(v_path) is not True or '.xml' not in v_path.lower():
                logger.warning('Not regular rule file {f}'.format(f=v_path))
                continue

            # rule information
            rule_info = {
                'id': None,
                'file': v_path,
                'name': None,
                'language': None,
                'match': None,
                'match-mode': 'regex-only-match',
                'match2': None,
                'match2-block': None,
                'repair': None,
                'repair-block': None,
                'level': None,
                'solution': None,
                'test': {
                    'true': [],
                    'false': []
                },
                'status': False,
                'author': None
            }
            xml_rule = read_xml(v_path)
            if xml_rule is None:
                logger.critical('rule read failed!!! ({file})'.format(file=v_path))
                continue
            cvi = v_path.lower().split('cvi-')[1][:6]
            rule_info['id'] = cvi
            for x in xml_rule:
                if x.tag == 'name':
                    rule_info['name'] = x.get('value')
                if x.tag == 'language':
                    rule_info['language'] = x.get('value')
                if x.tag == 'status':
                    rule_info['status'] = to_bool(x.get('value'))
                if x.tag == 'author':
                    name = x.get('name').encode('utf-8')
                    email = x.get('email')
                    rule_info['author'] = '{name}<{email}>'.format(name=name, email=email)
                if x.tag in ['match', 'match2', 'repair']:
                    if x.text is not None:
                        rule_info[x.tag] = x.text.strip()
                    if x.tag == 'match':
                        if x.get('mode') is None:
                            logger.warning('unset match mode attr (CVI-{cvi})'.format(cvi=cvi))
                        if x.get('mode') not in match_modes:
                            logger.warning('mode exception (CVI-{cvi})'.format(cvi=cvi))
                        rule_info['match-mode'] = x.get('mode')
                    elif x.tag == 'repair':
                        rule_info['repair-block'] = block(x.get('block'))
                    elif x.tag == 'match2':
                        rule_info['match2-block'] = block(x.get('block'))
                if x.tag == 'level':
                    rule_info['level'] = x.get('value')
                if x.tag == 'solution':
                    rule_info['solution'] = x.text.strip()
                if x.tag == 'test':
                    for case in x:
                        case_ret = case.get('assert').lower()
                        case_test = ''
                        if case.text is not None:
                            case_test = case.text.strip()
                        if case_ret in ['true', 'false']:
                            rule_info['test'][case_ret].append(case_test)
            vulnerabilities.append(rule_info)
        return vulnerabilities


def read_xml(filename):
    """
    读取xml file,返回json字符串
    :param filename:
    :return:
    """
    path = os.path.join(rules_path, filename)
    try:
        tree = ElementTree.parse(path)
        return tree.getroot()
    except Exception as e:
        logger.critical("xml file {f} read error:{m}".format(f=filename, m=e.message))
        return None


def block(index):
    default_index_reverse = 'in-function'
    default_index = 0
    blocks = {
        'in-function-up': 0,
        'in-function-down': 1,
        'in-current-line': 2,
        'in-function': 3,
        'in-class': 4,
        'in-class-up': 5,
        'in-class-down': 6,
        'in-file': 7,
        'in-file-up': 8,
        'in-file-down': 9
    }
    if isinstance(index, int):
        blocks_reverse = dict((v, k) for k, v in blocks.items())
        if index in blocks_reverse:
            return blocks_reverse[index]
        else:
            return default_index_reverse
    else:
        if index in blocks:
            return blocks[index]
        else:
            return default_index


def get_includes(lang):
    """
    获取lang语言的后缀列表
    :param lang:
    :return:
    """
    include = []
    language = Rule().languages[lang]
    lang_extensions = language["extensions"]
    for extension in lang_extensions:
        inc = "--include=*" + extension
        include.append(inc)
    return include


def get_extensions(lang):
    """
    返回lang语言的后缀
    :param lang:
    :return:
    """
    language = Rule().languages[lang]
    return language["extensions"]