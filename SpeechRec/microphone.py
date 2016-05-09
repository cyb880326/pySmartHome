#!/usr/bin/env python
#-*-encoding:utf-8-*-

'''
Created on 16/5/4

@author: chenyongbing
'''

import sys, os, urllib, re, logging, commands, json

reload(sys)
sys.setdefaultencoding('utf-8')
current_dir = os.path.split(os.path.realpath(__file__))[0]

from pyaudio import PyAudio,paInt16
from array import array
import wave


class MicroPhone(object):
    '''
        麦克风 录制
    '''
    def __init__(self):
        # define of params
        self.NUM_SAMPLES = 4096
        self.framerate = 44100
        self.channels = 1
        self.sampwidth = 2
        # record time
        self.TIME = 10

    def save_wave_file(self,filename, data):
        '''save the date to the wav file'''
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.framerate)
        wf.writeframes("".join(data))
        wf.close()


    def getRate(self,p):
        return self.framerate
        devcount = p.get_device_count()
        print  "Here are the available audio devices:"

        default_device_index = 0

        for device_index in range(devcount):
            device = p.get_device_info_by_index(device_index)
            print "[%s]  %s\tDefault Sample Rate: %i\t%s" % (device_index, device['name'], device['defaultSampleRate'],
                                                             "Default" if device_index == default_device_index else "")

        desired_device_index = raw_input("\nWhich device would you like to record audio from: ")

        device = p.get_device_info_by_index(int(desired_device_index))

        try:
            print  ("\nUsing device:\t%s" % device['name'])
            start = raw_input("\n[enter] to begin recording, [ctrl-c] to cancel\n")
        except KeyboardInterrupt:
            raise KeyboardInterrupt("\ncancelled recording")

        rate = int(device['defaultSampleRate'])
        return rate


    def load_pocketsphinx(self):
        '''加载 pocketsphinx'''
        print self.__doc__
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
        config.set_string('-adcdev', 'plughw:1,0')
        decoder = Decoder(config)
        return decoder

    def record(self):
        #open the input of wave
        pa = PyAudio()
        stream = pa.open(format = paInt16, channels = 1,
            rate = self.getRate(pa), input = True,
            frames_per_buffer = self.NUM_SAMPLES)
        save_buffer = []

        record_start = False
        record_end = False

        no_record_times = 0


        while 1:
            #read NUM_SAMPLES sampling data
            string_audio_data = stream.read(self.NUM_SAMPLES)
            if record_start == True :save_buffer.append(string_audio_data)
            print max(array('h', string_audio_data))
            if max(array('h', string_audio_data)) >5000:
                record_start = True
                no_record_times = 0
            else:
                no_record_times += 1
            if record_start == False:continue

            if no_record_times >10:
                break
        stream.close()
        pa.terminate()
        return save_buffer
        #
        # decoder.end_utt()
    def recognition_buffer(self,buffer):
        '''识别'''
        in_speech_bf = False
        decoder = self.load_pocketsphinx()
        decoder.start_utt()
        for  string_audio_data in buffer:
            if string_audio_data:
                decoder.process_raw(string_audio_data, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        print 'Result:', decoder.hyp().hypstr
                        decoder.start_utt()
            else:
                decoder.end_utt()

    def recognition_wav(self,filename):
        decoder = self.load_pocketsphinx()
        decoder.start_utt()
        in_speech_bf = False
        stream = open(filename, 'rb')
        while True:
            buf = stream.read(self.NUM_SAMPLES)
            if buf:
                decoder.process_raw(buf, False, False)
                if decoder.get_in_speech() != in_speech_bf:
                    in_speech_bf = decoder.get_in_speech()
                    if not in_speech_bf:
                        decoder.end_utt()
                        print 'Result:', decoder.hyp().hypstr
                        decoder.start_utt()
            else:
                decoder.end_utt()
        decoder.end_utt()

if __name__=='__main__':
    import datetime
    logging.basicConfig(level = logging.WARN)
    myMicroPhone = MicroPhone()
    while 1:
        buffer = myMicroPhone.record()
        filename = os.path.join(current_dir,datetime.datetime.now().strftime("%Y%m%d%H%M%S")+".wav")
        myMicroPhone.save_wave_file(filename,buffer)
        myMicroPhone.recognition_wav(filename)
