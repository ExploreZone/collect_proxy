# coding:utf-8

import requests
from bs4 import BeautifulSoup as bs
import Queue
import time
import threading
import sys

num = 0
proxy_ip = []
# import os
proxy_file = open("proxy.txt","a+")
# proxy_dict = {}
# 创建threading类
class test_proxy(threading.Thread):
    def __init__(self,queue,name):
        threading.Thread.__init__(self)
        self.urls = queue
        self.name =name
    def run(self):
        print "[ * ]"+self.name+"start work:"

        header = {'Accept-Encoding': 'gzip, deflate, br',
                'Cookie': 'bid=LrQN31nGWQQ; ll="118099"; __utmc=30149280; __utmz=30149280.1516180100.4.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _vwo_uuid_v2=87044A8644A6B35F343DEF23592CF1D2|a45ff09f0866b72a0db3c7e82de8d829; ap=1; ct=y; __utma=30149280.1648116166.1513566116.1516180100.1516194462.5; ps=y; __utmb=30149280.3.10.1516194462; dbcl2="154698815:25XxaBZL8xU"; ck=DM63; push_noty_num=0; push_doumail_num=0',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36}'}
        # 不断去从代理队列中去取代理，进行测试---->调用check_prox函数
        while True:
            global queueLock
            queueLock.acquire()
            if not self.urls.empty():
                test_proxy= self.urls.get()
                # print "see:",test_proxy
                queueLock.release()
            else:
                queueLock.release()
                exit(0)
            time.sleep(0.05)
            try:
                check_proxy(test_proxy)
            except Exception as e:
                # print e
                print "%s find bug"%test_proxy
                # print e
# 将代理网站页面队列放在函数中，进行爬虫爬到代理信息存放在数组中
def spider(queue):
    headers = {'Accept-Encoding': 'gzip, deflate, br',
               'Cookie': 'bid=LrQN31nGWQQ; ll="118099"; __utmc=30149280; __utmz=30149280.1516180100.4.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _vwo_uuid_v2=87044A8644A6B35F343DEF23592CF1D2|a45ff09f0866b72a0db3c7e82de8d829; ap=1; ct=y; __utma=30149280.1648116166.1513566116.1516180100.1516194462.5; ps=y; __utmb=30149280.3.10.1516194462; dbcl2="154698815:25XxaBZL8xU"; ck=DM63; push_noty_num=0; push_doumail_num=0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36}'}
    #
    while True:
        if not queue.empty():
            url = queue.get()
        else:
            print "tesk is ok"
            break
        req = requests.get(url=url,headers=headers,timeout =2)
        req_content = req.content
        soup = bs(req_content, "lxml")
        para = soup.find_all("tr")[1:]
        global num
        for i in para:
            ip = i.find_all("td")[1].string
            port = i.find_all("td")[2].string
            protocal = i.find_all("td")[5].string
            protocal = protocal.lower()
            # 格式：协议：IP：port
            domain = protocal+"://"+ip+":"+port
            proxy_ip.append(domain)
# 设置代理检查函数，不论协议全部改为http协议，使用代理在2s内访问成功就判定为正常的代理
def check_proxy(proxy_test):
    global num
    url= "https://www.baidu.com"
    headers = {'Accept-Encoding': 'gzip, deflate, br',
               'Cookie': 'bid=LrQN31nGWQQ; ll="118099"; __utmc=30149280; __utmz=30149280.1516180100.4.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; _vwo_uuid_v2=87044A8644A6B35F343DEF23592CF1D2|a45ff09f0866b72a0db3c7e82de8d829; ap=1; ct=y; __utma=30149280.1648116166.1513566116.1516180100.1516194462.5; ps=y; __utmb=30149280.3.10.1516194462; dbcl2="154698815:25XxaBZL8xU"; ck=DM63; push_noty_num=0; push_doumail_num=0',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36}'}
    dict_test = proxy_test.split(":")
    # 全部使用http协议，即使是https协议也不例外
    # proxy_dict = {dict_test[0]:dict_test[1]}
    proxy_dict = {"http":dict_test[1]}
    req_ok = requests.get(url=url,headers = headers,proxies=proxy_dict,timeout =2)
    if req_ok.status_code==200:
        proxy_file.write(proxy_test+"\n")
        # print proxy_test
        # print "ok"
        num += 1

def main():
    print "Welcome to my proxy tools！This tool Only applies to this site:http://www.xicidaili.com/nn"
    if len(sys.argv)<3:
        print "[ * ] usage: python check_proxy.py pages threads"
    thread_num =int(sys.argv[2])
    pages_num = int(sys.argv[1])
    queue_proxy = Queue.Queue()
    # 设置队列锁，一个线程对队列操作，其他线程等待
    global queueLock
    queueLock = threading.Lock()
    time_start = time.time()
    print time_start
    global num
    threads =[]
    queue = Queue.Queue()
    for i in range(pages_num+1):
        url = "http://www.xicidaili.com/nn/%d"%i
        if not queue.full():
            queue.put(url)
            time.sleep(0.05)
    print queue.qsize()
    spider(queue)
    for i in proxy_ip:
        queue_proxy.put(i)
    for i in range(thread_num):
        thread = test_proxy(queue_proxy,i)
        threads.append(thread)
    print "nums: %d"%queue_proxy.qsize()
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    time_end = time.time()
    time_using = time_end- time_start
    proxy_file.write("We all collect proxy %s"%num)
    print num
    print "using time :%s"%time_using
if __name__ == '__main__':
    main()

