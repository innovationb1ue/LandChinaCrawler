from bs4 import BeautifulSoup as bs



def extract_landMortgage(content:str):
    soup = bs(content, 'lxml')
    label = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c2_ctrl')
    code = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl')
    govdistrict = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r13_c2_ctrl')
    districtcode = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r13_c4_ctrl')
    loc = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl')
    size = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c4_ctrl')
    rightpeonum = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl')
    rightnum = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl')
    rightPersonName = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r4_c2_ctrl')
    MortClass = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r4_c4_ctrl')
    mortRightPerson = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r5_c2_ctrl')
    usage = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r5_c4_ctrl')
    mortType = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9_c2_ctrl')
    mortSize = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r9_c4_ctrl')
    evalPrice = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r8_c2_ctrl')
    mortPrice = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r8_c4_ctrl')
    startTime = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r11_c2_ctrl')
    endTime  = _find_text_by_id(soup, 'span', 'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r11_c4_ctrl')

    return [
        label,  # 宗地标识
        code,   # 宗地编号
        govdistrict,    # 所在行政区
        districtcode,   # 行政区code
        loc,    # 宗地座落
        size,   # 土地面积
        rightpeonum,# 土地他项权利人证号
        rightnum,   # 土地使用权证号
        rightPersonName, # 土地抵押人名称
        MortClass,  # 土地抵押人性质
        mortRightPerson,    # 土地抵押权人
        usage, # 抵押土地用途
        mortType,   # 抵押土地权属性质与使用权类型
        mortSize,   # 抵押面积(公顷)
        evalPrice,  # 评估金额(万元)
        mortPrice,  # 抵押金额(万元)
        startTime,  # 土地抵押登记起始时间
        endTime # 土地抵押登记结束时间
    ]









def _find_text_by_id(soup, tagname, id):
    t = None
    if (t := soup.find(tagname, attrs={'id': id})):
        t = t.text.strip()
    return t
