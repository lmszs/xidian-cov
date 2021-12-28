#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import json
import requests
import os
import smtplib
from email.mime.text import MIMEText
import time
import sys

default_mail_host = 'smtp.163.com'  # SMTP服务器
default_mail_user = 'englishlimaosong@163.com'  # 用户名
default_mail_pass = 'UJGHFPCSQEWBVZRR'  # 授权密码，非登录密码
send_hour = [10, 14, 19]  # 填报时间


def sendEmail(content, title, receivers, mail_user='', mail_pass='', mail_host=''):
    if mail_user == '':
        mail_user = default_mail_user
    if mail_pass == '':
        mail_pass = default_mail_pass
    if mail_host == '':
        mail_host = default_mail_host
    sender = mail_user
    receivers = [receivers]
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = '{}'.format(sender)
    message['To'] = ','.join(receivers)
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(mail_user, mail_pass)  # 登录验证
        smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
        print('mail has been send successfully.')
    except smtplib.SMTPException as e:
        print(e)


def submitYiqingtong(name):
    print(time.asctime(time.localtime()), end='\t')
    data = {}
    with open(name, 'r') as fd:
        data = json.load(fd)

    conn = requests.Session()

    # Login
    result = conn.post('https://xxcapp.xidian.edu.cn/uc/wap/login/check',
                       data={'username': data['_u'], 'password': data['_p']})
    if result.status_code != 200:
        print('认证大失败')
        sendEmail(title='疫情通失败', content='认证失败', receivers=data['receive_email'], mail_user=data['sent_email'],
                  mail_pass=data['sent_email_code'])
        return
        # exit()

    # Submit
    data_copy = data.copy()  #
    del data_copy['_u']
    del data_copy['_p']
    del data_copy['receive_email']
    del data_copy['sent_email']
    del data_copy['sent_email_code']

    result = conn.post('https://xxcapp.xidian.edu.cn/xisuncov/wap/open-report/save', data=data_copy)
    print(name + '  ' + result.text)
    if eval(result.text)['m'] != '您已上报过' and eval(result.text)['m'] != '填报成功':
        sendEmail(title='疫情通失败', content=eval(result.text)['m'], receivers=data['receive_email'],
                  mail_user=data['sent_email'],
                  mail_pass=data['sent_email_code'])


# while 1:
#     tim = time.localtime()
#     if tim.tm_hour in send_hour and tim.tm_mon == 0 and tim.tm_sec < 5:
#         for file in os.listdir('./json'):
#             submitYiqingtong(name=os.path.join('./json', file))
with open('log.txt', 'a') as f:
    sys.stdout = f
    for file in os.listdir('./json'):
        submitYiqingtong(name=os.path.join('./json', file))
    f.close()
