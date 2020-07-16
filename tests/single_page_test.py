#encoding=utf8
import requests
from bs4 import BeautifulSoup as bs
import gzip

s = requests.Session()
headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br'
        }

def get_cookies(url):
    try:
        yunsuo_s = s.get(url, timeout=5, headers=headers).cookies.get(
            'security_session_verify')
        mid_resp = s.get('{}{}'.format(url, '&security_verify_data=313932302c31303830'),
                              headers=headers, timeout=5)
        mid = mid_resp.cookies.get('security_session_mid_verify')
        # check for captcha. ----------------->
        try:
            content = mid_resp.content.decode('utf-8', 'ignore')
        except Exception as e:
            print('error in 验证码 logic')
            print(str(e))
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


cookies = get_cookies('https://www.landchina.com/default.aspx?tabid=264&ComName=default')

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
'Accept-Language': 'zh-CN,zh;q=0.9',}
resp = s.get('https://www.landchina.com//DesktopModule/BizframeExtendMdl/workList/bulWorkView.aspx?wmguid=20aae8dc-4a0c-4af5-aedf-cc153eb6efdf&recorderguid=d9d83b5f-5d93-4a2c-be66-de30c12d3371&sitePath='
              , cookies=cookies,
             headers = headers)
content = resp.content
soup = bs(content, 'lxml')
content.decode('gbk')



