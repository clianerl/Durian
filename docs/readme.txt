使用指南：
    1、linux编码格式为：UTF-8
        配置.bash_profile：
            # language
            export LC_ALL="zh_CN.UTF-8"
            export LANG="zh_CN.UTF-8"

    2、系统的vimrc编码不需要更改

    3、源码编码格式为：UTF-8
        文件头指定：# -*- coding:UTF-8 -*-

    4、检查工具依赖clang和clang的python bindings，且二者版本必须一致
        安装步骤：
            1)、clang安装：yum install clang
                 查看clang版本: clang -v
            2)、clang的python bindings安装：
                 pip install clang==clang版本号，如（pip install clang==3.4）
                Tips:
                    如果3.4安装失败，可以将下面链接里的clang、clang-3.4-py2.7.egg-info移到python的site-packages路径下
                    clang3.4的python bindings链接https://pan.baidu.com/s/1dw3auq
            3)、源码下载：
                    Github：https://github.com/DurianCoder/Durian

    5、在配置文件config中配置邮箱等信息

    6、cli运行：
            python durian.py -t "target file path" -o "recviver email" -r "rules"
                 如：python durian.py -t /opt/Source -o a@qq.com,b@hundsun.com -r cvi-100001,cvi-100002

            1)、-t 后面的参数是扫描路径
                    虚函数和变量重复赋值，只扫描-t路径下的直接子目录src

            2)、可以在参数-o 后输入收件人邮箱，也可以在config配置文件中配置
                    格式为：aaa@bbb.com,bbb@bbb.com

            3)、参数-r 后面添加扫描规则，如：-r cvi-100001,cvi-110001
                    如过没有添加-r,默认扫描所有规则，
                        如：python durian.py -t /opt/Source -o a@qq.com,b@hundsun.com

