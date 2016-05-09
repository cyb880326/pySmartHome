#!/usr/bin/env python
#-*-encoding:utf-8-*-
'''
Created on 2016-05-05 19:05

@author: chenyongbing
'''
import sys, os, urllib, re, logging, commands, json
import urllib2
import wave,pycurl
from StringIO import StringIO
reload(sys)
sys.setdefaultencoding('utf-8')
current_dir = os.path.split(os.path.realpath(__file__))[0]

class BaiDuSpeech():
    def __init__(self):
        self.cuid = ''

    def get_token(self):
        apiKey = "u8o9vxkdQNLptmGpYhPiFKpD"
        secretKey = "80ddb9029ea3671081094c4d2043aba8"

        auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;

        res = urllib2.urlopen(auth_url)
        json_data = res.read()
        return json.loads(json_data)['access_token']

    ## post audio to server
    def speech_rec(self,token, wav_file):
        '''百度语音识别'''
        fp = wave.open(wav_file, 'rb')
        nf = fp.getnframes()
        f_len = nf * 2
        audio_data = fp.readframes(nf)

        cuid = "xxxxxxxxxx"  # my xiaomi phone MAC
        srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
        http_header = [
            'Content-Type: audio/pcm; rate=8000',
            'Content-Length: %d' % f_len
        ]
        buffer = StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, str(srv_url))  # curl doesn't support unicode
        # c.setopt(c.RETURNTRANSFER, 1)
        c.setopt(c.HTTPHEADER, http_header)  # must be list, not dict
        c.setopt(c.POST, 1)
        c.setopt(c.CONNECTTIMEOUT, 30)
        c.setopt(c.TIMEOUT, 30)
        c.setopt(c.WRITEFUNCTION, None)
        c.setopt(c.POSTFIELDS, audio_data)
        c.setopt(c.POSTFIELDSIZE, f_len)
        c.setopt(c.WRITEDATA, buffer)
        c.perform()  # pycurl.perform() has no return val
        body = buffer.getvalue()
        c.close()
        return body

    def speech_syn(self,token,text):
        '''百度语音合成'''
        cuid = self.cuid
        lan = 'zh'

        data = {'tex':text,
                'lan':lan,
                'token':token,
                'ctp':1,
                'cuid':cuid}
        url = 'http://tsn.baidu.com/text2audio?'+urllib.urlencode(data)
        return url