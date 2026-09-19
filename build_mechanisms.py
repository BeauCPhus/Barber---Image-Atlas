from bs4 import BeautifulSoup
from pathlib import Path
import json,re,sys
src=Path(sys.argv[1] if len(sys.argv)>1 else 'pg58391-images.html')
out=Path(sys.argv[2] if len(sys.argv)>2 else 'mechanisms.json')
soup=BeautifulSoup(src.read_bytes(),'html.parser')
plates={}
seen=set()
for a in soup.find_all('a', href=True):
    m=re.fullmatch(r'#Plate0*(\d+)',a['href'],re.I)
    if not m: continue
    plate=int(m.group(1))
    if not 1<=plate<=156: continue
    parent=a.find_parent('p') or a.parent
    text=' '.join(parent.stripped_strings)
    # Only numbered Barber description paragraphs.
    lead=re.match(r'\s*(\d+)(?:\s*(?:to|&)\s*(\d+))?', text, re.I)
    if not lead: continue
    key=(plate,text)
    if key in seen: continue
    seen.add(key)
    nums=[]
    for z in parent.find_all('a',href=True):
        if z['href'].lower()==a['href'].lower(): nums += [int(x) for x in re.findall(r'\d+',z.get_text(' ',strip=True))]
    nums=list(dict.fromkeys(nums))
    lo=int(lead.group(1)); hi=int(lead.group(2)) if lead.group(2) else None
    # Expand explicit Barber ranges such as 535 to 545 / 1048 to 1053.
    if hi is not None and 0 <= hi-lo <= 100:
        nums=list(range(lo,hi+1))
    elif lo not in nums:
        nums.insert(0,lo)
    plates.setdefault(str(plate),[]).append({'numbers':nums,'text':text})
meta={'source':'The Engineer’s Sketch-Book, Thomas Walter Barber, 4th ed. (1902); Project Gutenberg eBook #58391 HTML edition','plate_count':156,'description_blocks':sum(map(len,plates.values())),'plates':plates}
out.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
allnums={n for arr in plates.values() for r in arr for n in r['numbers']}
print(f'Wrote {meta["description_blocks"]} description blocks across {len(plates)} plates; indexed {len(allnums)} mechanism numbers.')
print('Unindexed numbers:', [i for i in range(1,2604) if i not in allnums])
