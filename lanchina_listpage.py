# encoding=gb2312
import requests
from bs4 import BeautifulSoup as bs
import csv
import time
import os
from queue import Queue
import gc
from proxy_module import getProxy
from threading import Thread
import random
import uuid
import base64
import re
from utilsDIR.get_resp import my_post


# titles = ['index','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','约定开工日期','约定竣工时间','实际开工时间','实际竣工','批准单位','合同签订日期'


GLOBAL_TIMEOUT_INDEX = 10

class LandCrawler(Thread):
    def __init__(self, queue, thread_name, tabid=0, year=0):
        # init procedures
        Thread.__init__(self, name=thread_name)
        self.queue = queue
        self.s = requests.Session()
        self.s.keep_alive = False
        self.cookies = ''
        self.proxy = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        }
        self.tabid = tabid
        self.year = year

        print('init done', thread_name)

    def decode_image(self, src):
        """
        解码图片
        :param src: 图片编码
            eg:
                src="data:image/gif;base64,R0lGODlhMwAxAIAAAAAAAP///
                    yH5BAAAAAAALAAAAAAzADEAAAK8jI+pBr0PowytzotTtbm/DTqQ6C3hGX
                    ElcraA9jIr66ozVpM3nseUvYP1UEHF0FUUHkNJxhLZfEJNvol06tzwrgd
                    LbXsFZYmSMPnHLB+zNJFbq15+SOf50+6rG7lKOjwV1ibGdhHYRVYVJ9Wn
                    k2HWtLdIWMSH9lfyODZoZTb4xdnpxQSEF9oyOWIqp6gaI9pI1Qo7BijbF
                    ZkoaAtEeiiLeKn72xM7vMZofJy8zJys2UxsCT3kO229LH1tXAAAOw=="

        :return: str 保存到本地的文件名
        """
        # 1、信息提取
        result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
        if result:
            ext = result.groupdict().get("ext")
            data = result.groupdict().get("data")

        else:
            raise Exception("Do not parse!")

        # 2、base64解码
        img = base64.urlsafe_b64decode(data)

        # 3、二进制文件保存
        filename = "./captchas/{}.{}".format(uuid.uuid4(), ext)
        with open(filename, "wb") as f:
            f.write(img)
        return filename

    def recog(self, catpchapath) ->str:
        try:
            request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
            # 二进制方式打开图片文件
            access_token = '24.2acf612791d4ec6bb8a903e35cb8e698.2592000.1587016456.282335-11809953'
            f = open('{}'.format(catpchapath), 'rb')
            img = base64.b64encode(f.read())
            params = {"image": img}
            request_url = request_url + "?access_token=" + access_token
            headers = {'content-type': 'application/x-www-form-urlencoded'}
            response = requests.post(request_url, data=params, headers=headers, timeout=GLOBAL_TIMEOUT_INDEX)
            if response:
                text = response.json()['words_result'][0]['words']
                print(text)
                return text
            else:
                return ''
        except Exception as e:
            self.save_exception(e)
            self.save_log_string('exception in recog func')
            return ''

    def stringToHex(self, string):
        '''
        # function
        # stringToHex(str)
        # {
        #     var
        # val = "";
        # for (var i = 0; i < str.length; i++) {
        # if (val == "")
        # val = str.charCodeAt(i).toString(16);
        # else
        # val += str.charCodeAt(i).toString(16);
        # }
        # return val;
        # }
        '''
        # val = ''
        # for i in string:
        #     if val == '':
        #         val = '3' + i
        #     else:
        #         val += '3' + i
        val = ''
        for i in string:
            val += hex(ord(i))[2:]
        return val

    def get_cookies(self, url):
        try:
            yunsuo_s = self.s.get(url, timeout=GLOBAL_TIMEOUT_INDEX, headers=self.headers).cookies.get('security_session_verify')
            mid_resp = self.s.get('{}{}'.format(url, '&security_verify_data=313932302c31303830'),
                                                      headers=self.headers, timeout=GLOBAL_TIMEOUT_INDEX)
            mid = mid_resp.cookies.get('security_session_mid_verify')
            # check for captcha. ----------------->
            try:
                content = mid_resp.content.decode('utf-8','ignore')
                if '验证码不能为空' in content:
                    print('验证码')
                    soup = bs(content, 'lxml')
                    imgTag = soup.find('img', attrs={'alt': 'verify_img'})
                    imgdata = imgTag['src']
                    filename = self.decode_image(imgdata)
                    print(filename)
                    word = self.recog(filename)
                    if word == '':
                        return False
                    os.rename(filename, './captchas/'+word+'_{}.bmp'.format(uuid.uuid4()))
                    text = self.stringToHex(word)
                    high = self.s.get('{}&security_verify_img={}{}'.format(url, text,'&security_verify_data=313932302c31303830'),
                                headers=self.headers, timeout=GLOBAL_TIMEOUT_INDEX).cookies.get('security_session_high_verify')
                    return {
                        'security_session_verify': yunsuo_s,
                        'security_session_high_verify': high,
                        'security_session_mid_verify':mid
                    }
                else:
                    pass
            except Exception as e:
                self.save_exception(e)
                self.save_log_string('Exception in 验证码 logic')
                print('error in 验证码 logic')
                return False
            # captcha logic end here ---------------->

            # if captcha not showing up then just go through the normal process
            print(yunsuo_s, mid)
            if yunsuo_s == None and mid == None:
                return {}
            else:
                return {
                    'security_session_verify': yunsuo_s,
                    'security_session_mid_verify': mid
                }
        except Exception as e:
            print(str(e))
            print('failed to get cookies ')
            return False

    # get cookies for given proxy
    def get_cookies_proxy(self, url, proxy):
        try:
            proxy = {'http': '{}'.format(proxy), 'https': '{}'.format(proxy)}
            print('use%s'%proxy)
            yunsuo_s = self.s.get(url, proxies=proxy, timeout=GLOBAL_TIMEOUT_INDEX, headers=self.headers).cookies.get('security_session_verify')
            print(yunsuo_s)
            mid_resp = self.s.get('{}{}'.format(url, '&security_verify_data=313932302c31303830'),
                                                      proxies=proxy, headers=self.headers, timeout=GLOBAL_TIMEOUT_INDEX)
            mid = mid_resp.cookies.get('security_session_mid_verify')
            # check for captcha. ----------------->
            try:
                content = mid_resp.content.decode('utf-8','ignore')
                if '验证码不能为空' in content:
                    print('验证码')
                    soup = bs(content, 'lxml')
                    imgTag = soup.find('img', attrs={'alt': 'verify_img'})
                    imgdata = imgTag['src']
                    filename = self.decode_image(imgdata)
                    print(filename)
                    word = self.recog(filename)
                    if word == '':
                        return False
                    os.rename(filename, './captchas/'+word+'_{}.bmp'.format(uuid.uuid4()))
                    text = self.stringToHex(word)
                    high = self.s.post('{}&security_verify_img={}{}'.format(url, text,'&security_verify_data=313932302c31303830'),
                                proxies=proxy, headers=self.headers, timeout=GLOBAL_TIMEOUT_INDEX).cookies.get('security_session_high_verify')
                    return {
                        'security_session_verify': yunsuo_s,
                        'security_session_high_verify': high,
                        'security_session_mid_verify':mid
                    }
                else:
                    pass
            except Exception as e:
                self.save_exception(e)
                self.save_log_string('Exception in 验证码 logic')
                print('error in 验证码 logic')
                return False
            # captcha logic end here ---------------->

            # if captcha not showing up then just go through the normal process
            print(yunsuo_s, mid)
            if yunsuo_s == None and mid == None:
                return {}
            else:
                return {
                    'security_session_verify': yunsuo_s,
                    'security_session_mid_verify': mid
                }
        except Exception as e:
            print(str(e))
            print('failed to get cookies ')
            return False

    def set_proxy(self):
        try:
            time.sleep(random.random()*3 + random.random()*2)
            proxylist = getProxy()[:-1]
            print(proxylist)
            i = 0
            while i < 5:
                i+=1
                proxy = random.choice(proxylist)
                if proxy == '':
                    continue
                # print(proxy)
                # success->cookies string || fail-> False
                cookies = self.get_cookies_proxy('http://www.landchina.com/default.aspx?tabid=264&ComName=default')
                if cookies:
                    self.cookies = cookies
                    self.proxy = proxy
                    print('successfully set proxy')
                    # self.s.get('http://www.landchina.com/', cookies=self.cookies, timeout=GLOBAL_TIMEOUT_INDEX, headers=self.headers,
                    #            proxies={'http':self.proxy,'https':self.proxy})
                    return
                else:
                    continue

            print('reset proxy -> proxylist exhausted')
            self.set_proxy()
        except Exception as e:
            self.save_exception(e)
            self.save_log_string('error in set_proxy func')
            print('error in set_proc')
            self.set_proxy()

    def save(self, infos:list, filename:str) -> None:
        try:
            with open('./%s.csv'%filename, 'a', encoding='gb2312', newline='', errors='ignore') as f:
                writer = csv.writer(f)
                writer.writerow(infos)
        except Exception as e:
            self.save_exception(e)

    def run(self):
        # self.set_proxy()
        self.cookies = self.get_cookies('https://www.landchina.com/default.aspx?tabid=264&ComName=default')
        for month in range(1, 13):
            daylimit = [31,28,31,30,31,30,31,31,30,31,30,31][month-1]
            for day in range(1, daylimit+1):
                time.sleep(1.5+random.random()*3)
                datestring = '{0}-{1}-{2}~{0}-{1}-{2}'.format(self.year, month, day)
                print(datestring)
                self.get_list_page(self.tabid, datestring)

    def get_with_proxy(self, url, retryCount=0):
        if retryCount >= 10:
            return None
        try:
            resp = self.s.get(url, headers=self.headers, cookies=self.cookies, timeout=GLOBAL_TIMEOUT_INDEX, proxies= {'http':self.proxy,'https':self.proxy})
            content = resp.content.decode('gb2312', 'ignore')
            if 'YunSuoAutoJump()' in content:
                retryCount += 1
                self.set_proxy()
                return self.get_with_proxy(url, retryCount)
            elif resp.status_code == 200:
                return resp
            else:
                self.save_log_string('statuscode error')
                time.sleep(random.random()*5)
                self.set_proxy()
                retryCount += 1
                return self.get_with_proxy(url, retryCount)
        except Exception as e:
            self.save_exception(e)
            self.set_proxy()
            retryCount += 1
            return self.get_with_proxy(url, retryCount)

    def post_with_proxy(self, url, data, retryCount=0):
        if retryCount >= 10:
            return None
        try:
            print(self.proxy)
            resp = self.s.post(url, headers=self.headers, cookies=self.cookies, timeout=GLOBAL_TIMEOUT_INDEX,
                               proxies= {'http':self.proxy,'https':self.proxy},
                               data=data)
            content = resp.content.decode('gb2312', 'ignore')
            if 'YunSuoAutoJump()' in content:
                print('cookies 过期')
                retryCount += 1
                self.set_proxy()
                return self.post_with_proxy(url, data, retryCount)
            elif resp.status_code == 200:
                return resp
            else:
                print('status %s'%resp.status_code)
                self.save_log_string('statuscode error %s'%resp.status_code)
                time.sleep(random.random()*5)
                self.set_proxy()
                retryCount += 1
                return self.post_with_proxy(url, data, retryCount)
        except Exception as e:
            time.sleep(random.random() * 5)
            self.save_exception(e)
            self.set_proxy()
            retryCount += 1
            return self.post_with_proxy(url, data, retryCount)

    def process_verify_img(self, resp):
        '''
        disposed method
        will be removed later
        '''
        content = resp.content.decode('utf-8')
        soup = bs(content, 'lxml')
        imgTag = soup.find('img', attrs={'alt':'verify_img'})
        imgdata = imgTag['src']
        captchaPath = self.decode_image(imgdata)

    def write_compensate(self):
        index = {}
        with open('./indexed_result.csv', 'r', encoding='gb2312', errors='ignore') as f:
            reader = csv.reader(f)
            for row in reader:
                index.update({row[0]: row})
        with open('./lanchina_market_detail.csv', encoding='gb2312', errors='ignore') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    index.pop(row[0])
                except:
                    pass
        with open('./compensate.csv', 'a', encoding='gb2312', errors='ignore', newline='') as f:
            writer = csv.writer(f)
            for key, value in index.items():
                writer.writerow(value)

    def save_exception(self, e:Exception):
        with open('./Exceptions.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')

    def save_log_string(self, string:str):
        with open('./Exceptions.txt', 'a') as f:
            f.write(str(string))
            f.write('\n')

    def exstract_preview_landtransfer(self, tag) -> list:
        try:
            tds = tag.find_all('td')
            item1 = tds[1].text # 行政区
            link = 'https://www.landchina.com/' + tds[2].a['href']
            item2 = tds[2].text # 供应公告标题
            # original_user = tds[3].text
            item3 = tds[3].text #公告类型
            # now_user = tds[4].text
            item4 = tds[4].text # 发布时间
            item5 = tds[5].text # 网上创建时间
            infos = [item1, link, item2, item3, item4, item5]
            return infos
        except Exception as e:
            self.save_log_string('error when exstract_preview')
            self.save_exception(e)

    # component function for get_list_page
    def exstract_preview_from_itemTag(self, tag) -> list:
        try:
            tds = tag.find_all('td')
            district_name = tds[1].text
            link = 'https://www.landchina.com/' + tds[2].a['href']
            location = tds[2].text
            total_size = tds[3].text
            usage = tds[4].text
            # provide_method = tds[5].text
            # date = tds[6].text
            infos = [district_name, link, location, total_size, usage]
            return infos
        except Exception as e:
            self.save_exception(e)


    def get_list_page(self, tabid: int, datestring: str):
        '''
        :param tabid:  324 for 结果公告
        264 市场交易-土地转让
        :return:
        '''
        url = "http://www.landchina.com/default.aspx?tabid=%s&ComName=default" % tabid
        # loop for all 200 pages if possible
        for pagenum in range(1, 200):
            time.sleep(2 + random.random()*3)
            # TODO : Change the payload indexed to get different list page
            payload = {'TAB_QueryConditionItem': '598bdde3-078b-4c9b-b460-2e0b2d944e86',
                       'TAB_QuerySubmitPagerData':'%s'% pagenum,
                       'TAB_QuerySubmitConditionData': '598bdde3-078b-4c9b-b460-2e0b2d944e86:%s' % datestring,
                       # 'mainModuleContainer_492_1114_495_TabMenu1_selected_index':2 # select block
                        }
            # print(payload)
            # get response
            try:
                response = my_post(self.s, url, data=payload, header=self.headers, cookies=self.cookies)
                if not response:
                    continue
            except Exception as e:
                self.save_log_string('error in date %s page %s'%(datestring, pagenum))
                print('timeout')
                self.save_exception(e)
                continue
            # check for cookies validity
            try:
                content = response.content.decode('utf-8', 'ignore')
                if 'YunSuoAutoJump()' in content:
                    self.cookies = self.get_cookies(url)
                    response = my_post(self.s, url, data=payload, header=self.headers, cookies=self.cookies)
                else:
                    pass
            except Exception as e:
                self.save_log_string('error in get list page')
                self.save_exception(e)
                continue
            # extract info
            try:
                content = response.content.decode('gb2312', errors='ignore')
                soup = bs(content, 'lxml')
                # get tags (this fking website just hide another 2 search box for fun)
                # TODO: fix top root label here(can be 1 2 3 or None)
                # sourceTag = soup.find('table', attrs={'id':'top3_contentTable'})
                itemTags = []
                itemTags += soup.find_all('tr', attrs={'class': 'gridItem'})
                itemTags += soup.find_all('tr', attrs={'class': 'gridAlternatingItem'})

                print('%s page %s find %s' % (datestring, pagenum, len(itemTags)))
                # extract info and add to the infolist
                for tag in itemTags:
                    infos = self.exstract_preview_landtransfer(tag)
                    self.queue.put(infos)
                # if today has no more record, break loop
                if len(itemTags) < 30 :
                    break
            except Exception as e:
                self.save_exception(e)


def save_exception(e:Exception):
    with open('./Exceptions.txt', 'a') as f:
        f.write(str(e))
        f.write('\n')

def save_log_string(string:str):
        with open('./Exceptions.txt', 'a') as f:
            f.write(str(string))
            f.write('\n')

def save(infos:list, filepath:str) -> None:
    try:
        with open(filepath, 'a', encoding='gb2312', newline='', errors='ignore') as f:
            writer = csv.writer(f)
            writer.writerow(infos)
    except Exception as e:
        save_exception(e)

def writer_worker(q):
    print('writer started')
    while True:
        infos = q.get(timeout=2000)
        if type(infos) != list:
            LandCrawler.save_log_string('not list in queue!')
            print('not list in queue')
            save_log_string('not list in queue!')
        else:
            save(infos, './Data/出让公告.csv')


def start_listpage_task():
    q = Queue()
    thread_pool = []
    # start write worker function
    writer = Thread(target=writer_worker, args=(q,))
    writer.start()
    if not os.path.exists('./Data/出让公告.csv'):
        save(
            ['行政区','Link','供应公告标题','公告类型', '发布时间', '网上创建时间']
            , './Data/出让公告.csv')
    for year in range(2010, 2021):
        # thread_pool.append(LandCrawler(q, 'listpage thread', tabid=264, year=year))
        # TODO: let tabid auto recog here
        t = LandCrawler(q, 'listpage thread', tabid=261, year=year)
        t.start()
        t.join()
    # for t in thread_pool:
    #     t.start()
    # print(thread_pool)
    # for t in thread_pool:
    #     t.join()


if __name__ == '__main__':
    start_listpage_task()


