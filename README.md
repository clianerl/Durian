# Durian
![durian](https://github.com/DurianCoder/Durian/blob/master/docs/cmd.png "durian文档")
## Introduction（介绍）
  `Durian`工具是一个基于`libclang`的个性化代码检测工具。
> 1）、忘记日志打印等较为较为明显的问题，可以通过正则表达式直接匹配出。可以通过xml文件添加匹配规则，对于不同类型的问题，进行不同的逻辑处理，如是否打印了日志，虚函数是否写了文档注释等问题。</br>
> 2）、基于libclang，利用clang对C family 语言进行词法分析和语法分析。将源码生成对应的AST,通过遍历AST来分析函数内可能存在的变量重复赋值问题。

## Features（特点）

#### Multi-language Supported（支持多种开发语言）
> 支持C系列(基于libclang)、JAVA、PHP、等开发语言以及伪代码检测，并支持数十种类型文件。

#### Multi-Vulnerabilities Supported（支持多种漏洞类型）
> 暂时开放几条漏洞规则匹配，用户可以自定义，后续将继续更新。

#### CLI/API Mode（命令行模式和API模式）
> 暂时提供CLI模式，用户可以自己添加API、WEB扩展。

## 什么是”源代码安全审计（白盒扫描）”？
>  由于开发人员的技术水平和安全意识各不相同，导致可能开发出一些存在安全漏洞的代码。 攻击者可以通过渗透测试来找到这些漏洞，从而导致应用被攻击、服务器被入侵、数据被下载、业务受到影响等等问题。 “源代码安全审计”是指通过审计发现源代码中的安全隐患和漏洞，而Cobra可将这个流程自动化。

## Durian为什么能从源代码中扫描到漏洞？
> 对于一些特征较为明显的可以使用正则规则来直接进行匹配出，比如硬编码密码、错误的配置等。 对于OWASP Top 10的漏洞，Durian通过预先梳理能造成危害的函数，并定位代码中所有出现该危害函数的地方，继而基于Lex(Lexical Analyzer Generator, 词法分析生成器)和Yacc(Yet Another Compiler-Compiler, 编译器代码生成器)将对应源代码解析为AST(Abstract Syntax Tree, 抽象语法树)，MyCobra添加了libclang，可以支持对C系列的语言进行AST分析。

## 安装：
#### 1、安装pip
> 检查linux是否有安装python-pip包：   `yum install python-pip` </br>
> 没有python-pip包就执行命令：     `yum -y install epel-release` </br>
> 执行成功之后，再次执行：     `yum install python-pip` </br>
> 对安装好的pip进行升级：     `pip install --upgrade pip`

#### 2、安装clang编辑器
> yum安装 :    `yum install clang`  </br>
> apt安装 :      `sudo apt-get install clang`

#### 3、配置python bindings:
> 使用pip安装：`sudo pip install clang==版本号(如:3.4)`
##### 注意：clang的版本号和libclang的版本号必须一致。

#### 4、安装Durian依赖：
> `pip install -r requirement.txt`

#### 5、安装Durian：
> `git clone https://github.com/DurianCoder/Durian.git`

#### 6、测试
> cli输出到邮箱:</br>
    `python durian.py -t target_file  -o your_email -r cvi-100001,cvi-100002`      
