import re
lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')

def clean(s):
    s = re.sub('[(",)]','',s)
    s = s.replace("'","")
    return s
    
def increment(s):
    s = clean(s)
    m = lastNum.search(s)
    if m:
        next = str(int(m.group(1))+1)
        start, end = m.span(1)
        s = s[:max(end-len(next), start)] + next + s[end:]
    return s
