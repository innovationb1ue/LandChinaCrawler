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
from utilsDIR.extract_landTransfer import extract_landTrans
from utilsDIR.extract_landLending import extract_landLending
from utilsDIR.extract_landMortgage import extract_landMortgage
from utilsDIR.extract_sellNotice import extract_Notice
from woff.process_woff import get_font_dict
from utilsDIR.Saves import *

GLOBAL_TIMEOUT_INDEX = 10

class LandCrawler(Thread):
    def __init__(self, queue, thread_name, tasklist=None, tabid=0):
        # init procedures
        Thread.__init__(self, name=thread_name)
        self.queue = queue
        self.s = requests.Session()
        self.cookies = ''
        self.proxy = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        }
        self.tasklist = tasklist
        self.tabid = tabid
        self.FontDict = get_font_dict('./woff/YQrFiPvT3SaifS4J3BLtxTgci0q3oe0B.woff')
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
            save_exception(e)
            save_log_string('exception in recog func')
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
        val = ''
        for i in string:
            if val == '':
                val = '3' + i
            else:
                val += '3' + i
        return val

    # get cookies for given proxy
    def get_cookies_proxy(self, url, proxy):
        try:
            proxy = {'http': '{}'.format(proxy), 'https': '{}'.format(proxy)}
            yunsuo_s_resp = self.s.get(url, timeout=GLOBAL_TIMEOUT_INDEX, headers=self.headers,
                                       proxies=proxy)
            yunsuo_s = yunsuo_s_resp.cookies.get('security_session_verify')
            mid_resp = self.s.get('{}{}'.format(url, '&security_verify_data=313932302c31303830'),
                                                      headers=self.headers, timeout=GLOBAL_TIMEOUT_INDEX,
                                  proxies=proxy)
            mid = mid_resp.cookies.get('security_session_mid_verify')
            # check for captcha. ----------------->
            # try:
            #     content = mid_resp.content.decode('utf-8','ignore')
            #     if '验证码不能为空' in content:
            #         print('验证码')
            #         soup = bs(content, 'lxml')
            #         imgTag = soup.find('img', attrs={'alt': 'verify_img'})
            #         imgdata = imgTag['src']
            #         filename = self.decode_image(imgdata)
            #         print(filename)
            #         word = self.recog(filename)
            #         if word == '':
            #             return False
            #         os.rename(filename, './captchas/'+word+'_{}.bmp'.format(uuid.uuid4()))
            #         text = self.stringToHex(word)
            #         high = self.s.post('{}&security_verify_img={}{}'.format(url, text,'&security_verify_data=313932302c31303830'),
            #                     proxies=proxy, headers=self.headers, timeout=GLOBAL_TIMEOUT_INDEX).cookies.get('security_session_high_verify')
            #         return {
            #             'security_session_verify': yunsuo_s,
            #             'security_session_high_verify': high,
            #             'security_session_mid_verify':mid
            #         }
            #     else:
            #         pass
            # except Exception as e:
            #     save_exception(e)
            #     save_log_string('Exception in 验证码 logic')
            #     print('error in 验证码 logic')
            #     return False
            # captcha logic end here ---------------->

            # if captcha not showing up then just go through the normal process
            print(yunsuo_s, mid)
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
            time.sleep(random.random()*6 + random.random()*3)
            proxylist = getProxy()
            Count = 0
            while Count < 5:
                proxy = random.choice(proxylist)
                Count += 1
                if proxy == '':
                    continue
                # success->cookies string || fail-> False
                cookies = self.get_cookies_proxy('https://www.landchina.com/default.aspx?tabid=264&ComName=default',
                                                                    proxy)
                if cookies:
                    self.cookies = cookies
                    self.proxy = proxy
                    # self.s.get('http://www.landchina.com/', cookies=self.cookies, timeout=GLOBAL_TIMEOUT_INDEX, headers=self.headers,
                    #            proxies={'http':self.proxy,'https':self.proxy})
                    print('successfully set proxy')
                    return
                else:
                    continue
            print('reset proxy -> proxylist exhausted')
            self.set_proxy()
        except Exception as e:
            save_exception(e)
            save_log_string('error in set_proxy func')
            print('error in set_proxy func')
            self.set_proxy()


    def run(self):
        self.set_proxy()
        for row in self.tasklist:
            try:
                resp = self.get_with_proxy(row[2])
                # row + infos
                result = extract_Notice(resp.content, self.FontDict)
                result = row + [result]
                self.queue.put(result)
                time.sleep(random.random()*3)
            except Exception as e:
                save_exception(e)

    def get_with_proxy(self, url, retryCount=0):
        if retryCount >= 10:
            return None
        try:
            headers = {'Host': 'www.landchina.com',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
                       'Sec-Fetch-Dest': 'document',
                       'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                       'Sec-Fetch-Site': 'none',
                       'Sec-Fetch-Mode': 'navigate',
                       'Sec-Fetch-User': '?1',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'Accept-Language': 'zh-CN,zh;q=0.9', }
            resp = self.s.get(url, headers=headers, cookies=self.cookies, timeout=GLOBAL_TIMEOUT_INDEX,
                              proxies= {'http':self.proxy,'https':self.proxy})
            content = resp.content.decode('gb2312', 'ignore')
            if 'YunSuoAutoJump()' in content:
                print('AutoJump show up')
                retryCount += 1
                self.set_proxy()
                return self.get_with_proxy(url, retryCount)
            elif resp.status_code == 200:
                return resp
            else:
                save_log_string('statuscode error')
                time.sleep(random.random()*5)
                self.set_proxy()
                retryCount += 1
                return self.get_with_proxy(url, retryCount)
        except Exception as e:
            save_exception(e)
            self.set_proxy()
            retryCount += 1
            return self.get_with_proxy(url, retryCount)

    def post_with_proxy(self, url, data, retryCount=0):
        if retryCount >= 10:
            return None
        try:
            resp = self.s.post(url, headers=self.headers, cookies=self.cookies, timeout=GLOBAL_TIMEOUT_INDEX,
                               proxies= {'http':self.proxy,'https':self.proxy},
                               data=data)
            content = resp.content.decode('gb2312', 'ignore')
            if 'YunSuoAutoJump()' in content:
                retryCount += 1
                self.set_proxy()
                return self.post_with_proxy(url, data, retryCount)
            elif resp.status_code == 200:
                return resp
            else:
                save_log_string('statuscode error %s'%resp.status_code)
                time.sleep(random.random()*5)
                self.set_proxy()
                retryCount += 1
                return self.post_with_proxy(url, data, retryCount)
        except Exception as e:
            time.sleep(random.random() * 5)
            save_exception(e)
            self.set_proxy()
            retryCount += 1
            return self.post_with_proxy(url, data, retryCount)


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

    # return info : list (discarded for now)
    def get_result_details_proxy(self, row:list) -> list:
        # infos = [district_name, link, location, total_size, usage, provide_method, date]
        # url located in column 3
        try:
            url = row[2]
        except:
            save_log_string('no url')
            return []
        try:
            resp = self.get_with_proxy(url)
            if resp:
                content = resp.content.decode('gb2312', errors='ignore')
            else:
                return row

            # check for show up of captcha code
            try:
                # check for 验证码
                if '验证码不能为空' in resp.content.decode('utf-8', errors='ignore'):
                    self.set_proxy()
                    return self.get_result_details_proxy(row)
            except:
                pass

            soup = bs(content, 'lxml')
            # substract infos
            try:
                district = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c2_ctrl'}).text.strip()
            except:
                district = ''
            try:
                monitor_num = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl'}).text.strip()
            except:
                monitor_num = ''
                save_log_string('no monitor num')
            try:
                proj_name = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r17_c2_ctrl'}).text.strip()
            except:
                proj_name=''
                save_log_string('no proj name')
            try:
                proj_location = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r16_c2_ctrl'}).text.strip()
            except:
                proj_location = ''
            try:
                square = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl'}).text.strip()
            except:
                square = ''
            try:
                # mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c4_ctrl
                land_source = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c4_ctrl'}).text.strip()
                if land_source == square:
                    land_source = "现有建设用地"
                elif land_source == 0:
                    land_source = "新增建设用地"
                else:
                    land_source = "新增建设用地(来自存量库)"
            except:
                land_source = ''
            try:
                land_usage = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl'}).text.strip()
            except:
                land_usage = ''
            try:
                provide_form = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl'}).text.strip()
            except:
                provide_form=''
            try:
                time_limit = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c2_ctrl'}).text.strip()
            except:
                time_limit=''
            try:
                market_type = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c4_ctrl'}).text
            except:
                market_type = ''
            try:
                land_level = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c2_ctrl'}).text
                # mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c4_ctrl
                price = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c4_ctrl'}).text
            except:
                land_level= ''
                price= ''
            # 分期付款info
            try:
                # mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3
                table = soup.find('table', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3'})
                records = table.find_all('tr')[3:] # drop the first header item
                period_num=''
                deal_pay_date=''
                deal_pay_price=''
                backup=''
                for record in records:
                    # record is the row element (tr)
                    tds = record.find_all('td') # blocks
                    period = tds[0].text.strip()
                    date = tds[1].text.strip()
                    payment = tds[2].text.strip()
                    if len(period_num) > 0:
                        period_num = period_num + '_' + period
                    else:
                        period_num = period
                    if len(deal_pay_date) > 0:
                        deal_pay_date = deal_pay_date + '_' + date
                    else:
                        deal_pay_date = date
                    if len(deal_pay_price) > 0:
                        deal_pay_price = deal_pay_price + '_' + payment
                    else:
                        deal_pay_price = payment

            except Exception as e:
                print(str(e))
                period_num=''
                deal_pay_date=''
                deal_pay_price=''
                backup=''
            # 产权人info   2 posible position
            try:
                right_people_1 = soup.find('span',attrs={'id': 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9_c2_ctrl'}).text
                right_people_2 = soup.find('span',attrs={'id': 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r23_c2_ctrl'}).text
                right_people = str(right_people_1)+str(right_people_2)
            except:
                right_people = ''

            # 下半部分info
            try:
                lower_bound = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c2_ctrl'}).text
                upper_bound = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c4_ctrl'}).text
                deal_give_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21_c4_ctrl'}).text
                deal_start_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c2_ctrl'}).text
                deal_finish_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c4_ctrl'}).text
                start_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r10_c2_ctrl'}).text
                finish_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r10_c4_ctrl'}).text
                approval = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c2_ctrl'}).text
                sign_date = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c4_ctrl'}).text
            except:
                lower_bound = ''
                upper_bound = ''
                deal_give_time = ''
                deal_start_time = ''
                deal_finish_time = ''
                start_time = ''
                finish_time = ''
                approval = ''
                sign_date = ''
            # titles = ['行政区','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','批准单位','合同签订日期']

            if  approval != '' and approval.find('人民政府') < 0 :
                approval += '人民政府'

            infos = [monitor_num,
                     proj_name,
                     proj_location,
                     square,
                     land_source,
                     land_usage,
                     provide_form,
                     time_limit,
                     market_type,
                     land_level,
                     price,
                     period_num,
                     deal_pay_date,
                     deal_pay_price,
                     backup,
                     right_people,
                     lower_bound,
                     upper_bound,
                     deal_give_time,
                     deal_start_time,
                     deal_finish_time,
                     start_time,
                     finish_time,
                     approval,
                     sign_date,]
            # replace district full name
            row[1] = district
            row[3] = proj_location
            infos = row + infos
            print('sign_date : ', sign_date)
            return infos
        except Exception as e:
            print('error in get_result_detail_proxy')
            save_exception(e)
            save_log_string('error in get_result_detail_proxy')
            return []


def writer_worker(q, filepath):
    print('writer started')
    while True:
        infos = q.get(timeout=20000)
        if type(infos) != list:
            save_log_string('not list in queue!')
            print('not list in queue')
            save_log_string('not list in queue!')
        else:
            # TODO: need to swtich save func here
            save(infos,filepath)

def start_detail_task():
    MAX_TASK_COUNT = 100000
    INDEXED_FILE_PATH = './Data/indexed-出让公告.csv'
    DETAIL_FILE_PATH = './Data/出让公告-detail.csv'
    print(INDEXED_FILE_PATH)
    q = Queue()
    thread_pool = []
    # start write worker function
    writer = Thread(target=writer_worker, args=(q,DETAIL_FILE_PATH))
    writer.start()
    # init header for csv file
    if not os.path.exists(DETAIL_FILE_PATH):
        # save(
        #     ['index','Link' ,'宗地标识', '宗地编号', '宗地座落','所在行政区', '原土地使用权人', '现土地使用权人', '土地面积(公顷)',
        #      '土地用途', '土地使用权类型', '土地使用年限', '土地利用状况', '土地级别', '转让方式', '转让价格(万元)', '成交时间']
        #     , './Data/市场交易-土地出租_detail.csv')
        # save(['index', '行政区', 'Link', '宗地标识', '宗地编号', '宗地座落','所在行政区', '行政区号码', '土地使用权证号',
        #       '土地面积', '土地用途', '土地级别', '土地利用状况', '出租期限', '到期时间', '合同签订时间', '年租金总额']
        #      , './Data/市场交易-土地出租_detail.csv')
        # save(['index', '行政区','Link','土地坐落','抵押面积','抵押土地用途', # row
        #       '宗地标识', '宗地编号','所在行政区', '行政区号码', '宗地座落', '土地面积', '土地他项权利人证号',
        #       '土地使用权证号', '土地抵押人名称', '土地抵押人性质', '土地抵押权人', '抵押土地用途', '抵押土地权属性质与使用权类型',
        #       '抵押面积(公顷)', '评估金额(万元)', '抵押金额(万元)', '土地抵押登记起始时间', '土地抵押登记结束时间'
        #       ],
        #      './Data/出让公告-detail.csv')
        save(['index', '行政区', 'Link', '公告类型', '发布时间', '网上创建时间', 'html'],
             DETAIL_FILE_PATH)

    # load previews and urls
    with open(INDEXED_FILE_PATH, 'r', encoding='gb2312', errors='ignore') as f:
        count = 0
        reader = csv.reader(f)
        temp_task = []
        task_count = 0
        line = 1
        for i in reader:
            if line == 1:
                line += 1
                continue
            temp_task.append(i)
            count += 1
            if count > MAX_TASK_COUNT:
                # start(temp_task, q) # single process run test
                count = 0
                task_count += 1
                print('apply task %s' % task_count)
                thread_pool.append(LandCrawler(q, 'thread %s' % task_count, tasklist=temp_task))
                # release memory manually
                temp_task = []
                gc.collect()
                # test lines below
                # break
        # assign the last task
        task_count += 1
        thread_pool.append(LandCrawler(q, 'thread %s' % task_count,tasklist=temp_task))
        print('assgin done')
        del (temp_task)
        gc.collect()

        for t in thread_pool:
            t.start()
        print(thread_pool)
        for t in thread_pool:
            t.join()


if __name__ == '__main__':
    start_detail_task()


