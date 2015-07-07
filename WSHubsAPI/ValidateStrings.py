# coding=utf-8
import re

__author__ = 'Jorge'

def isNumeric(string):
    try:
        float(string)
        return True
    except:
        return False

def isInt(string):
    try:
        int(string)
        return True
    except:
        return False

def isFloat(string):
    return isNumeric(string)

emailValidator = re.compile(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$")

def isEmail(string):
    return emailValidator.match(string) is not None

phoneValidator = re.compile(r"^(00|\+)\d{7,15}$")

def isInternationalPhone(string):
    return phoneValidator.match(string) is not None

urlValidator= re.compile(r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")
"""from http://daringfireball.net/2010/07/improved_regex_for_matching_urls"""

def isURL(string):
    return urlValidator.match(string) is not None

#street names


ipValidator=re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){0,3}$")

def isIP(string):
    return ipValidator.match(string) is not None

TEXT_ENCODE='utf-8'
def getUnicode(s):
    if isinstance(s,str):
        try:
            return s.decode(TEXT_ENCODE)
        except:
            return s.decode('latin-1','replace')
    elif isinstance(s,unicode):
        try:
            return s.encode(TEXT_ENCODE).decode(TEXT_ENCODE)
        except:
                return s.encode('latin-1','replace').decode('latin-1','replace')
    else:
        return getUnicode(unicode(s))

def getStr(s):
    if isinstance(s,unicode):
        return s.encode(TEXT_ENCODE,'replace')
    elif isinstance(s,str):
        return s.decode(TEXT_ENCODE,'replace').encode(TEXT_ENCODE,'replace')
    else:
        return getStr(str(s))