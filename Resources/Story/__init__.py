#!/usr/bin/env python
#-*-encoding:utf-8-*-
'''
Created on 2016-05-06 12:18

@author: chenyongbing
'''
import sys, os, urllib, re, logging, commands, json

reload(sys)
sys.setdefaultencoding('utf-8')
current_dir = os.path.split(os.path.realpath(__file__))[0]