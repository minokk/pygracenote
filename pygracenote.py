import requests
import os
import glob
import struct
import re
import xml.etree.ElementTree as ET

def regGracenote():
    if os.path.exists('ClientID'):
        with open('ClientID') as f:
            ClientID = f.read()
    payload = ('<QUERIES>\n'
             '<QUERY CMD="REGISTER">\n'
             '<CLIENT>'+ClientID+'</CLIENT>\n'
             '</QUERY>\n'
             '</QUERIES>')
    res = requests.post(
        url = 'https://c2091926011.web.cddbp.net/webapi/xml/1.0/',
        data = payload,
        headers = {"Content-Type":"application/xml", "Content-Length":str(len(payload))})
    if res != 200:
        print('genarate user ID error:',res.status_code)
        exit()
    for r in ET.fromstring(res.content).iter('USER'):
        ret = r.text
    return ret

def WhereCD():
    flag = 'A'
    drive = ['C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

    for nowdrive in drive:
        if os.path.exists(nowdrive + ':\\Track01.cda'):
            print("CD exists:DRIVE " + nowdrive)
            flag = nowdrive
            break
    return flag

def getuserID():
    if os.path.exists('userID'):
        with open('userID') as f:
            userID = f.read()
    else:
        userID = regGracenote()
        print(userID)
        with open('userID', encoding='utf-8', mode='w') as w:
            w.write(userID)
    return userID

def makeTOC(drive):
    ret = ''
    tracknum = len(glob.glob(drive + ':\\*.cda'))
    for track in range(1, tracknum + 1):#ファイル数数える
        with open(drive + ':\\Track'+str(track).zfill(2)+'.cda', mode = 'rb') as f:
            f.seek(28)#ずらす
            frame = ''
            endframe = ''
            for count, bytes in enumerate(iter(lambda: f.read(1), b'')):#1バイトずつ読み出し
                if 0 <= count <= 3:
                    frame = str(bytes.hex()) + frame
                if 4 <= count <= 7:
                    endframe = str(bytes.hex()) + endframe
        ret = ret + str(int(frame, 16) + 150) + ' '
        if track == tracknum:
            ret = ret + str(int(frame, 16) + int(endframe, 16) + 150)
    return ret

def makeserial(drive):
    ret = ''
    with open(drive + ':\\Track01.cda', mode = 'rb') as f:
        f.seek(24)
        for count, bytes in enumerate(iter(lambda: f.read(1), b'')):#1バイトずつ読み出し
            if 0 <= count <= 3:
                ret = str(bytes.hex()) + ret
            if count == 4:
                break
    for i in range(8):
        ret = re.sub('^0', '', ret)
    return ret

def GetFromGracenote(payload):
    res = requests.post(
        url = 'https://c2091926011.web.cddbp.net/webapi/xml/1.0/',
        data = payload,
        headers = {"Content-Type":"application/xml", "Content-Length":str(len(payload))})
    if res != 200:
        print('get data from gracentoe error:',res.status_code)
        exit()
    return res.text

def makeini(xml, serial):
    for r in ET.fromstring(xml).iter('ARTIST'):
        artist = r.text
    for r in ET.fromstring(xml).iter('TITLE'):
        title = r.text
        break
    for r in ET.fromstring(xml).iter('DATE'):
        date = r.text
    for r in ET.fromstring(xml).iter('TRACK_COUNT'):
        numtracks = r.text
    with open('cdplayer.ini', mode='w', encoding='utf-8') as w:
        w.write('[' + serial + ']\n')
        w.write('artist='+artist+'\n')
        print('artist='+artist)
        w.write('title='+title+'\n')
        print('album='+title)
        print('year='+date)
        w.write('numtracks='+numtracks+'\n')
        for count, title in enumerate(ET.fromstring(xml).iter('TITLE')):#1バイトずつ読み出し
            if count == 0:
                continue
            w.write(str(count-1)+'='+title.text+'\n')
            print(str(count-1).zfill(2)+':'+title.text)
    return

if __name__ == "__main__":

    userID = getuserID()
    drive = WhereCD()
    if drive == 'A':
        print('no CD exist')
    
    payload = (
        '<QUERIES>'
            '<AUTH>'
                '<CLIENT>2091926011-4274C37419A9D5278558139AF472AD63</CLIENT>'
                '<USER>'+userID+'</USER>'
            '</AUTH>'
            '<QUERY CMD="ALBUM_TOC">'
                '<MODE>SINGLE_BEST</MODE>'
                '<TOC>'
                    '<OFFSETS>'+makeTOC(drive)+'</OFFSETS>'
                '</TOC>'
            '</QUERY>'
        '</QUERIES>')

    resultxml = GetFromGracenote(payload)
    serial = makeserial(drive)
    makeini(resultxml, serial)