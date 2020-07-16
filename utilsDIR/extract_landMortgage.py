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
        label,  # �ڵر�ʶ
        code,   # �ڵر��
        govdistrict,    # ����������
        districtcode,   # ������code
        loc,    # �ڵ�����
        size,   # �������
        rightpeonum,# ��������Ȩ����֤��
        rightnum,   # ����ʹ��Ȩ֤��
        rightPersonName, # ���ص�Ѻ������
        MortClass,  # ���ص�Ѻ������
        mortRightPerson,    # ���ص�ѺȨ��
        usage, # ��Ѻ������;
        mortType,   # ��Ѻ����Ȩ��������ʹ��Ȩ����
        mortSize,   # ��Ѻ���(����)
        evalPrice,  # �������(��Ԫ)
        mortPrice,  # ��Ѻ���(��Ԫ)
        startTime,  # ���ص�Ѻ�Ǽ���ʼʱ��
        endTime # ���ص�Ѻ�Ǽǽ���ʱ��
    ]









def _find_text_by_id(soup, tagname, id):
    t = None
    if (t := soup.find(tagname, attrs={'id': id})):
        t = t.text.strip()
    return t
