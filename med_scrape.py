#!/usr/bin/env python
# -*- coding: utf-8 -*-

##  Copyright 2024 Yingjie Lan
##
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


######################################
 #### BEGIN( WEB SCRAPING CODE ) ####
######################################
from bs4 import BeautifulSoup
import requests, time, re

# extract data from this url:
# f'http://www.a-hospital.com/w/{med}'
# two possible formats: table or paragraph,
# depending on the source of data.

# Another good website is baike.baidu.com 
# https://baike.baidu.com/item/褚实子

DBG_EXTRACT = False

IMG_BASE = 'http://p.ayxbk.com/images/thumb/'
def extract(med, cache_only=False):
    if med not in CACHE:
        if cache_only: return #Nothing to do
        url = f'http://www.a-hospital.com/w/{med}'
        for i in range(3):
            try: res = requests.get(url)
            except requests.exceptions.Timeout:
                time.sleep(20)
                continue #retry
            if res.status_code == 200: break
            return # all other status_code, such as
                   # 404: title is "页面没找到！"
        else: return # after failing 3 times
        CACHE[med] = res.text #CACHE pages
    soup = BeautifulSoup(CACHE[med], 'html.parser')
    title = soup.find(id='firstHeading')
    if not title:
        print(f"\n {med}: 没有发现firstHeading!")
        return
    title = title.text
    if title != med: # wrong page
        print(f"\n   查找“{med}”却得到“{title}”！")
        # 仍然收集信息，但以后可以发现该错误
    feat = { "class" : "infobox hproduct" }
    table = soup.find("table", feat)
    if table:
        res = table_extract(table, title)
        res['性味'] = f"{res['药味']}::{res['药性']}"
        del res['药味'], res['药性']
        # del res['毒性'], res['始载于']
        res['paradata'] = para_extract(soup, title)
    else: res = para_extract(soup, title)

    if res.get('图片','').startswith(IMG_BASE):
        res['图片'] = res['图片'][len(IMG_BASE):]

    return res


# extract from paragraphs:
#
# 两个例子，一个用[]，一个用【】
#
# http://www.a-hospital.com/w/川朴
#
# [处 方 名] 厚朴，川朴，姜厚朴，制川朴。
# [来 源] 为木兰科植物厚朴Magnolia of-ficinalis Rehd.et Wils或凹叶厚朴M.biloba（Rehd.et.wils.）Cheng的树皮或根皮。
# [性 味] 苦、辛，温。
# [功 效] 宽中理气，化湿开郁。
# [成 分] 含挥发油、厚朴酚、四氢厚朴酚、异厚朴酚、木兰箭毒碱等。　
#
# http://www.a-hospital.com/w/羊踯躅
#
#【异名】山芝麻根(《梁侯瀛集验良方》)，巴山虎(《百草镜》)，闹羊花根(《纲目拾遗》)。
#【来源】为杜鹃花科植物羊踯躅的根，植物形态详闹羊花条。
#【性味】《中医药实验研究》：有毒。
#【归经】《本草新编》：入脾经。
#【功用主治-羊踯躅根的功效】驱风，除湿，消肿，止痛。治风寒湿痹，跌打损伤，痔漏，癣疮。《纲目拾遗》：追风，定痛。

##http://www.a-hospital.com/w/半边莲
##
##【中药名】半边莲 banbianlian
##【别名】细米草、半边花、急解索、半边菊、金菊草。
##【英文名】Herba Lobeliae Chinensis。
##【来源】桔梗科植物半边莲Lobelia chinensis Lour.的全草。
##【植物形态】多年生矮小草本，高5~15厘米。全株光滑无毛，有乳汁。根细圆柱形，淡黄白色。茎细弱匍匐，上部直立。叶互生，无柄;叶片条形或条状披针形，全缘或有疏齿。叶腋开单生淡紫色或白色小花;花冠基部合成管状，上部向一边5裂展开，中央3裂片较浅，两侧裂片深裂至基部;雄蕊5，花丝基部分离，花药彼此连合，围抱柱头，花药位于下方的两个有毛，上方的3个无毛;子房下位。蒴果顶端2瓣开裂;种子细小，多数。花期5~8月，果期8~10月。
##【产地分布】生于水田边、路沟旁、潮湿的阴坡、荒地。分布于江苏、浙江、安徽等地。
##【采收加工】夏、秋季生长茂盛时采收，洗净晒干。生用或鲜用。
##【药材性状】全长15~35厘米，但常缠成团。根茎细长圆柱形，直径1~2毫米，表面淡黄色或黄棕色，多有细纵根。根细小，侧生细纤须根。茎细长，有分枝，灰绿色，节明显，有的可见附生的细根。叶互生，无柄，绿色，呈狭披针形或长卵圆形，长1~2厘米，宽2~5毫米，叶缘有疏锯齿。花梗细长，花小，单生于叶腋，花冠筒内有白色茸毛。花萼5裂，裂片绿色线形。气微，味微甘而辛。
##【性味归经】性平，味辛。归心经、小肠经、肺经。
##【功效与作用】利尿消肿、清热解毒。属清热药下属分类的清热解毒药。主治：小便不利，面目浮肿；蛇虫咬伤；胃癌肠癌、食管癌、肝癌及其并发腹水等病症。

EXCLUDED_KEYS = '1234567891011①②③④⑤⑥⑦⑧⑨⑩一二三四五六七八九十'
OpenClose = '[]【】［］〖〗'

def compile_key_pattern():
    pata = r'(?m)[【［〖[]([- 、\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]+)[]】］〗]'
    patb = r'^([\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF]+)[：:]'
    return re.compile( f'{pata}|{patb}')

KEYPAT  = compile_key_pattern()

def yieldKVs(text):
    key = "" # no key yet
    while True:
        find = KEYPAT.search(text)
        if not find:
            if key: yield key, text
            elif DBG_EXTRACT:
                print(">> 没发现关键词:", text, file=sys.stderr)
            break
        i,j = find.span()
        if key: yield key, text[:i]
        elif i and DBG_EXTRACT:
            print(">> 起始处无关键词:", text[:i], file=sys.stderr)
        text = text[j:]
        key = find.group(1) or find.group(2) # new key
        key = re.sub(r'[ ，、]', "", key)
        key = key.replace("性位", '性味') #e.g. 元参

def parseKVs(text, entries):
    for kwd, fext in yieldKVs(text):
        # empty kwd included
        if kwd in EXCLUDED_KEYS:
            if kwd or fext:
                if DBG_EXTRACT:
                    print("Excluded: Key=", kwd, "Value=",
                          fext, file=sys.stderr)
            continue
        if not fext or len(kwd) > 9:
            if DBG_EXTRACT:
                print("Bad key or value: Key=", kwd,
                      "Value=", fext, file=sys.stderr)
            continue
        if '\n' in fext: fext = fext.replace('\n', ' ')
        append_add(entries, kwd, fext)

def getKVpair(text):
    find = OpenClose.find(text[0])
    if find % 2: # find = -1 included
        find = text.find('【')
        if find < 0: find = len(text)
        if DBG_EXTRACT:
            print("无关键词起始标志:",
                  text[:find], file=sys.stderr)
        return "", "", text[find:]
    cind = text.find(OpenClose[find+1])
    if cind < 0: # didn't close!
        if DBG_EXTRACT:
            print("无关键词结束标志:", text,
                  file=sys.stderr)
        return "", "", ""
    kwd = text[1:cind] #text starts with key
    find = kwd.find('-') #special split
    if find > 0: kwd=kwd[:find]
    kwd = re.sub(r'[ ，、]', "", kwd)
    kwd = kwd.replace("性位", '性味') #e.g. 元参

    text = text[cind+1:]
    find = text.find('【') # other fields?
    fext = text if find < 0 else text[:find]
    text = "" if find<0 else text[find:]
    return kwd, fext, text

def append_add(dd, kk, vv):
    if kk in dd: dd[kk] = f"{dd[kk]};;{vv}"
    else: dd[kk] = vv

def parseKVpairs(text, entries):
    while text:
        kwd, fext, text = getKVpair(text)
        # empty kwd included
        if kwd in EXCLUDED_KEYS:
            if kwd or fext:
                if DBG_EXTRACT:
                    print("Excluded: Key=", kwd, "Value=",
                          fext, file=sys.stderr)
            continue
        #raise Exception(f"错误关键词:{kwd}")
        if not fext or len(kwd) > 9:
            if DBG_EXTRACT:
                print("Bad key or value: Key=", kwd,
                      "Value=", fext, file=sys.stderr)
            continue
        append_add(entries, kwd, fext)

def unipara_enum(soup):
    just_key = "" #make special case for just a key
    for par in soup.find_all("p"):
        text = par.text
        find = KEYPAT.search(text)
        if find:
            i,j = find.span()
            if j == len(text):
                just_key = text
            else:
                yield text
                just_key = ""
        elif just_key:
            yield just_key + text
            just_key = ""

def multipara_enum(soup):
    lines = []
    for par in soup.find_all("p"):
        text = par.text# empty text -> end of content
        #print(">>> DUMP:", text, file=sys.stderr)
        find = KEYPAT.match(text)
        if find: # end of current field
            merged = "\n".join(lines)
            lines = [text]
            yield merged
        else: lines.append(text) # extra field text
        par = par.find_next_sibling()
        if not par or par.name != 'p': # end of field
            merged, lines = "\n".join(lines), []
            yield merged

# TEXT_ENUMER = multipara_enum
TEXT_ENUMER = unipara_enum
def para_extract(soup, title):
    entries = {'from':'A+医学百科'}
    for text in TEXT_ENUMER(soup):
        parseKVs(text, entries)

    if '药材名' not in entries:
        entries['药材名'] = title
    elif ';;' in entries['药材名']:
        text = entries['药材名']
        find = text.find(';;')
        if len(set(text.split(';;')))>1:
            print("Many names:", text, file=sys.stderr)
        entries['药材名'] = text[:find]
    if entries['药材名'] != title:
        entries['title'] = title
    if not entries['药材名']: #empty name
        entries['药材名'] = title
        
    return entries
    

# http://www.a-hospital.com/w/厚朴
# this page contains a table that shows:
##厚朴
##Hòu Pò
##[a small image here]
##别名	川朴、紫油厚朴、厚皮、重皮、赤朴、烈朴
##功效作用	燥湿消痰，下气除满。用于湿滞伤中，脘痞吐泻，食积气滞，腹胀便秘，痰饮喘咳。
##英文名	CORTEX MAGNOLIAE OFFICINALIS
##始载于	《神农本草经》
##毒性	无毒
##归经	胃经、脾经、大肠经
##药性	温
##药味	辛、苦
def table_extract(table, title):
    entries = {'from':'中药图典'}
    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        th = row.find('th')
        if not i:
            name = th.text
            pinyin = name.find('\n')
            entries['药材拼音'] = name[pinyin+1:]
            hanzi  = name[:pinyin]
            entries['药材名'] = hanzi
            if hanzi != title: 
                #print(f"\n  表格药名：{title} <=> {hanzi}")
                entries['title'] = title
            continue
        td = row.find('td')
        # posssibly an image
        img = td.find('img')
        if img:
            entries['图片'] = img['src']
            continue
        if td and th: # may get empty fields
            entries[th.text] = td.text
    return entries

def merged_items(da, db):
    seen = set()
    for kk, vv in da.items():
        if kk in db:
            seen.add(kk)
            if vv == db[kk]: yield kk, vv
            else: yield kk, f'{vv};;{db[kk]}'
        else: yield kk, vv
    for kk, vv in db.items():
        if kk in seen: continue
        yield kk, vv

def alias_enum(dd, seen = None):
    # "学名" 有很多是英文
    for key in ('别名', "处方名", "异名", "又名", "名称", "学名"):
        if key not in dd: continue
        pid = dd[key].find('。')
        text = dd[key] if pid<0 else dd[key][:pid]
        for ali in re.sub(
r'\([^)]+\)|\[[^[]+\]|（[^）]+）|《[^》]+》|［[^［]+］|[a-zA-Z0-9();.,:：、，．（）]',
                     ' ', text).split():
            if ali in ("别名", "又名"):
                continue
            if seen is None: yield ali
            elif ali not in seen:
                seen.add(ali)
                yield ali                

def merged_alias_enum(dd, unique=True):
    seen = set() if unique else None
    yield from alias_enum(dd, seen)
    dd = dd.get('paradata')
    if dd: yield from alias_enum(dd, seen)


def printData(medict, fout):
    cols = ['药材名', '别名', '性味', '归经', '功效作用', '英文名']
    #kwds = {'别名': ["处方名","异名"], "功效作用": ["功效","通用","功效与作用"],}
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)
    for med, dat in medict.items():
        clean = {} # clean data for a table row
        if len(dat) < 3: continue
        if 'title' in dat: continue
        for kk,vv in merged_items(dat, dat['paradata']
                  ) if 'paradata' in dat else dat.items():
            if kk in cols:
                clean[kk] = vv
            elif kk in ('性味归经', '性味与归经'):
                for vs in vv.split(';;'):
                    pi = vs.find('。')
                    append_add(clean, '性味', vs[:pi+1])
                    append_add(clean, '归经', vs[pi+1:])
            elif kk in ("功效","通用","功效与作用","功能与主治"):
                append_add(clean, "功效作用", vv)

        for c, v in clean.items():
            if '\n' in v: clean[c] = v.replace('\n',' ')

        clean['别名'] = '，'.join(m for m in merged_alias_enum(dat)
                               if m!=clean['药材名'])

        if clean['药材名'] != med: clean['药材名'] += f'/{med}'

        print(f"| {' | '.join(clean.get(c,'-') for c in cols)} |", file=fout)

def save_web(medict, file):
    with open(f"{file}.py", "wt", encoding="utf-8") as fout:
        print("medict =", medict, file=fout)
    with open(f"{file}.md", 'wt', encoding="utf-8") as fout:
        printData(medict, fout)
    print(f'\n Saved to files: "{file}.py" and "{file}.md"')


def scrape_and_save(file, cache_only = False, nline=12):
    global CACHE, medict
    try: from pagecache import CACHE
    except: CACHE = {}
    cache_size = prev_len = len(CACHE)

    from 太医黑名单 import RAW_CAT_DATA, ALT_NAME_SEP

    for cat, clist in RAW_CAT_DATA.items():
        for meds in clist:
            for med in meds.split(ALT_NAME_SEP):
                if med in medict: continue
                # don't overwhelm the website
                if med not in CACHE and not cache_only:
                    time.sleep(3)
                ens = extract(med, cache_only)
                if ens: medict[med] = ens
                # IDLE在显示很长一行文字的时候很费时，可长达好几分钟
                print(med, '+' if ens else "-", end='、'
                      if len(medict)%nline else '、\n')
            if len(CACHE) > prev_len + 200:
                save_web(medict, file)
                prev_len = len(CACHE)

    fix_weird_values(medict)
    save_web(medict, file)

    if cache_size < len(CACHE):
        with open(PAGECACHE_FILE, 'wt', encoding="utf-8") as fout:
            print("CACHE =", CACHE, file=fout)

def check_and_save():
    global medict

    with open('checkdups.md', 'wt', encoding='utf-8') as fout:
        check_duplications(medict, fout)

    with open('datacheck.md', 'wt', encoding='utf-8') as fout:
        check_title(medict, fout=fout)
        check_weird_values(medict, fout)


        
### TODO: check consistency of the med base
    # 别名是否有重复？
    # 性味是否和毒性重复？


import sys
def check_title(medict, fout = sys.stderr):
    print("### 标题与数据对应的药名不同\n", file=fout)
    cols = ['请求药材', '页面标题', '数据标题']
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)
    for med, dat in medict.items():
        if 'title' in dat: 
            print(f"| {med} | Title:{dat['title']} | Data:{dat['药材名']} |", file=fout)
        if 'paradata' not in dat: continue
        if 'title' in dat['paradata']:
            print(f"| +{med} | Title:{dat['paradata']['title']} | Para:{dat['paradata']['药材名']} |", file=fout)
        if dat['药材名'] != dat['paradata']['药材名']:
            print(f"| #{med} | Table:{dat['药材名']} | Para:{dat['paradata']['药材名']} |", file=fout)


def check_weird_values(medict, fout = sys.stderr):
    print("\n### 带有其它内容的数据\n", file=fout)
    cols = ["数据位置", "数据"]
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)

    def check_dict(kk, dd):
        for ff, vv in dd.items():
            if ff == 'paradata':
                check_dict(f'{kk}+', vv)
            elif re.search(r'[【】]', vv):
                if "\n" in vv: vv = vv.replace("\n","")
                print(f'| /{kk}/{ff} | {vv} |', file=fout)
            elif re.search(r'<[^>]+>', vv):
                print(f'| /{kk}/{ff} | {vv} |', file=fout)
                
    for kk, dd in medict.items():
        check_dict(kk, dd)

def fix_weird_values(medict):
    # this comes from the output of check_weird_values
    # NOTE: all fields belong to 'paradata' dict
    weird_values = {'马蹄蕨':'别名',
                   '雀梅藤':'科属分类',
                   '骆驼肉':'骆驼肉营养成分',
                   '糯米':'科属分类',
                   '野荔枝':'资源分布',
                   '柳穿鱼':'功用' ,
                    }
    def extra_field(dd, ff, nfn):
        vv = dd[ff]
        find = vv.find(f"{nfn}】")
        if find < 0: return
        text = f"【{ff}】{vv[:find]}【{vv[find:]}"
        del dd[ff]
        print(f"{nfn}：{dd.get(nfn)}")
        parseKVpairs(text, dd)
        print(f"{nfn}：{dd.get(nfn)}")

    for med, ff in weird_values.items():
        dd = medict[med]['paradata']
        print("Before:", ff, dd[ff])
        if med == '马蹄蕨':
            extra_field(dd, ff, "异名")
        elif med == '野荔枝':
            extra_field(dd, ff, "动植物形态")
        elif med == '柳穿鱼':
            extra_field(dd, ff, "功用主治")
        elif med in ('雀梅藤','糯米'):
            dd[ff] = dd[ff][:-1]
        elif med == '骆驼肉':
            dd[ff] = dd[ff].replace("】、维生素B：","")
        #elif '<' in dd[ff] or '>' in dd[ff]: ## tags
        #    dd[ff] = re.sub(r'<[^>]*>','', dd[ff]) 
        print("After:", ff, dd[ff])

    def fix_dict(dd):
        for ff, vv in dd.items():
            if ff == 'paradata':
                fix_dict(vv)
            elif vv and vv[0] in "：:":
                dd[ff] = vv[1:]
                
    for kk, dd in medict.items():
        fix_dict(dd)
    
def check_duplications(medict, fout):
    print("### 错误的重定向列表\n", file=fout)
    cols = ['请求药名','得到药名', '别名清单']
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)

    badred = 0 # counter for bad redirections
    medseen, aliseen = {}, {}
    for kk, dd in medict.items():
        med = dd['药材名']
        if med in medseen: medseen[med].append(kk)
        else: medseen[med]=[kk]
        rba = 0 if kk==med else 1 # redirection?
        for ali in merged_alias_enum(dd):
            if rba and ali == kk:
                rba = 2 # redirection by alias
            if ali == med: continue #not an alias
            if ali in aliseen:
                if med not in aliseen[ali]: 
                    aliseen[ali].append(med)
            else: aliseen[ali] = [med]
        if rba == 1:
            print(f"| {kk} | {med} | {'，'.join(ali for ali in merged_alias_enum(dd))} |",
                  file=fout)
            badred += 1
                
    print(f"\n无理的重定向的总次数：{badred}。", file=fout)    
    print(f"别名数: {len(aliseen)}，药材数 {len(medseen)}，请求数{len(medict)}",
          file = fout)


    print("\n### 重复的药材别名列表\n", file=fout)
    cols = ['药材别名','可能的药材']
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)

    count, tot = 0, 0
    for ali, ml in aliseen.items():
        if len(ml)<2: continue
        print(f"| {ali} | {'，'.join(ml)} |", file=fout)
        tot += len(ml) 
        count += 1
    print(f"\n重复的别名数:{count}，总重复次数:{tot}，平均次数：{tot/count:.2f}",
          file=fout)

    print("\n###因为重定向而被多次访问的药名\n", file=fout)
    cols = ['药材名', '实际请求的药材']
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)

    count, tot = 0, 0
    for med, kl in medseen.items():
        if len(kl)<2:
            continue #no repeated visit
        count += 1
        tot  += len(kl)
        print(f"| {med} | {'，'.join(kl)} |", file=fout)
    print(f"\n重复访问的药材数:{count}，总重复次数:{tot}，平均次数：{tot/count:.2f}",
          file=fout)


def count_alias_repeats(cali):
    count = 0
    for kk, dd in medict.items():
        for ali in merged_alias_enum(dd):
            if ali == cali: count += 1
    return count

## 归经属性
MERIDIANS = ["心", "肝", "脾", "肺", "肾", "心包", 
"小肠", "胆", "胃", "大肠", "膀胱", "三焦", "大小肠"]
def getMeridian(dd):
   text = dd.get( '归经', '')
   if 'paradata' in dd:
       text += dd['paradata'].get( '归经', '')
   res = 0
   print(dd['药材名'], end="：")
   for i, mm in enumerate(MERIDIANS):
       if mm in text: 
           res |= 1<<i
           print(mm, end="，")
   print()
   return res

## 药性与药味
FLAVORS_ATTRS = "甘苦辛酸咸涩淡寒凉平温热"
def getFlavorAttr(dd):

    def get(kk, vv):
        nonlocal res
        for ff in  ["性味", "药味", "药性"]:
           if ff not in kk: continue
           for i, mm in enumerate(FLAVORS_ATTRS):
               if res & (1<<i): continue
               if mm in vv:
                   res |= 1<<i
                   print(mm, end="，")
               if res & (1<<i):
                   print("::", vv)

    print(dd['药材名'], end="：")
    res = 0

    for kk, vv in dd.items():
       get(kk, vv)

    if 'paradata' not in dd:
       return res

    for kk, vv in dd['paradata'].items():
       get(kk, vv)

    print()
    return res


## This code is used only if field value text 
#  contain other fields and values like 【归经】肝经。
def post_fix_all(file='medfix'):
    from medict import medict # previously scraped
    for kk, dd in medict.items(): 
        post_fix_one(dd)
    fix_weird_values(medict)
    save_web(medict, file)

def post_fix_one(dd):
    for ff, vv in dd.copy().items():
        if ff == 'paradata': 
            post_fix(dd['paradata'])
        elif ff in EXCLUDED_KEYS:
            print(ff, dd[ff], file=sys.stderr)
            del dd[ff]
        elif not vv:
            print(f"Empty field: {ff}", file=sys.stderr)
            del dd[ff]
        else:
            del dd[ff]
            parseKVpairs(f"【{ff}】{vv}", dd)

def print_med(med, dat):
    if not dat:
        print (med, ":: Not Found!", )
        return True
    print(f"==>> Extracted fields for {med}:")
    for ff, vv in dat.items():
        if ff!='paradata':
            print(f"【{ff}】{vv}")
            continue
        for ff, vv in vv.items():
            print(f">>【{ff}】{vv}")


## This part relates to poison data scraping

def extract_poisons(file = 'poisinf.py'):
    global POISON_CACHE
    try: from poison_pages import POISON_CACHE
    except: POISON_CACHE = {}
    cache_size = len(POISON_CACHE)
    psnd = {} #poison dict

    for i in range(6):
        extract_poison_page(i, psnd)
        time.sleep(5)

    if cache_size < len(POISON_CACHE):
        with open('poison_pages.py', 'wt', encoding='utf-8') as fout:
            print('POISON_CACHE =', POISON_CACHE, file=fout)
            
    with open(file, 'wt', encoding='utf-8') as fout:
        print('poisinf =', psnd, file=fout)
    return psnd

def extract_poison_page(i, psnd):
    base = 'http://www.a-hospital.com/w/有毒中药列表'
    url = f'{base}/{i+1}' if i else base
    if url not in POISON_CACHE:
        for i in range(3):
            try: res = requests.get(url)
            except requests.exceptions.Timeout:
                time.sleep(20)
                continue #retry
            if res.status_code == 200: break
            return # all other status_code
        else: return # after failing 3 times
        POISON_CACHE[url] = res.text #CACHE pages
    soup = BeautifulSoup(POISON_CACHE[url], 'html.parser')
    for ti, tab in enumerate(soup.find_all("table")):
        if not ti: continue
        rows = [r for r in tab.find_all('tr')]
        text = rows[0].text.strip() #need strip!!
        if text.startswith("有毒中药列表一共有6页"):
            break # end of poison list on this page
        valu = rows[1].text.strip()
        find = text.find('（')
        if find >= 0:
            valu =f"{valu}::{text[find:]}"
            text = text[:find]
        #print("Herb:", text, "Poison?:", valu)
        if text: append_add(psnd, text, valu)
        else: print("Empty name:", valu, file=sys.stderr)
        #if input("quit?"): break

######################################
  #### END( WEB SCRAPING CODE ) ####
######################################

def test_extract(use_cache=False):
    global CACHE
    if use_cache: from pagecache import CACHE
    if 'CACHE' not in globals(): CACHE = {}
    #【药 材 名】白牛胆【英 文 名】Sheepear Inula Her（羊耳菊）
    for med in ('卷柏','蚤休','七里香', '菊花参', '白牛胆',
                '元参','金钱桔饼','葱白', "厚朴", "川朴",
                "羊踯躅", '禹白附', '半支莲', '半边莲'):
        print_med(med, extract(med) )
        time.sleep(3)

#test_extract()
from pagecache import CACHE
#print_med('卷柏', extract('卷柏'))
#print_med('蚤休', extract('蚤休'))
#print_med('半支莲', extract('半支莲'))
#print_med('七里香', extract('七里香'))
#test_extract(True)

if __name__ == "__main__":
    medict = {}
    scrape_and_save('unimed', True)
    check_and_save()

    #try: from medata import medict
    #except: medict = {}

    #psnd = extract_poisons()

    for kk, dd in medict.items():
        print(kk, getMeridian(dd))
        print(kk, getFlavorAttr(dd))
        if input("Quit?"): break


