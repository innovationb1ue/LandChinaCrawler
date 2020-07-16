import pandas as pd
from bs4 import BeautifulSoup as bs
from bs4 import BeautifulSoup
import re
from lxml import etree

data = pd.read_csv('./出让公告-detail.csv', chunksize=10,
                   encoding='gb2312', iterator=True,
                   index_col=0)

test = data.get_chunk()

content = test.iloc[2]['html']
soup = bs(content, 'lxml')

html = etree.HTML(content)

def extract_churang_land_info_from_html(html_obj):
    target_cols = [
        u'宗地编号',
        u'宗地总面积',
        u'宗地坐落',
        u'出让年限',
        u'容积率',
        u'建筑密度',
        u'绿化率',
        u'建筑限高',
        u'土地用途明细',
        u'投资强度',
        u'保证金',
        u'估价报告备案号',
        u'起始价',
        u'加价幅度',
        u'挂牌开始时间',
        u'挂牌截止时间',
        # u'备注',
        u'现状土地条件',
    ]

    soup = BeautifulSoup(html_obj, 'html.parser')

    all_text = soup.get_text()
    deadline_match = re.search(r'交纳竞买保证金的截止时间为(\d+年\d+月\d+日\d+时\d+分)', all_text)
    if deadline_match:
        deadline_str = deadline_match.group(1)
    else:
        deadline_str = ''

    ret_table = []
    for tab in soup.find_all('table'):
        tab_border = tab.get('border', None)
        if tab_border != '1':
            continue

        kv_arr = []
        for tr_obj in tab.find_all('tr'):
            for td_obj in tr_obj.find_all('td'):
                val = td_obj.text.strip().replace('\n', '')
                kv_arr.append(val)

        print(kv_arr)
        ret = []
        for col in target_cols:
            found_flag = False
            for idx, val in enumerate(kv_arr):
                if val.find(col) == 0:
                    found_flag = True
                    if col == u'现状土地条件':
                        ret.append((val[:6], val[6:]))
                    else:
                        ret.append((col, kv_arr[idx + 1]))
                    break

            if not found_flag:
                ret.append((col, ''))

        ret.append((u'交纳竞买保证金的截止时间', deadline_str))
        ret_table.append(ret)
    return ret_table
