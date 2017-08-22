# --coding=utf-8 --
from bs4 import BeautifulSoup
import Queue
import requests
import sys
import os
import threading
import gzip
import time

sys.path.append('../')
import face_detect


pend_queue = Queue.Queue()
imageHander = face_detect.ImageHander('E:\\face_detect\\haarcascade_frontalface_default.xml')


def getImgUrl(urls):
	#time.sleep(self.delay)
	global pend_queue
	session = requests.Session()
	header = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
	'Cache-Control':'no-cache',
	'Connection':'keep-alive',
	'Cookie':'CGISource=hk%2Esearch%2Eyahoo%2Ecom%2F; CGIVid=20170413072958405196W5; _ga=GA1.2.2114753234.1492093831; _gat=1',
	'Host':'www.crystalgraphics.com',
	'Pragma':'no-cache',
	'Referer':'http://www.crystalgraphics.com/powerpictures/images.photos.asp?ss=girls+tongue+out&page=3',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}
	while not urls.empty():
		url = urls.get()
		print url
		requests.packages.urllib3.disable_warnings()
		try:
			resp = session.get(url,headers =header,  timeout = 20, verify=False)
			html = resp.content
		except Exception as e :
		    print(e)
		    print('error in getImgUrl %s' % url)
		    html = ''
		soup = BeautifulSoup(html, "lxml")
		imgtags = soup.find_all('img', class_="image_with_shadow")
		if len(imgtags) > 0:
		    [pend_queue.put(imgtag['src']) for imgtag in imgtags]
	print pend_queue.qsize()
	return pend_queue
	#time.sleep(self.delay)
	print'getImgUrl thread done'


def handleImg(pend_queue, imageHander, destPath='temp'):  
	print('thread to hander img' + str(pend_queue.qsize()))
	while not pend_queue.empty():# pend_queue.get():
		img = pend_queue.get()
		if img:
			imageHander.handerImage(img, '../' + destPath, '.png')
	time.sleep(1)

		
def buildUrls(page_size = 1, keyword = 'keyword'):
	urls = []
	if os.path.isfile('../jsonUrls.txt'):
		print('jsonUrls.txt exits load data')
		with open('../jsonUrls.txt', 'r') as file:
			for line in file:
				if 'str' in line:
					break
				urls.append(line)
	else:
		for i in range(page_size):
			urls.append('http://www.crystalgraphics.com/powerpictures/images.photos.asp?ss='+ keyword +'&page=' + str(i))	
	return urls
				
keyword = 'wink human face'	
urls = buildUrls(4000, keyword)
print('urls is ready')

#处理百度网址
baiduThreads = []
baiduQueue = Queue.Queue()
[baiduQueue.put(i) for i in urls]
for i in range(10):
	baiduThread = threading.Thread(target=getImgUrl, args = (baiduQueue,))
	baiduThread.start()
	baiduThreads.append(baiduThread)
for baiduThread in baiduThreads:
	baiduThread.join()
print('百度网址处理完成')
		
dirpath = 'shocked' #dirpath
if not os.path.exists('../' + dirpath):
	print('create folder ', dirpath)
	os.makedirs('../' + dirpath)
handleImg(pend_queue, imageHander, dirpath)	  
