from bs4 import BeautifulSoup as bs

def extract_landLending(content:str):
    soup = bs(content, 'lxml')
    # ×ÚµØ×ùÊ¶
    landlabel = _find_text_by_id(soup, 'span','mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r8_c2_ctrl')
    # ±àºÅ
    code = _find_text_by_id(soup, 'span','mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r8_c4_ctrl')
    location = _find_text_by_id(soup, 'span','mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r3_c2_ctrl')
    govdistrict = _find_text_by_id(soup, 'span','mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r10_c2_ctrl')
    discode = _find_text_by_id(soup, 'span','mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r10_c4_ctrl')
    rightnum = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r4_c2_ctrl')
    square = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r4_c6_ctrl')
    usage = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r1_c2_ctrl')
    level = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r1_c6_ctrl')
    usecondition = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r5_c2_ctrl')
    timeperiod = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r5_c6_ctrl')
    limit = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r6_c2_ctrl')
    signdate = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r6_c6_ctrl')
    rent = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f11_r7_c2_ctrl')
    return [landlabel,
                code,
                location,
                govdistrict,
                discode,
                rightnum,
                square,
                usage,
                level,
                usecondition,
                timeperiod,
                limit,
                signdate,
                rent
            ]


def _find_text_by_id(soup, tagname, id):
    t = None
    if (t := soup.find(tagname, attrs={'id': id})):
        t = t.text.strip()
    return t



