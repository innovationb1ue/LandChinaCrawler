# encoding:utf-8
import requests
import os
import base64

def get_token():
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    host = ''
    response = requests.get(host)
    if response:
        print(response.json()['access_token'])
        return response.json()['access_token']

def recog(catpchapath) ->str:
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
    # 二进制方式打开图片文件
    access_token = ''
    f = open('./captchas/{}'.format(catpchapath), 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        text = response.json()['words_result'][0]['words']
        print(text)
        return text
    else:
        return ''



if __name__ == '__main__':
    token = get_token()
    # recog()
