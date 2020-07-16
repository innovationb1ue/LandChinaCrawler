#encoding=utf-8
from fontTools.ttLib import TTFont
import os
import requests
from utilsDIR.Saves import save_exception
from utilsDIR.get_cookies import get_cookies

def get_font_dict(path:str):
    # path should be the path of file 'YQrFiPvT3SaifS4J3BLtxTgci0q3oe0B.woff'
    font1 = TTFont(path)
    # str list for YQxxx.woff
    strlist = '    津市法文顶' \
              '程讲音选要于赢乐农' \
              '对负狗委汉厉任藏哲' \
              '里认穿政水情体江扫' \
              '德习电做外活行转我' \
              '成浙所说园宣坚锋典' \
              '云博用注洁湾积挂十' \
              '想规洛密涯同吸军周' \
              '不人神建冀调大共弘' \
              '度地承精学企加高修' \
              '社失热据飞艺与性正' \
              '敌团息属头名更深土' \
              '书准臂作点多期强化' \
              '区黄料工员时近管迎' \
              '鞋临治恶会伦页赋荐' \
              '术如服府经胡阿渔六' \
              '集字络视见专践步业' \
              '明贸型首凰马决党计' \
              '财健巴质窗家史标载' \
              '收坛何公代协关事中' \
              '优牌海抱引勇西端困' \
              '淀舆下利录在生群斯' \
              '悬变责版上数梦年荣' \
              '告兵层参扎好末位招' \
              '有退源统红网魂克的' \
              '吾动丽传亲铁其省知' \
              '远制广毛量祠欢担面' \
              '具办新舟血七存九极' \
              '报沉请命东发善届客' \
              '盒排狐役波讯绿争皮' \
              '众裁膀日主遗聚展城' \
              '总天技论定产搜国复' \
              '系百宽理资境频除补' \
              '去疆浪绩设入持先厅' \
              '顿示指律李泽推单得' \
              '育信都态控移机民局' \
              '扬布闻黑平错山方南' \
              '进堡之印件来登无涉' \
              '第拥能列卫申通犯改' \
              '央聘幕权当廉站素范' \
              '凤康微思户腾续干简' \
              '欧北华为务软田光全' \
              '台常开脸款夫部革竞' \
              '线酷埃个听本义张'
    # Build FontDict
    FontDict = {}
    for key, word in zip(font1.getGlyphOrder()[1:], strlist[1:]):
        coor = font1['glyf'][key].coordinates
        FontDict[hash(str(coor))] = word.encode('unicode_escape')
    return FontDict


def decodeFont(raw:bytes, woffname:str, FontDict:dict)->str:
    """
    :param unicode: the unicode bytes waiting to be replace and decode
    :param woffname: the page woff name (xxxxx.woff)
    :return str: decoded string object

    """
    if not os.path.exists('./woff/%s' % woffname):
        _download_woff(woffname)
    try:
        font = TTFont(f'./woff/{woffname}')
    except Exception as e:
        return ''
    for unistr in font.getGlyphOrder()[1:]:
        coor = font['glyf'][unistr].coordinates
        coor_hash = hash(str(coor))
        correct_unistr = FontDict.get(coor_hash)
        unistr = unistr.lower()
        unistr = unistr.replace('uni', r'\u')
        unistr = unistr.encode('unicode_escape')[1:]
        raw = raw.replace(unistr, correct_unistr)
    try:
        return raw.decode('unicode_escape')
    except Exception as e:
        print('Exception in decode Font func, ', str(e))
        save_exception(e)


def _download_woff(woffname) ->None:
    s = requests.Session()
    cookies = get_cookies(s, 'https://www.landchina.com/default.aspx?tabid=264&ComName=default')
    try:
        resp = s.get(f'https://www.landchina.com/styles/fonts/{woffname}', timeout=3, cookies=cookies)
        if resp.status_code != 200:
            return
    except Exception as e:
        print('Donwload woff timeout!')
        save_exception(e)
        return
    with open(f'./woff/{woffname}', 'wb') as f:
        f.write(resp.content)


# 流程
# 获取网页->获取字体文件（使用缓存）-> 获取网页上文字对应的coordinates->通过FontDict替换乱码为正确unicode->完成
def test():
    FontDict = get_font_dict('./YQrFiPvT3SaifS4J3BLtxTgci0q3oe0B.woff')
    font2 = TTFont('./N2BQFizNQ7aV6gymJy75hcEXV7Bqqcah.woff')
    a = '舉僟舙自然朢喪橆ル瀋譒飜使蔠騏拍卖出让輕攋'
    a_uni = a.encode('unicode_escape')
    pre = a_uni
    for unistr in font2.getGlyphOrder()[1:]:
        # 获取页面的字体的coor
        coor = font2['glyf'][unistr].coordinates
        coor_hash = hash(str(coor))
        correct_unistr = FontDict.get(coor_hash)
        unistr = unistr.lower()
        unistr = unistr.replace('uni', r'\u')
        unistr = unistr.encode('unicode_escape')[1:]
        print(unistr, '->', correct_unistr)
        a_uni = a_uni.replace(unistr, correct_unistr)
    print('Before decode : ', pre)
    print('After decode : ', a_uni)
    print(pre.decode('unicode_escape'))
    print(a_uni.decode('unicode_escape'))


if __name__ == '__main__':
    test()
