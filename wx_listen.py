from wxauto import *
import datetime
import time
import csv
import threading
import os
import re
from urllib.parse import urlparse, parse_qs
import requests
import asyncio
from answer import gpt_35_api_stream
import saveautio
# 获取当前微信客户端
wx = WeChat()
# 获取会话列表
wx.GetSessionList()

def savemsg(msg):
    #获取线程锁
    lock.acquire()
    try:
        filename = msg[0][:6]+ '.csv'
        with open(filename, 'a', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows([[datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg[1][0], msg[1][1]]])
    finally:
        #释放线程锁
        lock.release()

def answer(messages,qustion):
    #获取线程锁
    lock.acquire()
    try:
        messages.append({'role': 'user','content': qustion})
        if len(messages) > 3:
            del messages[:-3]
        wx.ChatWith(msg[1][0]) 
        wx.SendMsg('思考中') 
        if gpt_35_api_stream(messages)[0]:
            wx.ChatWith(msg[1][0]) 
            wx.SendMsg(messages[-1]['content']) 
        else:
            wx.ChatWith(msg[1][0]) 
            wx.SendMsg('error') 
    finally:
        #释放线程锁
        lock.release()
        
def downloadaudio(text):
    #获取线程锁
    lock.acquire()
    try:
        # 使用正则表达式匹配URL
        url_pattern = r'https?://\S+'
        urls = re.findall(url_pattern, text)
        
        # 打印提取到的URL
        for url in urls:
            res = requests.head(url)
            BVurl = res.headers.get('location')  
            #print(BVurl)
            parsed_url = urlparse(BVurl)
            bv = parsed_url.path.split('/')[-1]
            #print(bv)
        asyncio.get_event_loop().run_until_complete(saveautio.main(bv))
        wx.ChatWith(msg[1][0]) 
        wx.SendMsg('下载中') 
    finally:
        #释放线程锁
        lock.release()


# 全局线程锁
lock = threading.Lock()
messages = []
answermode = "download" #'download','answer',
answermodes = ['download','answer']
while True:
    try:
        msg = wx.listenmsg()
        if msg:
            thread = threading.Thread(target=savemsg(msg))
            thread.start()
            if '何乐不为' in msg[1][0]:
                if msg[1][1] in answermodes:
                    answermode = msg[1][1]
                    wx.ChatWith(msg[1][0]) 
                    wx.SendMsg('mode:'+answermode) 
                    continue                
                if answermode == 'answer':
                    print('question:',msg[1][1])
                    thread = threading.Thread(target=answer(messages,msg[1][1]))
                    thread.start()
                if answermode == 'download':
                    thread = threading.Thread(target=downloadaudio(msg[1][1]))
    except  Exception as e:
        print('Error:', str(e))
                