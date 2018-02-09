#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import subprocess
import multiprocessing
import json
import os
import logging
# 导入clang 的 lib bindings 模块
from clang.cindex import CursorKind
import clang

from .log import logger
from .rule import Rule

"""
clang python bindings
解析c系类文件成AST
获取文件中函数、变量等信息
检查单个文件是否存在变量重复赋值
"""


def clang_detect_file(f, vulnerability):
    """
    clang 检测当个c系列文件
    :param f:文件的绝对路径
    :param vulnerability:
    :return:
    """
    # logger.info("进入到clang_detect_file！")
    var_reevaluate_list = []
    filename = os.path.split(f)[1]
    # todo 将改方法抽象到工具类
    language = Rule().languages[vulnerability["language"]]
    lang_extensions = language["extensions"]
    # todo 封装，获取文件的后缀
    idx = filename.find(".")

    if idx != -1 and filename[idx:] in lang_extensions:
        # if f.lower()[-4:] == ".cpp" or f.lower()[-2:] == ".h":
        # 获取clang接口
        index = clang.cindex.Index.create()
        # 解析文件，获取语法树对象
        tu = index.parse(f)
        # 获取函数列表
        var_reevaluate_list = get_funs_info(tu.cursor, f, [])
        # 获取cpp文件中的变量
        vars_list = get_vars(tu.cursor)
        # 遍历每个变量，grep查询
        for var in vars_list:
            # todo 将grep执行命令抽象处理，判断不同系统
            # grep命令判断变量后的赋值语句是否包含特定字符串
            # -s Suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            # grep -P -n "durian\s?=\s?.*ResultSet*" person.cpp
            param = ["/bin/grep", "-s", "-n", "-r"] + [var + vulnerability["match"], f]
            try:
                p = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                result, error = p.communicate()  # communicate(stdin、timeout) return stdout and std err
            except Exception as e:
                traceback.print_exc()
                logger.critical('match exception ({e})'.format(e=e.message))
                continue
            try:
                # todo 可能存在编码转换
                var_line_result = result
                error = error
                # exists result
                if var_line_result == '' or var_line_result is None:
                    logger.debug("没匹配到变量重复赋值！")
                    continue
                var_line_results = var_line_result.strip().split("\n")
                if len(var_line_results) > 1:
                    var_reevaluate_list = get_function_list_by_line_num(var, var_line_results, var_reevaluate_list)
            except AttributeError as e:
                pass
            if len(error) is not 0:
                logger.critical("grep查询变量有误！")
    # 将函数列表中的vul中的变量赋值语句进行判断，是否存在重复赋值，没有则删除
    var_reevaluate_list = evaluate_funs_list(var_reevaluate_list)
    if len(var_reevaluate_list) > 0:
        logger.info("文件{fe}存在变量重复赋值！".format(fe=f))
        logger.info(json.dumps(var_reevaluate_list, indent=4))
        return var_reevaluate_list
    else:
        return []


def evaluate_funs_list(funs_list):
    """evaluate funs_list, if vul_num < 2, del"""

    lens = len(funs_list)
    while lens > 0:
        for fun_name, fun_detail in funs_list[lens-1].items():
            for var, var_detail in fun_detail["vul"].items():
                if len(var_detail) < 2:
                    fun_detail["vul"].pop(var)
            if len(fun_detail["vul"]) == 0:
                funs_list.pop(lens-1)
            lens -= 1
    return funs_list


def get_function_list_by_line_num(var, var_line_results, funs_list):
    """将grep到的变量赋值语句添加到funs_list的vul对应函数属性中"""

    # 当匹配到的行数大于1，则可能存在变量重复赋值
    if len(var_line_results) > 1:
        # 38:  durian = aResultSet->add_int(1);
        # 根据：截取 var_line_results
        vul_list = {}
        for var_reevaluate_line in var_line_results:
            # grep扫描单个文件的结果格式为：linenum：content
            line_num = var_reevaluate_line.split(":")[0]
            code_content = var_reevaluate_line.split(":")[1]
            # 判断语句在哪个函数
            for fun in funs_list:
                for fun_name, fun_detail in fun.items():
                    if fun_detail["start_line"] <= int(line_num) <= fun_detail["end_line"]:
                        var_detail = fun_detail["vul"][var] = fun_detail["vul"].get(var, {})
                        var_detail["line:" + line_num] = code_content
                    continue
    return funs_list


def get_vars(cur):
    """
    获取单个c系列文件中的变量去重列表
    获取cur对应AST中的变量（即cur.kind为Cursorkind.VAR_DECL的var）
    return: vars的一个去重的list集合
    """

    # 这里展示的是一个提取每个分词的方法。
    var_list = []
    for token in cur.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        cur = token.cursor
        if cur.kind == CursorKind.VAR_DECL and cur.spelling != "":
            var_list.append(cur.spelling)
    # 去重，list和set互相转化
    return list(set(var_list))


def get_funs_info(node, f, funs_list):
    """
    brief : 返回文件中函数信息
    node : cur节点
    f : 要检查的文件
    funs_list : 结果列表
    return ： f 文件包含的函数信息（所在的文件，起始和结束的行号，以及函数类型）
            {
                fun1:{
                    start_line:12
                    end_line:23
                    kind:CursorKind.FUNCTION_DECL
                    file:../bin/..
                    vul:{
                        var:{
                            a = xxx->sxxxx()
                            b = xxx->sxxxx()
                        }
                    }
                }

                ...
            }
    """
    for c in node.get_children():
        children = get_funs_info(c, f, funs_list)
    if node.is_definition() and not node.spelling == "" and str(node.location.file) == f:
        if node.kind == CursorKind.FUNCTION_DECL or node.kind == CursorKind.CXX_METHOD:
            fun = {}
            fun_detail = fun[node.spelling or node.displayname] = {}
            fun_detail["start_line"] = node.extent.start.line
            fun_detail["end_line"] = node.extent.end.line
            fun_detail["kind"] = str(node.kind)
            fun_detail["file"] = str(node.location.file)
            fun_detail["vul"] = {}
            funs_list.append(fun)
    return funs_list
