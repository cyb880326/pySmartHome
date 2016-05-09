#!/usr/bin/env python
#-*-encoding:utf-8-*-
'''
Created on 2016-05-04 20:23

@author: chenyongbing
'''
import sys, os, urllib, re, logging, commands, json

reload(sys)
sys.setdefaultencoding('utf-8')
current_dir = os.path.split(os.path.realpath(__file__))[0]


#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from pyaudio import PyAudio,paInt16
import datetime
import wave
from array import array
import time
from StringIO import StringIO
import json
#define of params
NUM_SAMPLES = 8192
framerate = 44100
channels = 1
sampwidth = 2
#record time
TIME = 10

def save_wave_file(filename, data):
  '''save the date to the wav file'''
  wf = wave.open(filename, 'wb')
  wf.setnchannels(channels)
  wf.setsampwidth(sampwidth)
  wf.setframerate(framerate)
  wf.writeframes("".join(data))
  wf.close()


def getRate(p):
      return 44100
      devcount = p.get_device_count()
      print "Here are the available audio devices:"

      default_device_index = 0

      for device_index in range(devcount):
          device = p.get_device_info_by_index(device_index)
          print "[%s]  %s\tDefault Sample Rate: %i\t%s" % (device_index, device['name'], device['defaultSampleRate'], "Default" if device_index == default_device_index else "")

      #user_input = UserInput(question="\nWhich device would you like to record audio from: ", input_type=int, default_value=default_device_index)
      #
     # desired_device_index = user_input.get_input()
      desired_device_index = raw_input("\nWhich device would you like to record audio from: ")

      device = p.get_device_info_by_index(int(desired_device_index))

      try:
           print  ("\nUsing device:\t%s" % device['name'])
           start = raw_input("\n[enter] to begin recording, [ctrl-c] to cancel\n")
      except KeyboardInterrupt:
           raise KeyboardInterrupt("\ncancelled recording")

      rate = int(device['defaultSampleRate'])
      print rate
      return rate
      return 16000

def record_wave():
  #open the input of wave
  pa = PyAudio()
  stream = pa.open(format = paInt16, channels = 1,
          rate = getRate(pa), input = True,
          frames_per_buffer = NUM_SAMPLES)
  save_buffer = []
  count = 0
  while count < TIME*4:
    #read NUM_SAMPLES sampling data
    string_audio_data = stream.read(NUM_SAMPLES)
    print datetime.datetime.today() ,  string_audio_data
    save_buffer.append(string_audio_data)
    count += 1
    print '.'


import wave
import urllib, urllib2, pycurl
import base64
import json
## get access token by api key & secret key

def get_token():
    apiKey = "u8o9vxkdQNLptmGpYhPiFKpD"
    secretKey = "80ddb9029ea3671081094c4d2043aba8"

    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey;

    res = urllib2.urlopen(auth_url)
    json_data = res.read()
    return json.loads(json_data)['access_token']

def dump_res(buf):
    print buf


## post audio to server
def use_cloud(token,wav_file):
    fp = wave.open(wav_file, 'rb')
    nf = fp.getnframes()
    f_len = nf * 2
    audio_data = fp.readframes(nf)

    cuid = "xxxxxxxxxx" #my xiaomi phone MAC
    srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
    http_header = [
        'Content-Type: audio/pcm; rate=8000',
        'Content-Length: %d' % f_len
    ]
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(srv_url)) #curl doesn't support unicode
    #c.setopt(c.RETURNTRANSFER, 1)
    c.setopt(c.HTTPHEADER, http_header)   #must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    c.setopt(c.POSTFIELDS, audio_data)
    c.setopt(c.POSTFIELDSIZE, f_len)
    c.setopt(c.WRITEDATA, buffer)
    c.perform() #pycurl.perform() has no return val
    body = buffer.getvalue()
    c.close()
    return body

def record_wave():
  #open the input of wave
  pa = PyAudio()
  stream = pa.open(format = paInt16, channels = 1,
          rate = getRate(pa), input = True,
          frames_per_buffer = NUM_SAMPLES)
  save_buffer = []
  count = 0
  least_time = None
  #while count < TIME*4:
  while 1:
    #read NUM_SAMPLES sampling data
    string_audio_data = stream.read(NUM_SAMPLES)
    save_buffer.append(string_audio_data)
    print max(array('h', string_audio_data))
    if max(array('h', string_audio_data)) >2000:
      least_time = time.time()
    if least_time!=None and time.time() - least_time >1:
      break
    count += 1

  filename = datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")+".wav"
  save_wave_file(filename, save_buffer)
  save_buffer = []
  print filename, "saved"
  stream.close()
  pa.terminate()
  return filename






from os import environ, path

from pocketsphinx.pocketsphinx import *
from sphinxbase.sphinxbase import *

MODELDIR = "/home/pi/pyprojects/pocketsphinx"
DATADIR = "/home/pi/pyprojects/pocketsphinx"

# Create a decoder with certain model
config = Decoder.default_config()
config.set_string('-hmm', path.join(MODELDIR, 'zh_broadcastnews_ptm256_8000'))
config.set_string('-lm', path.join(MODELDIR, 'TAR2608/2608.lm'))
config.set_string('-dict', path.join(MODELDIR, 'TAR2608/2608.dic'))
config.set_string('-adcdev','plughw:1,0')
decoder = Decoder(config)

def __decoder__(config,wav_file):
    # Decode streaming data.
    decoder = Decoder(config)
    decoder.start_utt()
    stream = open(path.join(DATADIR, wav_file), 'rb')
    while True:
      buf = stream.read(1024)
      if buf:
        decoder.process_raw(buf, False, False)
      else:
        break
    decoder.end_utt()
    print ('Best hypothesis segments: ', [seg.word for seg in decoder.seg()])



if __name__ == "__main__":
  from subprocess import call
  token = get_token()
  while 1:
    print "----**"*5
    wav_file = record_wave()
    __decoder__(config,wav_file)

    call(['espeak','-vzh',u'请稍等，百度云正在识别'])
    yunMsg = use_cloud(token,wav_file)
    print yunMsg
    json.loads(yunMsg)
    try:
      yunMsg = json.loads(yunMsg)
      print yumMsg
      if yunMsg['err_msg'] == 'success.':
        call(['espeak','-vzh',yunMsg['result'][0]])
      else:
        call(['espeak','recognition error.'])
    except:
      call(['espeak','-vzh','识别失败'])



