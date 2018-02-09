# -*- coding:utf-8 -*-
import sys
from pprint import pprint
from clang.cindex import Config
from clang.cindex import TypeKind
from clang.cindex import CursorKind
from clang.cindex import Config
import clang


def yacc_ast(cursor):
    """
    在遍历过程中，遇到了一个节点就进行检查。
    CursorKind指的是这个节点在AST中的位置例如（函数，类，参数定义等）
    TypeKind指的是这个节点的语义类别，例如这个参数的类别是const char，int等类别。
    :param cursor:
    :return:
    """
    file_dict = {}
    file_dict["global_var"] = []
    for cur in cursor.get_children():
        if hasattr(cur, "CursorKind") and cur.CursorKind == CursorKind.FUNCTION_DECL:
            # do something
            file_dict[cur.spelling] = []
            for cur_sub in cur.get_children():
                if cur_sub .kind == CursorKind.CALL_EXPR:
                    pass
                    # do something
                    # 这一段代码分析的是函数定义调用的其他函数。
                elif cur.kind == CursorKind.VAR_DECL and cur.spelling != "":
                    file_dict[cur.spelling].append(cur.spelling)
        elif cur.kind == CursorKind.FIELD_DECL:
            pass
            # do something
        elif cur.type.kind == TypeKind.UCHAR:
            pass
            # do something
        elif cur.kind == CursorKind.VAR_DECL and cur.spelling != "":
            file_dict["global_var"].append(cur.spelling)
        yacc_ast(cur)
    return file_dict


def get_functions(cur):
    """
    获取语法树上的函数
    :param cur:
    :return:
    """
    # 这里展示的是一个提取每个分词的方法。
    var_list = []
    for token in cur.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        cur = token.cursor
        if cur.kind == CursorKind.FUNCTION_DECL and cur.spelling != "":
            var_list.append(cur.spelling or cur.displayname)
    return list(set(var_list))


def get_vars(cur):
    """
    获取语法树上的变量
    :param cur:
    :return:
    """
    # 这里展示的是一个提取每个分词的方法。
    var_list = []
    for token in cur.get_tokens():
        # 针对一个节点，调用get_tokens的方法。
        cur = token.cursor
        if cur.kind == CursorKind.VAR_DECL and cur.spelling != "":
            var_list.append(cur.spelling)
    return list(set(var_list))


index = clang.cindex.Index.create()
tu = index.parse("person.cpp")
file_content = yacc_ast(tu.cursor)
print(get_functions(tu.cursor))
pprint(file_content)
