from bs4 import BeautifulSoup as bs

def extract_landTrans(content:str):
    soup = bs(content, 'lxml')
    if (landlabel := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c2_ctrl'})):
        landlabel = landlabel.text.strip()
    if (code := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl'})):
        code = code.text.strip()
    if (location := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl'})):
        location = location.text.strip()
    if(govdistrct:= soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r11_c4_ctrl'})):
        govdistrct = govdistrct.text.strip()
    if (formerUser := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl'})):
        formerUser = formerUser.text.strip()
    if (nowUser := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl'})):
        nowUser = nowUser.text.strip()
    if (landsize := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r4_c2_ctrl'})):
        landsize = landsize.text.strip()
    if (usage := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r4_c4_ctrl'})):
        usage = usage.text.strip()
    if (rightclass := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r5_c2_ctrl'})):
        rightclass = rightclass.text.strip()
    if (timelimit := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r5_c4_ctrl'})):
        timelimit = timelimit.text.strip()
    if (curCondition := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r6_c2_ctrl'})):
        curCondition = curCondition.text.strip()
    if (landlevel := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r6_c4_ctrl'})):
        landlevel = landlevel.text.strip()
    if (trademethod := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r8_c2_ctrl'})):
        trademethod = trademethod.text.strip()
    if (price := soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r8_c4_ctrl'})):
        price = price.text.strip()
    if (dealtime :=soup.find('span', attrs={'id':'mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r7_c2_ctrl'})):
        dealtime = dealtime.text.strip()
    print(dealtime)
    return [landlabel, code, location, govdistrct, formerUser, nowUser, landsize, usage,
            rightclass, timelimit, curCondition, landlevel, trademethod, price, dealtime]


