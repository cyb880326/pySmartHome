#!/usr/bin/env python
#-*-encoding:utf-8-*-
'''
Created on 2016-05-06 12:18

@author: chenyongbing
'''
import sys, os, urllib, re, logging, commands, json
import  urlparse,base64
# reload(sys)
# sys.setdefaultencoding('utf-8')
current_dir = os.path.split(os.path.realpath(__file__))[0]



class StoryText():
    def __init__(self):
        pass
        self.URL = 'http://www.61ertong.com/wenxue/'
        self.HTMLPATH = os.path.join(current_dir,'../../tmp')

    def download(self,url):
        urlname = re.sub('http://','',url)
        urlname = re.sub('/$','.html',urlname)
        if not re.search('\.',urlname.split('/')[-1]):
            urlname = urlname + '.html'
        filename = self.HTMLPATH + '/'+urlname
        if os.path.exists(filename):
            logging.info('%s 已经下载 %s'%(url,filename))
            return open(filename).read()
        filePath = os.path.dirname(filename)
        logging.info('%s 开始下载 %s' % (url, filename))
        if not os.path.exists(filePath):
            os.popen('mkdir -p %s'%filePath)

        html = urllib.urlopen(url).read()
        fr = open(filename,'w+')
        fr.write(html)
        fr.close()
        return html

    def analyze_index(self):
        html = self.download(self.URL)
        cate_group = re.search('<ul class="wenxue_menu">(.*?)</ul>',html,re.DOTALL)
        if cate_group == None:
            return
        cate_html = cate_group.group(1)


        for cate_url , cate_name in re.findall('<a href="([^\"]+)" class="wx_c[\d]+">\s*<h2>([^<]+)</h2>',cate_html,re.DOTALL):
            print cate_name , cate_url
            self.analyze_page(cate_url)
    def analyze_page(self,cate_url):
        html = self.download(cate_url)
        self.analyze_story_list(html)
        page_group = re.search("<a href='([^\']+)' title='下一页'>下一页</a>",html)
        if page_group == None:
            return
        page_url = urlparse.urljoin(cate_url,page_group.group(1))
        self.analyze_page(page_url)

    def analyze_story_list(self,html):
        story_list_group = re.search('<div class="list">(.*?)</div>',html,re.DOTALL)
        if story_list_group == None:
            return
        story_list_html = story_list_group.group(1)
        for story_url , story_name in re.findall('<a href="([^\"]+)" target="_blank" title="([^\"]+)">',story_list_html,re.DOTALL):
            self.analyze_story(story_url=story_url , story_name = story_name)

    def analyze_story(self,story_url='',story_name = ''):
        html = self.download(story_url)
        # return
        content_group = re.search('<div class="content">(.*?)</div>',html,re.DOTALL)
        if content_group == None:
            return
        content = content_group.group(1)

        next_page_group = re.search("<a href='([^\']+)'>下一页</a>",content)
        if next_page_group != None:
            next_page_url = next_page_group.group(1)
            story_next_page_url = urlparse.urljoin(story_url,next_page_url)
            if story_next_page_url != story_url:
                self.analyze_story(story_url = story_next_page_url , story_name = story_name)



class ChildSongs(StoryText):
    def __init__(self):
        self.URL = 'http://www.61ertong.com/'
        self.HTMLPATH = os.path.join(current_dir, '../../tmp')
        self.cate = ''
        self.cmds = []
    def analyze_index(self):
        html = self.download(self.URL)
        cate_group = re.search('<div class="nav">(.*?)</div>', html, re.DOTALL)
        if cate_group == None:
            return
        cate_html = cate_group.group(1)
        i=0
        for cate_url, cate_name in re.findall('<p class="subnav"><a href="([^\"]+)" target="_blank">([^<]+)</a></p>', cate_html,
                                              re.DOTALL):
            print cate_name, cate_url
            self.cate = cate_name
            i+=1
            if re.search('xiaoyouxi|wenxue',cate_url):continue
            self.analyze_page(cate_url)


    def analyze_page(self, cate_url):
        html = self.download(cate_url)
        self.analyze_song_list(html)
        page_group = re.search("<a href='([^\']+)' title='下一页'>下一页</a>", html)
        if page_group == None:
            return
        page_url = urlparse.urljoin(cate_url, page_group.group(1))
        self.analyze_page(page_url)


    def analyze_song_list(self,html):
        story_list_group = re.search('<div class="flash_list">(.*?)</div>',html,re.DOTALL)
        if story_list_group == None:
            return
        story_list_html = story_list_group.group(1)
        for story_url , story_name in re.findall('<a href="([^\"]+)" title="([^\"]+)" target="_blank">',story_list_html,re.DOTALL):
            self.analyze_song_flash_url(story_url=story_url , story_name = story_name)


    def analyze_song_flash_url(self,story_url='' , story_name = ''):
        html = self.download(story_url)
        url_group = re.search('swfurl:"([^\"]+)"',html,re.DOTALL)
        if url_group != None:
            song_url = url_group.group(1)
            try:
                song_url = base64.b64decode(song_url)
            except:return
            # print self.cate,story_name,song_url
            if not re.search('.swf$',song_url):return
            cmd = 'wget "%s" -O "/data/songs/%s/%s.swf"'%(song_url,self.cate,story_name)
            cmd = "%s"%({'url':song_url,'cate':self.cate,'name':story_name,'suffix':'swf'})
            self.cmds.append(cmd)
    def save_cmd(self):
        fr = open('cmds.txt','w+')
        fr.write('\n'.join(self.cmds))
        fr.close()

    def download_swf(self,data={}):
        url = data.get('url',None)
        cate = data.get('cate',None)
if __name__=='__main__':
    logging.basicConfig(level = logging.WARN)
    #myERTong = StoryText()
    myERTong = ChildSongs()
    myERTong.analyze_index()
    myERTong.save_cmd()