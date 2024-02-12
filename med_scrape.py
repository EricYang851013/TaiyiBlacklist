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
import 太医黑名单 as taiyi
from bs4 import BeautifulSoup
import requests, time, re

# extract data from this url:
# f'http://www.a-hospital.com/w/{med}'
# two possible formats: table or paragraph,
# depending on the source of data.

# Another good website is baike.baidu.com 
# https://baike.baidu.com/item/褚实子

IMG_BASE = 'http://p.ayxbk.com/images/thumb/'
def extract(med):
    url = f'http://www.a-hospital.com/w/{med}'
    for i in range(3):
        try: res = requests.get(url)
        except requests.exceptions.Timeout:
            time.sleep(20)
            continue #retry
        if res.status_code == 200: break
        return # all other status_code,
               # 404: title is "页面没找到！"
    else: return # after failing 3 times
    soup = BeautifulSoup(res.text, 'html.parser')
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
        res['性味'] = f"{res['药味']}；{res['药性']}"
        del res['药味'], res['药性']
        # del res['毒性'], res['始载于']
        title_res = 'title' in res
        if title_res:
            print(f"\n   药名不同：{title} <=> {res['药材名']}")
        for kk, vv in para_extract(soup, title).items():
            if res.get(kk) == vv: continue
            if title_res: vv = f'[{title}]：{vv}'
            if kk not in res: res[kk] = vv
            else: res[kk] = f'{res[kk]}《+》{vv}'
    else:
        res = para_extract(soup, title)
        
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
EXCLUDED_KEYS = '1234567891011①②③④⑤⑥⑦⑧⑨⑩'
def para_extract(soup, title):
    entries = {'from':'A+医学百科', '药材名':title}
    openclose = '[]<>【】'
    # medname = '中药名' # ignore this
    for par in soup.find_all("p"):
        text = par.text
        if not text: continue
        find = openclose.find(text[0])
        if find%2: continue # find = -1 included
        cind = text.find(openclose[find+1])
        if cind < 0: continue
        kwd = text[1:cind]
        find = kwd.find('-')
        if find > 0: kwd=kwd[:find]
        kwd = kwd.replace(" ", '')
        kwd = kwd.replace("、", '') #e.g. 元参
        kwd = kwd.replace("性位", '性味') #e.g. 元参
        if kwd in EXCLUDED_KEYS: continue
        text = text[cind+1:].strip()
        if text and len(kwd) <= 9:
             entries[kwd] = text
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
                entries['title'] = title
            continue
        td = row.find('td')
        # posssibly an image
        img = td.find('img')
        if img:
            entries['图片'] = img['src']
            continue
        if td and th:
            entries[th.text] = td.text
    return entries

def printData(medict, fout):
    cols = ['药材名', '别名', '性味', '归经', '功效作用', '英文名']
    kwds = {'别名': ["处方名","异名"], "功效作用": ["功效","通用","功效与作用"],}
    print(f"| {' | '.join(cols)} |", file=fout) # table headers
    print(f"| {' | '.join('---' for c in cols)} |", file=fout)
    for med in medict:
        data, clean = medict[med], {}
        if len(data) < 3: continue
        for c in cols:
            if c in data:
                clean[c] = data[c]
            elif c in kwds:
                clean[c] = " ".join(f'{key}: {data[key]}'
                        for key in kwds[c] if key in data)
            elif c == '性味' and '性味归经' in data:
                text = data['性味归经']
                pi = text.find('。')
                clean['性味'] = text[:pi]
                clean['归经'] = text[pi+1:]
                
        for c, v in clean.items():
            if '\n' in v: clean[c] = v.replace('\n',' ')

        if clean['药材名'] != med: clean['药材名'] += f'[{med}]'

        print(f"| {' | '.join(clean.get(c,'-') for c in cols)} |", file=fout)

def scrape_web(meds, medict, nline=12):
    for med in meds.split(taiyi.ALT_NAME_SEP):
        ens = extract(med)
        if ens:
            medict[med] = ens
            # IDLE在显示很长一行文字的时候很费时，可长达好几分钟
            print(med, end='、' if len(medict)%nline else '、\n')
        time.sleep(3) # don't overwhelm the website

def save_web(medict, file):
    with open(f"{file}.py", "wt", encoding="utf-8") as fout:
        print("medict =", medict, file=fout)
    with open(f"{file}.md", 'wt', encoding="utf-8") as fout:
        printData(medict, fout)

    print(f'\nData saved to files: "{file}.py" and "{file}.md"')

def scrape_and_save(CATS, medone=None, file = 'medict'):
    global medict
    if medone is None: # no previous work
        medict = {} # start fresh
    prev_len = len(medict)
    for cat in CATS:
        for meds in CATS[cat]:
            if medone: # previous work done
                if medone == meds: # til meds 
                    medone = None
                continue
            scrape_web(meds, medict)
            if len(medict) > prev_len + 200:
                save_web(medict, file)
                prev_len = len(medict)
    if prev_len != len(medict):
        save_web(medict, file)
        
### TODO: check consistency of the med base
    # 别名是否有重复？
    # 性味是否和毒性重复？

def alias_enum(dd):
    for key in ('别名', "处方名", "异名"):
        if key not in dd: continue
        for ali in re.sub(r'\([^)]+\)|（[^）]+）|《[^》]+》|[.,、，。]',
                     ' ', dd[key]).split():
            yield ali

def check_duplications(medict):
    medseen, aliseen = {}, {}
    for kk, dd in medict.items():
        med = dd['药材名']
        kd = kk if kk == med else f"{med}<={kk}"
        if med in medseen:
            #print("已有药材名：{kd}")
            medseen[med].append(kk)
            continue
        medseen[med]=[kk]
        for ali in alias_enum(dd):
            if ali == med: continue
            if ali in aliseen:
                if med not in aliseen[ali]: 
                    #print(f"重复的别名：{ali} [{kd}]")
                    aliseen[ali].append(med)
            else: aliseen[ali] = [med]
                
    input(f"别名数: {len(aliseen)}. 药材数 {len(medseen)}")
    count = 0
    for ali, ml in aliseen.items():
        if len(ml)>1:
            print(ali, ml)
        count += len(ml) - 1
    print("Duplications:", count)

    input("太医黑名单中因为重定向而被多次访问的药名：")
    count = 0
    for med, kl in medseen.items():
        count += len(kl) - 1
        if len(kl)<2: continue
        print(med, kl)
        # check consistency
        for kk in kl:
            if kk == med: continue
            for ali in alias_enum(medict[kk]):
                if med == ali: break
            else: print(f"Bad redirection: {kk} => {med}")
    print("Duplications:", count)


######################################
  #### END( WEB SCRAPING CODE ) ####
######################################

def test_extract():
    #【药 材 名】白牛胆【英 文 名】Sheepear Inula Her（羊耳菊）
    for med in ('白牛胆', '元参','金钱桔饼','葱白',
                "厚朴", "川朴", "羊踯躅", '禹白附', '半支莲',
                '半边莲'):
        print(med, ":", extract(med))

# test_extract()

if __name__ == "__main__":
    taiyi.prepare_raw_data()
    scrape_and_save(taiyi.RAW_CAT_DATA)
