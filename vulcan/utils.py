#!/usr/bin/env python
# coding:utf-8
# code by pnig0s@20140131

import urlparse
import bs4

import lxml.html as H
from splinter import Browser

class WebKit(object):
    '''WebKit引擎'''
    def __init__(self):
        self.tag_attr_dict = {'*':'href',
                              'embed':'src',
                              'frame':'src',
                              'iframe':'src',
                              'object':'data'}

    def extract_links(self,url):
        '''
        抓取页面链接
        '''
        self.browser = Browser("phantomjs")
        try:
            self.browser.visit(url)
        except Exception,e:
            return
        for tag,attr in self.tag_attr_dict.iteritems():
            link_list = self.browser.find_by_xpath('//%s[@%s]' % (tag,attr))
            if not link_list:
                continue
            for link in link_list:
                link = link.__getitem__(attr)
                if not link:
                    continue
                link = link.strip()
                if link == 'about:blank' or link.startswith('javascript:'):
                    continue
                if not link.startswith('http'):
                    link = urlparse.urljoin(url,link)
                yield link
    
    def close(self):
        self.browser.quit()

class HtmlAnalyzer(object):
    '''页面分析类'''
    @staticmethod
    def extract_links(html,base_ref,tags=[]):
        '''
        抓取页面内链接(生成器)
        base_ref : 用于将页面中的相对地址转换为绝对地址
        tags     : 期望从该列表所指明的标签中提取链接
        '''
        if not html.strip():
            return
            
        link_list = []
        try:
            doc = H.document_fromstring(html)
        except Exception,e:
            return
            
        default_tags = ['a','img','iframe','frame']
        default_tags.extend(tags)
        default_tags = list(set(default_tags))
        doc.make_links_absolute(base_ref)
        links_in_doc = doc.iterlinks()
        for link in links_in_doc:
            if link[0].tag in set(default_tags):
                yield link[2]

    @staticmethod
    def extract_links_gxdk(html):
       soup = bs4.BeautifulSoup(html, from_encoding='utf-8')
       div = soup.find('div' , {'class' : 'detailbox'})
       link_list = []
       if div is not None:
           for a in div.find_all('a'):
               href = a.get('href')
               if href is not None:
                   if 'tag' not in href and 'news.gxdk.com.cn/list' not in href:
                       if href.find('/list') == 0:
                           link_list.append('http://news.gxdk.com.cn' + href)
                       if href.endswith('shtml'):
                           link_list.append(href)

       for link in link_list:
           yield link

    @staticmethod
    def extract_links_ithome(html):
       soup = bs4.BeautifulSoup(html, from_encoding='utf-8')
       list = []
       href = ''
       div = soup.find('div' , {'class' : 'content fl'})
       if div is None:
           return
       for a in div.find_all('a'):
           href = a.get('href')
           if href is None:
               continue
           if 'tag' not in href and (href.endswith('html') or href.endswith('htm')):
               print 'page', href
               if href.find('/category/47') == 0:
                   list.append('http://it.ithome.com' + href)     
               else:
                   list.append(href)

       for link in list:
           yield link
