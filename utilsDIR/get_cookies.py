import requests

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
        }


def get_cookies(s: requests.Session, url: str) -> dict:
    if not s:
        s = requests.Session()
    try:
        yunsuo_s = s.get(url, timeout=5, headers=headers).cookies.get(
            'security_session_verify')
        mid_resp = s.get('{}{}'.format(url, '&security_verify_data=313932302c31303830'),
                              headers=headers, timeout=5)
        mid = mid_resp.cookies.get('security_session_mid_verify')
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