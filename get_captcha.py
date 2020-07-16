# coding=gbk
import requests
import re
import base64
import uuid
from bs4 import BeautifulSoup as bs

def decode_image(src):
    # 1����Ϣ��ȡ
    result = re.search("data:image/(?P<ext>.*?);base64,(?P<data>.*)", src, re.DOTALL)
    if result:
        ext = result.groupdict().get("ext")
        data = result.groupdict().get("data")

    else:
        raise Exception("Do not parse!")

    # 2��base64����
    img = base64.urlsafe_b64decode(data)

    # 3���������ļ�����
    filename = "./captchas/{}.{}".format(uuid.uuid4(), ext)
    with open(filename, "wb") as f:
        f.write(img)
    return filename


s = requests.Session()
resp = s.get('https://www.landchina.com/default.aspx?tabid=330&ComName=default')
while True:
    if '��֤�벻��Ϊ��' in resp.content.decode('utf-8'):
        content = resp.content.decode('utf-8')
        soup = bs(content, 'lxml')
        imgTag = soup.find('img', attrs={'alt': 'verify_img'})
        imgdata = imgTag['src']
        decode_image(imgdata)
        print('get one')