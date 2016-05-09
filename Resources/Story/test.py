#!/usr/bin/env python
#-*-encoding:utf-8-*-
'''
Created on 2016-05-06 13:54

@author: chenyongbing
'''
import sys, os, urllib, re, logging, commands, json

reload(sys)
sys.setdefaultencoding('utf-8')
current_dir = os.path.split(os.path.realpath(__file__))[0]


import threading,thread
import time

exitFlag = 0

class myThread (threading.Thread):   #继承父类threading.Thread
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self._stop = threading.Event()
   def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
      print "Starting " + self.name
      print_time(self.name, self.counter, 5)
      print "Exiting " + self.name
   def stop(self):
      self._stop.set()
def print_time(threadName, delay, counter):
   while counter:
      if exitFlag:
         thread.exit()
      time.sleep(delay)
      print "%s: %s" % (threadName, time.ctime(time.time()))
      counter -= 1

# 创建新线程

thread2 = myThread(2, "Thread-2", 2)

# 开启线程

# thread2.start()
# thread1._stop()
print "Exiting Main Thread"
count = 0
while 1:
   count += 1
   print "main " , count
   if count == 2:
      thread1 = myThread(1, "Thread-1", 1)
      thread1.start()
   if count%3==0:
      thread1.stop()
   if count == 5 :
      thread1 = myThread(1, "Thread-1", 1)
      thread1.start()
   time.sleep(3)