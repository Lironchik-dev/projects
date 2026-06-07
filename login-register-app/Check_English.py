def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

assert not isEnglish('slabiky, ale liší se podle významu')
assert isEnglish('English')
assert not isEnglish('ގެ ފުރަތަމަ ދެ އަކުރު ކަ')
assert not isEnglish('how about this one : 通 asfަ')
assert isEnglish('?fd4))45s&')
