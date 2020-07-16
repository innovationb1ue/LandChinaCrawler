import requests
from bs4 import BeautifulSoup as bs
import csv
import time
import os
from multiprocessing import Pool, Queue
import gc
from proxy_module import getProxy, get_page, API

q = Queue()

# titles = ['index','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','约定开工日期','约定竣工时间','实际开工时间','实际竣工','批准单位','合同签订日期'


class LandCrawler():
    def __init__(self, q=None):
        self.q = q
        self.s =requests.Session()
        self.cookies = ''
        self.refresh_cookies()
        self.proxy = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        }

    def get_cookies(self, url, pagenum):
        try:
            payload = {'TAB_QuerySortItemList': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
                       'TAB_QuerySubmitPagerData': '%s'%pagenum,
                       '__VIEWSTATE': '/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6IzAwMDAwMDtCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2dkamhfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfA2QWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwF/AY8cCBhbGlnbj0iY2VudGVyIj48c3BhbiBzdHlsZT0iZm9udC1zaXplOiB4LXNtYWxsIj4mbmJzcDs8YnIgLz4NCiZuYnNwOzxhIHRhcmdldD0iX3NlbGYiIGhyZWY9Imh0dHBzOi8vd3d3LmxhbmRjaGluYS5jb20vIj48aW1nIGJvcmRlcj0iMCIgYWx0PSIiIHdpZHRoPSIyNjAiIGhlaWdodD0iNjEiIHNyYz0iL1VzZXIvZGVmYXVsdC9VcGxvYWQvZmNrL2ltYWdlL3Rkc2N3X2xvZ2UucG5nIiAvPjwvYT4mbmJzcDs8YnIgLz4NCiZuYnNwOzxzcGFuIHN0eWxlPSJjb2xvcjogI2ZmZmZmZiI+Q29weXJpZ2h0IDIwMDgtMjAxOSBEUkNuZXQuIEFsbCBSaWdodHMgUmVzZXJ2ZWQmbmJzcDsmbmJzcDsmbmJzcDsgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPg0KdmFyIF9iZGhtUHJvdG9jb2wgPSAoKCJodHRwczoiID09IGRvY3VtZW50LmxvY2F0aW9uLnByb3RvY29sKSA/ICIgaHR0cHM6Ly8iIDogIiBodHRwczovLyIpOw0KZG9jdW1lbnQud3JpdGUodW5lc2NhcGUoIiUzQ3NjcmlwdCBzcmM9JyIgKyBfYmRobVByb3RvY29sICsgImhtLmJhaWR1LmNvbS9oLmpzJTNGODM4NTM4NTljNzI0N2M1YjAzYjUyNzg5NDYyMmQzZmEnIHR5cGU9J3RleHQvamF2YXNjcmlwdCclM0UlM0Mvc2NyaXB0JTNFIikpOw0KPC9zY3JpcHQ+Jm5ic3A7PGJyIC8+DQrniYjmnYPmiYDmnIkmbmJzcDsg5Lit5Zu95Zyf5Zyw5biC5Zy6572RJm5ic3A7Jm5ic3A75oqA5pyv5pSv5oyBOua1meaxn+iHu+WWhOenkeaKgOiCoeS7veaciemZkOWFrOWPuCZuYnNwOzxiciAvPg0K5aSH5qGI5Y+3OiDkuqxJQ1DlpIcwOTA3NDk5MuWPtyDkuqzlhaznvZHlronlpIcxMTAxMDIwMDA2NjYoMikmbmJzcDs8YnIgLz4NCjwvc3Bhbj4mbmJzcDsmbmJzcDsmbmJzcDs8YnIgLz4NCiZuYnNwOzwvc3Bhbj48L3A+HwEFZEJBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3cyMDEzX3l3XzEuanBnKTtkZE7708COJcrCEa3ChM4IYD0Oc18rkXhLzt32qZGyq8/r'}
            return {
                'yunsuo_session_verify': self.s.post(url, data=payload, timeout=8).cookies.get('yunsuo_session_verify'),
                'security_session_mid_verify': self.s.post('{}{}'.format(url, '&security_verify_data=313932302c31303830'),)
                .cookies.get('security_session_mid_verify')
            }
        except Exception as e:
            print('get cookies time out')
            self.save_exception(e)

    # get cookies for given proxy
    def get_cookies_proxy(self, url, proxy):
        payload = {'TAB_QuerySortItemList': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
                   'TAB_QuerySubmitPagerData': '1',
                   '__VIEWSTATE': '/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6IzAwMDAwMDtCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2dkamhfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfA2QWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwF/AY8cCBhbGlnbj0iY2VudGVyIj48c3BhbiBzdHlsZT0iZm9udC1zaXplOiB4LXNtYWxsIj4mbmJzcDs8YnIgLz4NCiZuYnNwOzxhIHRhcmdldD0iX3NlbGYiIGhyZWY9Imh0dHBzOi8vd3d3LmxhbmRjaGluYS5jb20vIj48aW1nIGJvcmRlcj0iMCIgYWx0PSIiIHdpZHRoPSIyNjAiIGhlaWdodD0iNjEiIHNyYz0iL1VzZXIvZGVmYXVsdC9VcGxvYWQvZmNrL2ltYWdlL3Rkc2N3X2xvZ2UucG5nIiAvPjwvYT4mbmJzcDs8YnIgLz4NCiZuYnNwOzxzcGFuIHN0eWxlPSJjb2xvcjogI2ZmZmZmZiI+Q29weXJpZ2h0IDIwMDgtMjAxOSBEUkNuZXQuIEFsbCBSaWdodHMgUmVzZXJ2ZWQmbmJzcDsmbmJzcDsmbmJzcDsgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPg0KdmFyIF9iZGhtUHJvdG9jb2wgPSAoKCJodHRwczoiID09IGRvY3VtZW50LmxvY2F0aW9uLnByb3RvY29sKSA/ICIgaHR0cHM6Ly8iIDogIiBodHRwczovLyIpOw0KZG9jdW1lbnQud3JpdGUodW5lc2NhcGUoIiUzQ3NjcmlwdCBzcmM9JyIgKyBfYmRobVByb3RvY29sICsgImhtLmJhaWR1LmNvbS9oLmpzJTNGODM4NTM4NTljNzI0N2M1YjAzYjUyNzg5NDYyMmQzZmEnIHR5cGU9J3RleHQvamF2YXNjcmlwdCclM0UlM0Mvc2NyaXB0JTNFIikpOw0KPC9zY3JpcHQ+Jm5ic3A7PGJyIC8+DQrniYjmnYPmiYDmnIkmbmJzcDsg5Lit5Zu95Zyf5Zyw5biC5Zy6572RJm5ic3A7Jm5ic3A75oqA5pyv5pSv5oyBOua1meaxn+iHu+WWhOenkeaKgOiCoeS7veaciemZkOWFrOWPuCZuYnNwOzxiciAvPg0K5aSH5qGI5Y+3OiDkuqxJQ1DlpIcwOTA3NDk5MuWPtyDkuqzlhaznvZHlronlpIcxMTAxMDIwMDA2NjYoMikmbmJzcDs8YnIgLz4NCjwvc3Bhbj4mbmJzcDsmbmJzcDsmbmJzcDs8YnIgLz4NCiZuYnNwOzwvc3Bhbj48L3A+HwEFZEJBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3cyMDEzX3l3XzEuanBnKTtkZE7708COJcrCEa3ChM4IYD0Oc18rkXhLzt32qZGyq8/r'}

        try:
            proxy = {'http': '{}'.format(proxy), 'https': '{}'.format(proxy)}
            # print(proxy)
            return {
                'yunsuo_session_verify': self.s.post(url,proxies=proxy,data=payload, timeout=6).cookies.get('yunsuo_session_verify'),
                'security_session_mid_verify': self.s.post('{}{}'.format(url, '&security_verify_data=313932302c31303830'),
                                                             proxies=proxy, headers=self.headers, timeout=6).cookies.get('security_session_mid_verify')
            }
        except Exception as e:
            print('error in get_cookies_proxy')
            return False

    def set_proxy(self):
        try:
            proxylist = getProxy()
            for proxy in proxylist:
                # success->cookies string || fail->return False
                cookies = self.get_cookies_proxy('https://www.landchina.com/default.aspx?tabid=263&ComName=default',
                                                      proxy)
                if cookies:
                    self.cookies = cookies
                    self.proxy = proxy
                    print('successfully set proxy')
                    return
                else:
                    continue
            print('重新set proxy')
            self.set_proxy()
        except Exception as e:

            self.save_exception(e)
            print('error in set proxy')
            self.set_proxy()

    def refresh_cookies(self):
        self.cookies = self.get_cookies('https://www.landchina.com/default.aspx?tabid=263&ComName=default', 2)

    def save_queue(self, infos:list):
        try:
            q.put(infos)
        except Exception as e:
            self.save_exception(e)

    def writer_worker(self):
        while True:
            print('loop start')
            infos = q.get(timeout=2000)
            print(infos)
            print('get one ')
            if type(infos) != list:
                self.save_log_string('not list in queue!')
            else:
                self.save(infos, 'lanchina_market_detail')


    def save(self, infos:list, filename:str) -> None:
        try:
            with open('./%s.csv'%filename, 'a', encoding='gb2312', newline='', errors='ignore') as f:
                writer = csv.writer(f)
                writer.writerow(infos)
        except Exception as e:
            self.save_exception(e)

    def save_index(self, i:int):
        with open('./pagenum.txt', 'w') as f:
            f.write(str(i))

    def start_listpage_task(self, tabid:int, yearstart:int, yearend:int):
        for year in range(yearstart, yearend + 1):
            for month in range(1, 13):
                daylimit = [31,28,31,30,31,30,31,31,30,31,30,31][month-1]
                for day in range(1, daylimit+1):
                    datestring = '{0}-{1}-{2}~{0}-{1}-{2}'.format(year, month, day)
                    self.get_list_page(tabid, datestring)

    def start_multiprocess_detail_task(self, worker=5, max_task_count=200000, useproxy=False):
        if not os.path.exists('./lanchina_market_detail.csv'):
            # titles = ['行政区','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','约定开工日期','约定竣工时间','实际开工时间', '实际竣工','批准单位','合同签订日期']
            self.save(['index','行政区','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','约定开工日期','约定竣工时间','实际开工时间', '实际竣工','批准单位','合同签订日期']
                       ,'lanchina_market_detail')
        # load previews and urls
        with open('./indexed_result.csv', 'r', encoding='gb2312', errors='ignore') as f:
            count = 0
            reader = csv.reader(f)
            temp_task = []
            task_count = 0
            p = Pool(worker)
            # start the write function first
            p.apply_async(self.writer_worker)
            print('applied writer worker')
            for i in reader:
                temp_task.append(i)
                count += 1
                if count > max_task_count:
                    count=0
                    p.apply_async(self.multi_detail_woker, args=(temp_task, useproxy))
                    task_count += 1
                    print('apply task %s'%task_count)
                    # release memory manually
                    del(temp_task)
                    gc.collect()
                    temp_task = []
            # assign the last task
            p.apply_async(self.multi_detail_woker, args=(temp_task, useproxy))
            print('assgin done')
            del(temp_task)
            gc.collect()
            p.close()
            p.join()

    def multi_detail_woker(self, tasklist:list, useproxy=False):
        try:
            if useproxy:
                self.set_proxy()
                for row in tasklist:
                    infos = self.get_result_details_proxy(row)
                    # self.save(infos, 'lanchina_market_detail')
                    q.put(infos)
            else:
                 for row in tasklist:
                    infos = self.get_result_details(row)
                    # self.save(infos, 'lanchina_market_detail')
                    q.put(infos)
        except Exception as e:
            self.save_exception(e)

    def start_result_detail_task(self):
        '''
        结果公告
        :return:
        '''
        if not os.path.exists('./lanchina_market_detail.csv'):
            # titles = ['index','行政区','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','约定开工日期','约定竣工时间','实际开工时间', '实际竣工','批准单位','合同签订日期']
            self.save(['index','行政区','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','约定开工日期','约定竣工时间','实际开工时间', '实际竣工','批准单位','合同签订日期']
                       ,'lanchina_market_detail')
        with open('./lanchina_market_result.csv', 'r', encoding='gb2312') as f:
            reader = csv.reader(f)
            for row in reader:
                infos = self.get_result_details(row)
                self.save(infos, 'lanchina_market_detail')

    def get_with_cookies(self, url):
        try:
            resp = self.s.get(url, headers=self.headers, cookies=self.cookies, timeout=8)
            content = resp.content.decode('gb2312', 'ignore')
            if 'YunSuoAutoJump()' in content:
                self.refresh_cookies()
                return self.get_with_cookies(url)
            else:
                return resp
        except Exception as e:
            self.save_exception(e)
            return ''

    def get_with_proxy(self, url, retryCount=0):
        if retryCount >= 3:
            return None
        try:
            resp = self.s.get(url, headers=self.headers, cookies=self.cookies, timeout=6, proxies= {'http':self.proxy,'https':self.proxy})
            content = resp.content.decode('gb2312', 'ignore')
            if 'YunSuoAutoJump()' in content:
                retryCount += 1
                self.set_proxy()
                return self.get_with_proxy(url, retryCount)
            elif resp.status_code == 200:
                return resp
            else:
                self.save_log_string('statuscode error')
                self.save_log_string(url)
                self.set_proxy()
                retryCount += 1
                return self.get_with_proxy(url, retryCount)
        except Exception as e:
            self.save_exception(e)
            self.set_proxy()
            retryCount += 1
            return self.get_with_proxy(url, retryCount)

    def get_result_details_proxy(self, row:list) -> list:
        # infos = [district_name, link, location, total_size, usage, provide_method, date]

        # url located in column 3
        try:
            url = row[2]
        except:
            self.save_log_string('no url')
        try:
            resp = self.get_with_proxy(url)
            if resp:
                content = resp.content.decode('gb2312', errors='ignore')
            else:
                return []
            soup = bs(content, 'lxml')
            # substract infos
            try:
                monitor_num = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl'}).text
            except:
                monitor_num = ''
                self.save_log_string('no monitor num')
            try:
                proj_name = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r17_c2_ctrl'}).text
            except:
                proj_name=''
                self.save_log_string('no proj name')
            try:
                proj_location = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r16_c2_ctrl'}).text
            except:
                proj_location = ''
            try:
                square = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl'}).text
            except:
                square = ''
            try:
                land_source = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c4_ctrl'}).text
            except:
                land_source = ''
            try:
                land_usage = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl'}).text
            except:
                land_usage = ''
            try:
                provide_form = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl'}).text
            except:
                provide_form=''
            try:
                time_limit = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c2_ctrl'}).text
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
                period_num = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c1_0_ctrl'}).text
                deal_pay_date = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c2_0_ctrl'}).text
                deal_pay_parice = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c3_0_ctrl'}).text
                backup = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c4_0_ctrl'}).text
            except:
                period_num=''
                deal_pay_date=''
                deal_pay_parice=''
                backup=''
            # 产权人info   2 posible position
            try:
                right_people = soup.find('span',attrs={'id': 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9_c2_ctrl'}).text
            except:
                try:
                    # mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r23_c2_ctrl
                    right_people = soup.find('span', attrs={
                        'id': 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r23_c2_ctrl'}).text
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
                     deal_pay_parice,
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
            infos = row + infos
            print(sign_date)
            return infos
        except Exception as e:
            # print('error in get_result_detail_proxy')
            self.save_exception(e)
            self.save_log_string('error in get_result_detail_proxy')
            return ['']


    def get_result_details(self, row:list) -> list:
        # infos = [district_name, link, location, total_size, usage, provide_method, date]

        # url located in column 3
        try:
            url = row[2]
            resp = self.get_with_cookies(url)
            if resp:
                content = resp.content.decode('gb2312', errors='ignore')
            else:
                return []
            soup = bs(content, 'lxml')
            # substract infos
            monitor_num = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl'}).text
            proj_name = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r17_c2_ctrl'}).text
            proj_location = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r16_c2_ctrl'}).text
            square = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl'}).text
            land_source = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c4_ctrl'}).text
            land_usage = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl'}).text
            provide_form = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl'}).text
            time_limit = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c2_ctrl'}).text
            market_type = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c4_ctrl'}).text
            land_level = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c2_ctrl'}).text
            price = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c4_ctrl'}).text
            try:
                period_num = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c1_0_ctrl'}).text
                deal_pay_date = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c2_0_ctrl'}).text
                deal_pay_parice = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c3_0_ctrl'}).text
                backup = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f3_r2_c4_0_ctrl'}).text
                right_people = soup.find('span',attrs={'id': 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9_c2_ctrl'}).text
            except:
                try:
                    right_people = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r23_c2_ctrl'}).text
                except:
                    right_people = ''
                period_num=''
                deal_pay_date=''
                deal_pay_parice=''
                backup=''
                print('no 分期付款')
            lower_bound = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c2_ctrl'}).text
            upper_bound = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c4_ctrl'}).text
            deal_give_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21_c4_ctrl'}).text
            deal_start_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c2_ctrl'}).text
            deal_finish_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c4_ctrl'}).text
            start_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r10_c2_ctrl'}).text
            finish_time = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r10_c4_ctrl'}).text
            approval = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c2_ctrl'}).text
            sign_date = soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c4_ctrl'}).text
            # titles = ['行政区','Link','土地坐落','总面积','土地用途','供应方式','签订日期','电子监管号','项目名称','项目位置','面积（公顷）','土地来源','土地用途','供地方式','土地使用年限','行业分类','土地级别','成交价格（万元）','支付期号','约定支付日期','约定支付金额','备注','土地使用权人','下限','上限','约定交地时间','批准单位','合同签订日期']

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
                     deal_pay_parice,
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
            infos = row + infos
            print(sign_date)
            return infos
        except Exception as e:
            self.save_exception(e)

    def get_list_page(self, tabid:int, datestring:str) -> None:
        '''
        :param tabid:  324 for 结果公告
        :return:
        '''
        url = "http://www.landchina.com/default.aspx?tabid=%s&ComName=default" % tabid
        # loop for all 200 pages if possible
        for pagenum in range(1, 200):
            payload = {'TAB_QuerySortItemList': 'ef2af72e-5b46-49a5-8824-7bba173eb6a8:False',
                       'TAB_QuerySubmitPagerData': '%s'%pagenum,
                       'TAB_QuerySubmitConditionData': '9f2c3acd-0256-4da2-a659-6949c4671a2a:%s'%datestring, #  2019-12-5~2019-12-5
                       '__VIEWSTATE': '/wEPDwUJNjkzNzgyNTU4D2QWAmYPZBYIZg9kFgICAQ9kFgJmDxYCHgdWaXNpYmxlaGQCAQ9kFgICAQ8WAh4Fc3R5bGUFIEJBQ0tHUk9VTkQtQ09MT1I6I2YzZjVmNztDT0xPUjo7ZAICD2QWAgIBD2QWAmYPZBYCZg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHgRUZXh0ZWRkAgEPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFhwFDT0xPUjojRDNEM0QzO0JBQ0tHUk9VTkQtQ09MT1I6O0JBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3dfc3lfamhnZ18wMDAuZ2lmKTseBmhlaWdodAUBMxYCZg9kFgICAQ9kFgJmDw8WAh8CZWRkAgIPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYEZg9kFgJmDxYEHwEFIENPTE9SOiNEM0QzRDM7QkFDS0dST1VORC1DT0xPUjo7HwBoFgJmD2QWAgIBD2QWAmYPDxYCHwJlZGQCAg9kFgJmD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfAGgWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAICD2QWBGYPZBYCZg9kFgJmD2QWAmYPZBYCAgEPZBYCZg8WBB8BBYYBQ09MT1I6IzAwMDAwMDtCQUNLR1JPVU5ELUNPTE9SOjtCQUNLR1JPVU5ELUlNQUdFOnVybChodHRwOi8vd3d3LmxhbmRjaGluYS5jb20vVXNlci9kZWZhdWx0L1VwbG9hZC9zeXNGcmFtZUltZy94X3Rkc2N3X3p5X2dkamhfMDEuZ2lmKTsfAwUCNDYWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIBD2QWAmYPZBYCZg9kFgJmD2QWAgIBD2QWAmYPFgQfAQUgQ09MT1I6I0QzRDNEMztCQUNLR1JPVU5ELUNPTE9SOjsfA2QWAmYPZBYCAgEPZBYCZg8PFgIfAmVkZAIDD2QWAgIDDxYEHglpbm5lcmh0bWwF/AY8cCBhbGlnbj0iY2VudGVyIj48c3BhbiBzdHlsZT0iZm9udC1zaXplOiB4LXNtYWxsIj4mbmJzcDs8YnIgLz4NCiZuYnNwOzxhIHRhcmdldD0iX3NlbGYiIGhyZWY9Imh0dHBzOi8vd3d3LmxhbmRjaGluYS5jb20vIj48aW1nIGJvcmRlcj0iMCIgYWx0PSIiIHdpZHRoPSIyNjAiIGhlaWdodD0iNjEiIHNyYz0iL1VzZXIvZGVmYXVsdC9VcGxvYWQvZmNrL2ltYWdlL3Rkc2N3X2xvZ2UucG5nIiAvPjwvYT4mbmJzcDs8YnIgLz4NCiZuYnNwOzxzcGFuIHN0eWxlPSJjb2xvcjogI2ZmZmZmZiI+Q29weXJpZ2h0IDIwMDgtMjAxOSBEUkNuZXQuIEFsbCBSaWdodHMgUmVzZXJ2ZWQmbmJzcDsmbmJzcDsmbmJzcDsgPHNjcmlwdCB0eXBlPSJ0ZXh0L2phdmFzY3JpcHQiPg0KdmFyIF9iZGhtUHJvdG9jb2wgPSAoKCJodHRwczoiID09IGRvY3VtZW50LmxvY2F0aW9uLnByb3RvY29sKSA/ICIgaHR0cHM6Ly8iIDogIiBodHRwczovLyIpOw0KZG9jdW1lbnQud3JpdGUodW5lc2NhcGUoIiUzQ3NjcmlwdCBzcmM9JyIgKyBfYmRobVByb3RvY29sICsgImhtLmJhaWR1LmNvbS9oLmpzJTNGODM4NTM4NTljNzI0N2M1YjAzYjUyNzg5NDYyMmQzZmEnIHR5cGU9J3RleHQvamF2YXNjcmlwdCclM0UlM0Mvc2NyaXB0JTNFIikpOw0KPC9zY3JpcHQ+Jm5ic3A7PGJyIC8+DQrniYjmnYPmiYDmnIkmbmJzcDsg5Lit5Zu95Zyf5Zyw5biC5Zy6572RJm5ic3A7Jm5ic3A75oqA5pyv5pSv5oyBOua1meaxn+iHu+WWhOenkeaKgOiCoeS7veaciemZkOWFrOWPuCZuYnNwOzxiciAvPg0K5aSH5qGI5Y+3OiDkuqxJQ1DlpIcwOTA3NDk5MuWPtyDkuqzlhaznvZHlronlpIcxMTAxMDIwMDA2NjYoMikmbmJzcDs8YnIgLz4NCjwvc3Bhbj4mbmJzcDsmbmJzcDsmbmJzcDs8YnIgLz4NCiZuYnNwOzwvc3Bhbj48L3A+HwEFZEJBQ0tHUk9VTkQtSU1BR0U6dXJsKGh0dHA6Ly93d3cubGFuZGNoaW5hLmNvbS9Vc2VyL2RlZmF1bHQvVXBsb2FkL3N5c0ZyYW1lSW1nL3hfdGRzY3cyMDEzX3l3XzEuanBnKTtkZE7708COJcrCEa3ChM4IYD0Oc18rkXhLzt32qZGyq8/r'}
            try:
                response = self.s.post(url, headers=self.headers, data=payload, cookies=self.cookies, timeout=8)
            except Exception as e:
                self.save_exception(e)
                continue
            if response.status_code == 200:
                try:
                    content = response.content.decode('gb2312', errors='ignore')
                except:
                    return None
                if 'YunSuoAutoJump()' in content:
                    self.refresh_cookies()
                    return self.get_list_page(tabid, datestring)
                soup = bs(content, 'lxml')
                # get tags
                itemTags = soup.find_all('tr', attrs={'class':'gridItem'})
                itemTags += soup.find_all('tr', attrs={'class':'gridAlternatingItem'})
                print('%s page %s find %s'%(datestring, pagenum, len(itemTags)))
                # if today has no more record, break loop
                if len(itemTags) == 0:
                    break
                # substract info and save into csv
                for tag in itemTags:
                    infos = self.substract_preview_from_itemTag(tag)
                    self.save(infos, '市场交易')
                    self.save_index(pagenum)
            else:
                print('request error, status code = {}'.format(response.status_code))


    def substract_preview_from_itemTag(self, tag):
        try:
            tds = tag.find_all('td')
            district_name = tds[1].text
            link = 'https://www.landchina.com/' + tds[2].a['href']
            location = tds[2].text
            total_size = tds[3].text
            usage = tds[4].text
            provide_method = tds[5].text
            date = tds[6].text
            infos = [district_name, link, location, total_size, usage, provide_method, date]
            return infos
        except Exception as e:
            self.save_exception(e)

    def save_exception(self, e:Exception):
        with open('./Exceptions.txt', 'a') as f:
            f.write(str(e))
            f.write('\n')

    def save_log_string(self, string:str):
        with open('./Exceptions.txt', 'a') as f:
            f.write(str(string))
            f.write('\n')


    def add_index(self, filename):
        index = 0
        with open(filename, 'r', encoding='gb2312', errors='ignore', newline='') as f:
            with open('./indexed_result.csv', 'a', encoding='gb2312', errors='ignore', newline='') as f1:
                reader = csv.reader(f)
                writer = csv.writer(f1)
                for row in reader:
                    row = [index] + row
                    writer.writerow(row)
                    index += 1
        print('finished indexing')



def start(tasklist):
    pass



if __name__ == '__main__':
    e = LandCrawler()
    e.start_listpage_task(264, 2000, 2005)
    # WORKER_NUM = 4
    # MAX_TASK_COUNT = 2000000
    # q = Queue()
    # p = Pool(4)
    #
    #
    # def start_multiprocess_detail_task():
    #     # load previews and urls
    #     with open('./indexed_result.csv', 'r', encoding='gb2312', errors='ignore') as f:
    #         count = 0
    #         reader = csv.reader(f)
    #         temp_task = []
    #         task_count = 0
    #         # start the write function first
    #         print('applied writer worker')
    #         for i in reader:
    #             temp_task.append(i)
    #             count += 1
    #             if count > MAX_TASK_COUNT:
    #                 count=0
    #                 p.apply_async(self.multi_detail_woker, args=(temp_task, useproxy))
    #                 task_count += 1
    #                 print('apply task %s'%task_count)
    #                 # release memory manually
    #                 del(temp_task)
    #                 gc.collect()
    #                 temp_task = []
    #         # assign the last task
    #         p.apply_async(self.multi_detail_woker, args=(temp_task, useproxy))
    #         print('assgin done')
    #         del(temp_task)
    #         gc.collect()
    #         p.close()
    #         p.join()
    #
    #
    #
    # exx = LandCrawler()
    # # exx.start_listpage_task(263, 2020, 2020)
    # # exx.start_result_detail_task()
    # # exx.add_index('./lanchina_market_result.csv')
    # exx.start_multiprocess_detail_task(useproxy=True)