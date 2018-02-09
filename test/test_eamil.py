#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src import send_mail
# project_path = os.path.join(os.getcwd(), os.pardir)
# config_path = os.path.join(os.getcwd(), "config")


if __name__ == "__main__":
    # config = ConfigParser()
    # config.read(config_path)
    # print(config_path)
    # #in_log = config.get("log_rule","没有打印进入日志")
    # in_log = config.get("email", "port")
    # print(in_log)

    project_path = os.path.join(os.getcwd())
    result_path = os.path.join(project_path, "result/result.json")
    # print(result_path)

    host = "smtp.qq.com"
    # SMTP Port
    port = 465
    username = "2435978786@qq.com"
    password = "qytvlftavvfjdjge"
    sender = "2435978786@qq.com"
    receiver = "jiangying1110@outlook.com"
    print("1")
    server = smtplib.SMTP_SSL(host=host, port=port)
    print("2")
    msg = MIMEMultipart()
    msg['From'] = sender + "代码检测工具"
    msg['To'] = receiver
    msg['Subject'] = '代码扫描报告'

    msg.attach(MIMEText("扫描项目：{t}\n报告见附件\nJSON在线转化: https://www.bejson.com/".format(t="target"), 'plain', 'gbk'))
    print("3")
    with open(result_path, 'rb') as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=os.path.split(result_path)[1])
        msg.attach(attachment)
    try:
        server.login(user=username, password=password)
        server.sendmail(from_addr=sender, to_addrs=receiver, msg=msg.as_string())
        server.quit()
        print("successful!")
    except smtplib.SMTPRecipientsRefused:
        print("exception!")
        pass