API = 'http://dev.qydailiip.com/api/?apikey=90c68bee2d04747b727310c1a810d9272a43cde8&num=30&type=text&line=win&proxy_type=putong&sort=rand&model=post&protocol=https&address=&kill_address=&port=&kill_port=80&today=false&abroad=1&isp=&anonymity=2'
import requests
import time

s = requests.Session()
proxies = []
start_time = time.time()
while True:
    time.sleep(1)
    s.get(API)
    content = s.get(API, timeout=5).content.decode('utf-8')
    proxies += content.split('\r\n')
    proxies = list(set(proxies))
    now = time.time()
    print('After %s second, len = %s'%(now-start_time, len(proxies)))