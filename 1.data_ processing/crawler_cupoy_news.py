#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
from tornado import gen, httpclient, ioloop
from requests import get
import re
import os
import sys
import pandas as pd
 

class SynSpider(object):
    content_list = []
    def __init__(self, urls):
        self.urls = urls
        
    def fetch_url(self, url):
        r = get(url)
        return r.content

    def handle_page(self, html):
        content = ''
        reg = re.compile('<[^>]*>')
        content = reg.sub('',html.decode('utf-8')).replace('\n','').replace(' ','').replace('\r','').replace('\t','')
        self.content_list.append(content)

    def run(self):
        for url in self.urls:
            html = self.fetch_url(url)
            self.handle_page(html)


class AsyncSpider(object):
    content_list = []
    def __init__(self, urls):
        self.urls = urls

    @gen.coroutine
    def fetch_url(self, url):
        try:
            response = yield httpclient.AsyncHTTPClient().fetch(url)
        except Exception as e:
            print('Exception: %s %s' % (e, url))
            print('fetch fail')
            raise gen.Return('')

        raise gen.Return(response.body)

    def handle_page(self, html):
        content = ''
        reg = re.compile('<[^>]*>')
        if html != '':
            content = reg.sub('',html.decode('utf-8')).replace('\n','').replace(' ','').replace('\r','').replace('\t','')
        else:
            content = ''            
        self.content_list.append(content)
        

    @gen.coroutine
    def _run(self):
        for url in self.urls:
            html = yield self.fetch_url(url)
            self.handle_page(html)

    def run(self):
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._run)

        
        

if __name__ == '__main__':
    path_dir = '/home/jovyan/AIA_project/datasets/cupoy/regular_dataset'
    file_list = os.listdir(path_dir)
    for p in file_list:
        data = pd.read_json(path_dir+'/'+p)
        urls = list(data['cbodyurl'])
        file_name = p.split('/')[-1].rstrip('.json')
        print('爬取'+file_name+'...')
        s = AsyncSpider(urls)
        s.content_list = []
        s.run()
        data['txtcontent'] = data['txtcontent'].str.replace('\r','').replace('\n','').replace('\t','')
        data['content'] = s.content_list
        data.to_csv('./news/'+ file_name + '.csv')
        del s