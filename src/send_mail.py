#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import json
import smtplib
from .config import Config
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .log import logger
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

project_path = os.path.join(os.getcwd())
config_path = os.path.join(project_path, "config")


def send_mail(target, filename, output, scan_result_list):
    # logger.info("config path == " + config_path + ",project path == " + project_path)
    host = Config("email", "host").value
    port = Config("email", "port").value
    username = Config("email", "username").value
    password = Config("email", "password").value
    sender = Config("email", "sender").value   # 如果是公司邮箱，查看发送邮件的From格式

    # 将-o输入的邮箱添加到receiver
    receiver_list = Config("email", "receiver").value.split(",")
    output = output.strip().split(",")
    for receiver in output:
        if re.match(r'^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', receiver):
            receiver_list.append(receiver)
        else:
            continue

    # 邮箱去重
    receiver_list = list(set(receiver_list))
    logger.info("receiver == " + str(receiver_list))

    logger.info("host=" + host + ",port=" + port)
    # server = smtplib.SMTP_SSL(host=host, port=port)
    server = smtplib.SMTP(host=host, port=port)
    msg = MIMEMultipart()
    msg['From'] = sender + "CodeCheckingTool"
    # 收件人必须是一个字符串
    msg['To'] = ",".join(receiver_list)
    msg['Subject'] = "Code scan report"

    msg.attach(MIMEText("扫描的项目路径：{t}\n报告见附件。\n扫描结果：{result_content}\nJSON在线转化: https://www.bejson.com/"
                        .format(t=target, result_content=json.dumps(scan_result_list, ensure_ascii=False, indent=4)),
                        'plain', 'utf-8'))

    with open(filename, 'rb') as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.split(filename)[1])
        msg.attach(attachment)
        logger.info("add attach file success!")
    try:
        logger.info("start login")
        server.login(user=username, password=password)
        # to_address 是一个list或者字符串
        server.sendmail(from_addr=sender, to_addrs=receiver_list, msg=msg.as_string())
        server.quit()
        logger.info('[EMAIL] Email delivered successfully.')
        return True
    except smtplib.SMTPRecipientsRefused:
        logger.critical('[EMAIL] Email delivery rejected.')
        return False
    except smtplib.SMTPAuthenticationError:
        logger.critical('[EMAIL] SMTP authentication error.')
        return False
    except smtplib.SMTPSenderRefused:
        logger.critical('[EMAIL] SMTP sender refused.')
        return False
    except smtplib.SMTPException as error:
        logger.critical(error)
        return False
