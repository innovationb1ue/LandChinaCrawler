from woff.process_woff import decodeFont
import re
import time

def extract_Notice(content:bytes, FontDict:dict) -> str:
    raw = content.decode('gbk')
    unistr = raw.encode('unicode_escape')
    if woffnameslist := re.findall('fonts/(.*?).woff', raw):
        woffname = woffnameslist[0]+'.woff'
    else:
        print('Not found woff name!')
        return ''
    normalcontent = decodeFont(unistr, woffname, FontDict)
    return normalcontent


