import requests

API = 'http://dev.qydailiip.com/api/?apikey=90c68bee2d04747b727310c1a810d9272a43cde8&num=30&type=text&line=win&proxy_type=putong&sort=1&model=all&protocol=https&address=&kill_address=&port=&kill_port=80&today=false&abroad=1&isp=&anonymity=2'

def getProxy(s=None) -> list:
    Headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'}
    if not s:
        s = requests.Session()
    while True:
        try:
            content = s.get(API,headers=Headers, timeout=5).content.decode('utf-8')
            proxies = content.split('\r\n')
            if proxies:
                break
        except:
            print('getProxy Failed')
            return getProxy(s)
            pass
    return proxies

def get_page(url,proxylist=None,s=None,headers=None,):
    Headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15'}
    if not s:
        s = requests.Session()
    if not headers:
        headers = Headers
    if not proxylist:
        proxylist = getProxy(s)
    proxycount = 0
    while True :
        try:
            if proxycount >= len(proxylist)-1:
                proxylist = getProxy(s)
                proxycount =0
            resp = s.get(url,proxies = {'http':proxylist[proxycount],'https':proxylist[proxycount]},headers=headers,timeout=4)
            break
        # except requests.exceptions.ConnectTimeout:
        #     proxycount += 1
        except:
            proxycount += 1
    return resp

