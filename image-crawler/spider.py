import os
import requests
import time
import face_detect
import threading
import Queue
count = 0
imageHander = face_detect.ImageHander('E:\\face_detect\\haarcascade_frontalface_default.xml')
urlqueue = Queue.Queue()
def handle():
       global urlqueue
       with open('imgUrls.txt') as file:
              for imgUrl in file:
                     urlqueue.put(imgUrl)
                      
def getimg():
       global imageHander
       imageHander = face_detect.ImageHander('E:\\face_detect\\haarcascade_frontalface_default.xml')
       while not urlqueue.empty():
              imgUrl = urlqueue.get()
              print(urlqueue.qsize())
              imageHander.handerImage(imgUrl, 'wink', 'png')
       print('end')
handle()
thread = threading.Thread(target=getimg)
thread.start()
thread2 = threading.Thread(target=getimg)
thread2.start()
thread3 = threading.Thread(target=getimg)
thread3.start()
thread4 = threading.Thread(target=getimg)
thread4.start()
