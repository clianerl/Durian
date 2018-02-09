cron配置定时任务：

    1、设置环境变量，cron确定使用那个编辑器来编辑crontab文件:
        在$HOME/.bash_profile添加：EDITOR=vi; export EDITOR

    2、创建cron任务：
        创建文件jiangcron添加一下内容:
            # jiang scan project report to mail
            # 每星期一9点扫描
            * 9 * * 1 /usr/bin/python  /home/jiangying/Durian/durian.py -t /opt/Sources/ -r cvi-100001

    3、提交任务：
            $ crontab jiangcron
         系统会在每个星期一早上九点扫描项目，将结果发到指定邮箱
         同时系统会自动在/var/spool/cron下会新建一个任务副本，文件名为用户名

    4、cron命令：
             -u <user>  define user
             -e         edit user's crontab
             -l         list user's crontab
             -r         delete user's crontab
             -i         prompt before deleting
             -n <host>  set host in cluster to run users' crontabs
             -c         get host in cluster to run users' crontabs
             -s         selinux context
             -x <mask>  enable debugging

    5、crontab文件格式：
        * 9 * * 1   /usr/bin/python  /home/jiangying/Durian/durian.py -t /opt/Sources/ -r cvi-100001
        * * * * *     command
        minute： 表示分钟，可以是从0到59之间的任何整数。
        hour：表示小时，可以是从0到23之间的任何整数。
        day：表示日期，可以是从1到31之间的任何整数。
        month：表示月份，可以是从1到12之间的任何整数。
        week：表示星期几，可以是从0到7之间的任何整数，这里的0或7代表星期日。
        command：要执行的命令，可以是系统命令，也可以是自己编写的脚本文件。

        在以上各个字段中，还可以使用以下特殊字符：
        星号（*）：代表所有可能的值，例如month字段如果是星号，则表示在满足其它字段的制约条件后每月都执行该命令操作。
        逗号（,）：可以用逗号隔开的值指定一个列表范围，例如，“1,2,5,7,8,9”
        中杠（-）：可以用整数之间的中杠表示一个整数范围，例如“2-6”表示“2,3,4,5,6”
        正斜线（/）：可以用正斜线指定时间的间隔频率，例如“0-23/2”表示每两小时执行一次。同时正斜线可以和星号一起使用，例如*/10，如果用在minute字段，表示每十分钟执行一次。


    6、crontab备份：
         1)、将cron任务备份到文件mycron:
                crontab -l > mycron
         2)、当文件被删除时，可以在/var/spool/cron下查看，文件名为用户名