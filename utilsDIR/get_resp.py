import requests

def my_post(s:requests.Session, url, data, header, cookies=None, retryCount=0):
    if retryCount >= 5:
        return False
    resp = s.post(url, data=data, headers=header, cookies=cookies, timeout=10)
    if resp.status_code == 200:
        return resp
    else:
        return my_post(s, url, data, header, cookies, retryCount+1)
