#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import json
import time
import traceback
import subprocess
import multiprocessing
import logging
# 导入clang 的 lib bindings 模块
import clang
from clang.cindex import CursorKind

from .rule import Rule, get_includes, get_extensions
from .clangtool import clang_detect_file
from .log import logger
from .send_mail import send_mail
from .config import Config
from .util import read_before_line, result_path, get_sid, save_json_to_file, clear_directory


# 检查结果
check_result = {}
var_reevaluate_result = []
log_result = []
static_rule_result = []
virtual_result = []
# ../CodeCheckingTool/result 目录
result_path = os.path.join(os.getcwd(), "result")
pool = None


def start(target, output, special_rules):
    """扫描 .h 虚函数没有写文档注释  ---> .logicservice 没有打印日志  -----> 变量重复赋值"""

    global pool
    pool = multiprocessing.Pool()
    sid = get_sid(target)

    check_result["sid"] = sid
    check_result["target"] = target
    check_result["analysis"] = {}
    check_result["analysis_nums"] = {}

    logger.info("开始扫描...")
    # 扫描规则文件
    scan_rules(target, special_rules)

    # 统计扫描结果
    for a_name, a_result in check_result["analysis"].items():
        check_result["analysis_nums"][a_name] = len(a_result)

    # 将结果保存到result中，result中文件超过max个，清空
    clear_directory(result_path, Config("result", "max").value)
    result_file = os.path.join(result_path, sid)
    save_json_to_file(result_file, check_result)

    # 发送邮件
    send_mail(target, result_file, output, check_result)


def scan_rules(target, special_rules):
    """
    扫描规则
    :param target
    :param special_rules: 输入的-r 规则以','隔开
    :return:
    """
    r = Rule()
    vulnerabilities = r.rules(special_rules)
    logger.info("规则条数为{n}".format(n=len(vulnerabilities)))

    def store_rule_result(data_list):
        """
        将单条规则结果添加到扫描结果
        :param data_list ---> [l_name, data]
        :return:
        """
        global var_reevaluate_result
        global log_result
        global static_rule_result
        global virtual_result
        if data_list is not None:
            check_result["analysis"][data_list[0]] = data_list[1]
            # 每次扫描后，加扫描结果清空
            var_reevaluate_result = []
            log_result = []
            static_rule_result = []
            virtual_result = []

    """
    当没有扫描 CVI-120 开头的检查变量重复赋值等耗时检查时，每扫描一条规则开启一个进程
    否则，在扫描耗时规则内部，每扫描一个文件开启一个进程
    """
    if "cvi-120" not in special_rules and special_rules != "None":
        scan_rule_pool = multiprocessing.Pool()
        # 每条规则开启一个进程
        for vulnerability in vulnerabilities:
            scan_rule_pool.apply_async(scan_single_rule, args=(target, vulnerability,), callback=store_rule_result)
        scan_rule_pool.close()
        scan_rule_pool.join()
    else:
        for vulnerability in vulnerabilities:
            store_rule_result(scan_single_rule(target, vulnerability))


def scan_single_rule(target, vulnerability):
    """
    单条规则扫描，返回扫描结果
    cvi-100  ----> 日志打印规则
    cvi-110  ----> 函数注释检查规则
    cvi-120  ----> 变量重复赋值规则
    cvi-200  ----> 普通静态规则
    :param target:
    :param vulnerability:
    :return:
    """

    if vulnerability["id"][:3] == "100":
        # 日志打印规则扫描,扫描出该语言后缀没有打印该条日志的文件
        start_scan_log_check(target, vulnerability)
        return [vulnerability["name"], log_result]

    elif vulnerability["id"][:3] == "110":
        # 函数注释检查规则扫描
        start_scan_virtual(target, vulnerability)
        return [vulnerability["name"], virtual_result]

    elif vulnerability["id"][:3] == "120":
        # 变量重复赋值规则扫描
        start_scan_var_reevaluate(target, vulnerability)
        return [vulnerability["name"], var_reevaluate_result]

    elif vulnerability["id"][:3] == "200":
        # 普通静态规则扫描
        start_scan_static_rules(target, vulnerability)
        return [vulnerability["name"], static_rule_result]


def start_scan_static_rules(target, vulnerability):
    """
    扫描静态规则打印耗时
    :param target:
    :param vulnerability:
    :return:
    """
    logger.info("{r}静态规则扫描开始...".format(r=vulnerability["id"]))
    t1 = time.time()
    scan_static_rule(target, vulnerability)
    t2 = time.time()
    logger.info("{r}静态规则扫描结束，共耗时{t}s".format(r=vulnerability["id"],t=(t2 - t1)))
    # logger.info("静态规则结果为:{r}".format(r=str(static_rule_result)))


def start_scan_log_check(target, vulnerability):
    """
    开始扫描日志规则，打印耗时
    :param target:
    :param vulnerability:
    :return:
    """
    logger.info("{r}日志规则扫描开始...".format(r=vulnerability["id"]))
    t1 = time.time()
    scan_log_print(target, vulnerability)
    t2 = time.time()
    logger.info("{r}日志规则扫描结束，共耗时{t}s".format(r=vulnerability["id"],t=(t2 - t1)))


def start_scan_virtual(target, vulnerability):
    """
    开始扫描虚函数注释
    :param target:
    :param vulnerability:
    :return:
    """
    logger.info("{r}函数注释规则扫描开始...".format(r=vulnerability["id"]))
    t1 = time.time()
    scan_virtual_annotation(target, vulnerability)
    t2 = time.time()
    logger.info("{r}函数注释规则扫描结束，共耗时{t}s".format(r=vulnerability["id"], t=(t2 - t1)))


def start_scan_var_reevaluate(target, vulnerability):
    """
    开始扫描变量重复赋值
    :param target:
    :param vulnerability:
    :return:
    """
    logger.info("{r}深度规则扫描开始...".format(r=vulnerability["id"]))
    t1 = time.time()
    deep_src = os.path.join(target, "src")
    # 只扫描-t 路径下的src目录
    if os.path.exists(deep_src):
        scan_var_reevaluate(os.path.join(target, "src"), vulnerability)
    else:
        logger.warning("-t路径下没有src目录，跳过cvi-{r}.xml规则扫描...".format(r=vulnerability["id"]))
    t2 = time.time()
    pool.close()
    pool.join()
    logger.info("{r}深度规则扫描结束，共耗时{t}s".format(r=vulnerability["id"], t=(t2 - t1)))


def scan_static_rule(target, vulnerability):
    """
    扫描单条静态规则
    :param target:
    :param vulnerability:
    :return:
    """
    param = ["/bin/grep", "-s", "-n", "-r"] + [vulnerability["match"], target]
    # logger.info("static command : {c}".format(c=str(param)))
    try:
        p = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # communicate(standard in、timeout) return stdout and std err
        result, error = p.communicate()
        # logger.info("static rule scan result : {r}".format(r=result))
        if result == "" or result is None:
            logger.info(" > continue(out)...")
        else:
            origin_vulnerabilities = result.strip().split("\n")
            for origin_vulnerability in origin_vulnerabilities:
                origin_vulnerability = origin_vulnerability.strip()
                if origin_vulnerability == '':
                    logger.debug(' > continue(in)...')
                    continue
                file_path = origin_vulnerability.split(":")[0]
                code_line = origin_vulnerability.split(":")[1]
                code_content = origin_vulnerability.split(":")[2]
                static_dict = {"title": vulnerability["name"], "file_path": file_path, "line_num": code_line,
                               "code_content": code_content, "solution": vulnerability["solution"].strip()}
                static_rule_result.append(static_dict)
    except Exception as e:
        traceback.print_exc()
        logger.critical('scan static rules exception ({e})'.format(e=e.message))
        return


def scan_log_print(target, vulnerability):
    """
    扫描日志规则，将没有打印日志的文件扫描出来
    :param target:
    :param vulnerability:
    :return:
    日志打印规则
    log_rule_dict = {"没有打印进入日志": ".*\(.*进入\[.*_.*\].*\)",
                     "没有打印输入包文信息": "\[输入包文信息打印\]",
                     "没有打印函数调用报错": "\[函数调用报错打印\]\[.*\]",
                     "没有打印离开日志": ".*\(.*离开\[.*_.*\].*\)",
                     "没有打印调用耗时": "\[耗时打印\]\[.*_.*\]\[@tmp_mill\]"}
    """

    include = get_includes(vulnerability["language"])
    param = ["/bin/grep", "-s", "-n", "-r"] + include + [vulnerability["match"], target]
    # logger.info("查找命令：{c}".format(c=str(param)))
    try:
        p = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = p.communicate()  # communicate(stdin、timeout) return stdout and std err
        inc_file = []  # 有打印日志规则的文件集合
        if result == "" or result is None:
            logger.info(" > 没有匹配到该日志规则结果(out),continue...")
            pass
        else:
            origin_vulnerabilities = result.strip().split("\n")
            for origin_vulnerability in origin_vulnerabilities:
                origin_vulnerability = origin_vulnerability.strip()
                if origin_vulnerability == '':
                    logger.debug(' > 没有匹配到该日志规则结果(in),continue...')
                    continue
                # 将有打印日志的文件路径加入inc_file集合中
                file_path = origin_vulnerability.split(":")[0]
                inc_file.append(file_path)
        # 将没有在inc_file中的后缀文件添加到check_result中
        append_no_logfile(target, inc_file, vulnerability)
    except Exception as e:
        traceback.print_exc()
        logger.critical('scan log print exception ({e})'.format(e=e.message))
        return


# 递归将不符合规则的文件添加到返回list中
def append_no_logfile(directory, file_list, vulnerability):
    """
    扫描target,将不在file_list中的文件打印
    :param directory:
    :param file_list:
    :param vulnerability:
    :return:
    """
    files = os.listdir(directory)
    for f in files:
        extensions = get_extensions(vulnerability["language"])
        filename = f
        idx = f.find(".")
        if idx == -1 or filename[idx:] in extensions:
            f = os.path.join(directory, f)
            if os.path.isfile(f):
                if f in file_list:
                    continue
                elif filename[idx:] in extensions:
                    log_dict = {"title": vulnerability["name"], "file_path": str(f)}
                    log_result.append(log_dict)
            elif os.path.isdir(f):
                append_no_logfile(f, file_list, vulnerability)


def store(file_var_reevaluate_list):
    """
    将异步检查结果添加到check_result["analysis"]
    :param file_var_reevaluate_list:
    :return:
    """
    if len(file_var_reevaluate_list) > 0:
        var_reevaluate_result.append(file_var_reevaluate_list)


def detect_single_file_reevaluate(directory, f, vulnerability):
    """
    detective single file reevaluate
    :param directory:
    :param f:
    :param vulnerability:
    :return:
    """
    f = os.path.join(directory, f)
    if os.path.isfile(f):
        # clang_detect_file(index, f)
        pool.apply_async(clang_detect_file, args=(f, vulnerability), callback=store)
    elif os.path.isdir(f):
        scan_var_reevaluate(f, vulnerability)


def scan_var_reevaluate(directory, vulnerability):
    """
    递归扫描target中的cpp文件，识别变量重复赋值缺陷、
    todo 多线程提高性能
    :param directory:
    :param vulnerability:
    :return:
    """
    files = os.listdir(directory)
    for f in files:
        lang_extensions = get_extensions(vulnerability["language"])
        idx = f.find(".")
        if idx == -1 or f[idx:] in lang_extensions:
            detect_single_file_reevaluate(directory, f, vulnerability)
        else:
            continue


def scan_virtual_annotation(target, vulnerability):
    """
    输入targer路径，返回一个没有文档注释的虚函数的列表list
    :param target:
    :param vulnerability:
    :return:
    """
    # 虚函数只要检查src目录下的.h文件
    target = os.path.join(target, "src")
    # todo 将grep封装
    include = get_includes(vulnerability["language"])
    param = ["/bin/grep", "-s", "-n", "-r"] + include + [vulnerability["match"], target]
    # param = ["/bin/grep", "-s", "-n", "-r"] + ["--include=*.logicservice"] + ["LogFlow\(.*进入\[LS_.*\].*\)", target]
    try:
        p = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, error = p.communicate()  # communicate(stdin、timeout) return stdout and std err
        if result == "" or result is None:
            return []
        else:
            origin_vulnerabilities = result.strip().split("\n")
            for origin_vulnerability in origin_vulnerabilities:
                origin_vulnerability = origin_vulnerability.strip()
                # 如果匹配到的行以//和/*开头则为注释掉的
                if origin_vulnerability == '' or origin_vulnerability.split(":")[2][:2] in ["//", "/*", "# "]:
                    logger.debug(' > continue...')
                    continue
                # 获取虚函数内容，去掉;后面的注释等内容
                code_content = origin_vulnerability.split(":")[2]
                code_line = origin_vulnerability.split(":")[1]
                file_path = origin_vulnerability.split(":")[0]
                code_content_list = code_content.split(";")
                code_content = code_content_list[0]
                have_annotation = read_before_line(file_path, code_line)
                if not have_annotation:
                    ano_dict = {"title": vulnerability["name"], "file_path": file_path, "line_num": code_line,
                                "code_content": code_content, "solution": vulnerability["solution"].strip()}
                    # check_result["analysis"]["虚函数注释扫描结果："].append(ano_dict)
                    virtual_result.append(ano_dict)
    except Exception as e:
        traceback.print_exc()
        logger.critical('scan virtual annotation exception ({e})'.format(e=e.message))
    pass

