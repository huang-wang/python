# --coding=utf-8 --
import Queue
import urllib
import time
import requests
import re
from multiprocessing.dummy import Pool
import os
import sys
import threading
import face_detect
import string

dirPath = ''
queue_lock = threading.Lock()
pend_queue = Queue.Queue()
history_queue = Queue.Queue()

class HistoryBaiduUrls(threading.Thread):
    def __init__(self, historyBaiduUrls):
        threading.Thread.__init__(self)
        self.alive = True
        self.history_url = historyBaiduUrls
        
    def run(self):
        while self.alive:
            time.sleep(120) #两分钟更新一次
            print('后台存储baidu url历史记录！')
            with open('historyUrls.txt', 'w') as file:
                while not self.history_url.empty():
                    file.write(self.history_url.get()+'\n')
        print('HistoryBaiduUrls Thread die')


class Image(object):
    """图片类，保存图片信息"""

    def __init__(self, url, imgtype):
        super(Image, self).__init__()
        self.url = url
        self.type = imgtype


class ImgThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.imageHander = face_detect.ImageHander('E:\\face_detect\\haarcascade_frontalface_default.xml')

    def run (self):
        global pend_queue, history_queue,dirPath
        print('thread to hander img' + str(pend_queue.qsize()))
        while  not pend_queue.empty():# pend_queue.get():
            imgs = pend_queue.get()
            for img in imgs:
                if img.url:
                    if img.url not in history_queue.queue:
                        history_queue.put(img.url)
                        self.imageHander.handerImage(img.url, dirPath, img.type)
            time.sleep(1)
            pend_queue.task_done()

class HistoryUrls(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.alive = True
        
    def run(self):
        global history_queue
        while self.alive:
            time.sleep(120)
            print('后台存储image url历史日志！')
            with open('historyImgUrls.txt', 'w') as file:
                while not history_queue.empty():
                    file.write(history_queue.get()+'\n')

        
class BaiduSpider(object):
   # 解码网址用的映射表
    str_table = {
        '_z2C$q': ':',
        '_z&e3B': '.',
        'AzdH3F': '/'
    }

    char_table = {
        'w': 'a',
        'k': 'b',
        'v': 'c',
        '1': 'd',
        'j': 'e',
        'u': 'f',
        '2': 'g',
        'i': 'h',
        't': 'i',
        '3': 'j',
        'h': 'k',
        's': 'l',
        '4': 'm',
        'g': 'n',
        '5': 'o',
        'r': 'p',
        'q': 'q',
        '6': 'r',
        'f': 's',
        'p': 't',
        '7': 'u',
        'e': 'v',
        'o': 'w',
        '8': '1',
        'd': '2',
        'n': '3',
        '9': '4',
        'c': '5',
        'm': '6',
        '0': '7',
        'b': '8',
        'l': '9',
        'a': '0'
    }
    history_url = Queue.Queue()
    session = requests.Session()
    re_objURL = re.compile(r'"objURL":"(.*?)".*?"type":"(.*?)"')

    def __init__(self, delay, word):
          print('init')
          self.delay = delay
          self.pool = Pool(4)
          self.word = word
          global history_queue
          if os.path.isfile('historyUrls.txt'):
              print('读取baidu url历史记录！')
              with open('historyUrls.txt', 'r') as file:
                  for url in file:
                      self.history_url.put(url)
          if os.path.isfile('historyImgUrls.txt'):
              print('读取imgUrl历史记录！')
              with open('historyImgUrls.txt', 'r') as file:
                  for url in file:
                      history_queue.put(url)

    def decode(self, url):
        for key, value in self.str_table.items():
             url = url.replace(key, value)
        trans = string.maketrans('wkvlju2it3hs4g5rq6fp7eo8dn9cm0bla'
,'abcdefghijklmnopqrstuvw1234567890')
        return str(url).translate(trans)
        

    def buildUrls(self):
          #if os.path.isfile('jsonUrls.txt'):
             # os.remove('jsonUrls.txt')
          if os.path.isfile('jsonUrls.txt'):
              print('jsonUrls.txt exits load data')
              urls = []
              with open('jsonUrls.txt', 'r') as file:
                      for line in file:
                          if 'str' in line:
                              break
                          urls.append(line)
              return urls 
          else:
              word = urllib.quote(self.word)
              url = r"https://image.baidu.com/search/acjson?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result&queryWord={word}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z=&ic=0&word={word}&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1&fr=&pn={pn}&rn=30&gsm=1e&1496752249673="
              time.sleep(self.delay)
              try:
                     html = self.session.get(url.format(word=word, pn=0), timeout = 15).content.decode('utf-8')
              except requests.exceptions.RequestException as e:
                     print("Exception in -> html = self.session.get(url.format(word=word, pn=0), timeout = 15).content.decode('utf-8')")
                     html = ''
              results = re.findall(r'"displayNum":(\d+),', html)
              maxNum = int(results[0]) if results else 0
              maxNum = 830
              urls = [url.format(word=word, pn=x)
                      for x in range(0, maxNum + 1, 30)]
              with open('jsonUrls.txt', 'w') as file:
                  for url in urls:
                      file.write(url + '\n')
              print('成功获取图片urls')
              return urls

    def getImgUrl(self, urls):
		  #time.sleep(self.delay)
		  global pend_queue
		  session = requests.Session()
		  while not urls.empty():
			  url = urls.get()
			  if url in (self.history_url.queue):
				  continue
			  else:
				  self.history_url.put(url)
				  try:
					  html = session.get(url, timeout = 20).content.decode('utf-8') 
				  except Exception as e :
					  print('error in getImgUrl %s' % url)
					  html = ''
				  datas = self.re_objURL.findall(html)
				  if len(datas) > 0:
					  imgs = [Image(self.decode(x[0]), x[1]) for x in datas]
					  pend_queue.put(imgs)
					  print pend_queue.qsize()
			  #time.sleep(self.delay)
		  print('getImgUrl thread done')

def main():
    args = {
    "眨一只眼睛 人脸":"wink"
}
    for searchWord in args.keys():
        sysdirPath = args[searchWord] 
        print('if you want to start for nothing clear all the txt file in this folder !')
        print('baiduSpider start!')
        #searchWord = input('enter search word in baidu.com:')
        #sysdirPath = input('enter save fileDir for face image:')
        if not os.path.exists(sysdirPath): #如果目录不存在就返回False
            os.mkdir(sysdirPath)
        global dirPath
        dirPath = sysdirPath
        print('search %s image in baidu.com save file to / %s' % (searchWord, dirPath))
        baiduSpider = BaiduSpider(2, args[searchWord]+" face")
        urls = baiduSpider.buildUrls()
        print('urls is ready')
        #处理百度网址
        baiduThreads = []
        baiduQueue = Queue.Queue()
        [baiduQueue.put(i) for i in urls]
        for i in range(10):
            baiduThread = threading.Thread(target=baiduSpider.getImgUrl, args = (baiduQueue,))
            baiduThread.start()
            baiduThreads.append(baiduThread)
        for baiduThread in baiduThreads:
            baiduThread.join()
        print('百度网址处理完成')

        #后台baidu url日志
        historyBaiduThread= HistoryBaiduUrls(baiduSpider.history_url)
        historyBaiduThread.daemon = True
        #historyBaiduThread.start()
        
        #后台image url历史日志
        historyImgThread = HistoryUrls()
        historyImgThread.daemon = True
        #historyImgThread.start()
        
        #获取图片后进行处理
        print('产生图片后进行处理线程')
        imgthreads = []
        for i in range(5) :
            thread = ImgThread()
            thread.start()
            imgthreads.append(thread)
            
        global pend_queue
        pend_queue.join()
        print('task down' + searchWord)
        historyImgThread.alive = False
        historyBaiduThread.alive = False
        
if __name__=='__main__':
    main()





    

#
##def on_click():
##    button['text'] = 'It is changed.'
##
##from tkinter import *
##root = Tk(className='aaa')
##button = Button(root)
##button['text'] = 'change it'
##button['command'] = on_click    #事件关联函数
##button.pack()
##root.mainloop()
##args = {
##	  "恐惧 人":"fraid",
##    "愤怒 人":"angry",
##    "惊讶 人":"shocked",
##    "厌恶 人":"disgusted",
##    "惊喜 人":"suprised",
##    "悲伤并恐惧 人":"SadnessAndfraid",
##    "悲愤 人":"SadnessAndAngry",
##    "悲伤并惊讶 人":"SadnessAndSurprise",
##    "悲伤并厌恶 人":"SadnessAndDisgusted",
##    "恐惧并愤怒 人":"FearAndAnger",
##    "恐惧并厌恶 人":"FearAndDisgusted",
##    "愤怒并惊讶 人":"AngerAndSurprise",
##    "愤怒并厌恶 人":"AngerAndDisgusted",
##    "厌恶并惊讶 人":"DisgustedAndSurprise",
##    "惊惧 人":"frightened",
##    "仇恨 人":"hatred",
##    "疑问 人":"doubt",
##    "崇敬 人":"respect",
##    "向往（渴望） 人":"yearn",
##    "嫉妒 人":"jealous",
##    "焦急 人":"anxiety",
##    "冷漠 人":"indifference",
##    "舒适（享受） 人":"comfort",
##    "热爱（热情） 人":"love",
##    "好奇 人":"curiousness",
##    "骄傲（自豪） 人":"pride",
##    "困窘（害羞） 人":"shy",
##    "轻蔑 人":"Scorn",
##    "疲劳 人":"tired"
##    "担忧":"worried"
##    "悲伤":"sad"
##    "愉快":"happy"}
