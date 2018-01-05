#coding=utf-8

'''
Created on 2016-9-22

@author: admin
'''

import os
import re
import time
import json
import random
import requests
import functools
import hashlib
import traceback
import datetime
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
from requests.exceptions import ConnectionError
from requests.packages.urllib3.connectionpool import HTTPConnectionPool
from urllib2 import HTTPError
from utncommon.util import MyEncoder
from utncommon import date, log
from utncommon.sprider.spider import SpiderError, ERROR_CODE_IO,\
    ERROR_CODE_INHIBIT, ERROR_CODE_PARSE

ERROR_CODE_UNKNOWN  = 999

def logger(message):
    """
              在方法执行前输出的日志信息
    """
    def log_decorator(func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log.info(message)
            return func(*args, **kwargs)
        return wrapper
    
    return log_decorator


def retry(times=3, interval=0):
    """
                方法失败时重新调用,尝试times次,重复调用间隔interval秒
    """
    def retry_decorator(func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ts = 0
            while ts<=times:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    log.error(u"[RetryTimes:%d] 调用方法[%s]出错:\n%s"%(ts,func.__name__,traceback.format_exc()))
                    time.sleep(interval)
                    ts += 1
            raise
        return wrapper
    
    return retry_decorator

def catch(flag=True):
    """
                捕获异常
    """
    def catch_decorator(func):
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            
            try:
                
                return func(*args, **kwargs)
            
            except SpiderError as err:
                
                if flag is False:
                    raise
                formatted_lines = traceback.format_exc().splitlines()
                log.error("func[%s] : %s , %s"%(func.__name__,formatted_lines[-1],formatted_lines[-3]))
            
            except Exception as ex:
                
                if flag is False:
                    raise SpiderError(ERROR_CODE_PARSE, ex.message)
                formatted_lines = traceback.format_exc().splitlines()
                log.error("func[%s] : %s , %s"%(func.__name__,formatted_lines[-1],formatted_lines[-3]))
                
        return wrapper
    
    return catch_decorator

class BaseCrawler(object):
    
    REG_MILTIMESTRAMP = re.compile(u"^\d{13}$")
    
    default_charset = u'utf-8'
    
    cookies= RequestsCookieJar()
    
    client = requests.Session()
    
    TIMEOUT = 60
    
    HOST = None
    
    USER_AGENTS = [u"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
                   u"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0" ,
                   u"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0",
                   u"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
                   u"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)",
                   u"Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50",
                   u"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
                   u"Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
                   u"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
                   u"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
                   u"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0",
                   u"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
                   u"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201",
                   u"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201"
                   
    ]
    
    HEADERS = {u"Accept" : u"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
               u"Accept-Encoding" : u"gzip, deflate, sdch",
               u"Accept-Language" : u"zh-CN,zh;q=0.8",
               u"User-Agent": random.choice(USER_AGENTS)}
    #PROXIES = {u"http":u"202.171.253.72:80"}
    PROXIES={}
    
    CODE_LIST_INHIBIT = [503,403]
    
    def __init__(self):
        '''
        Constructor
        '''
        
    def _create_headers(self, add_headers = None):
        
        headers = self.HEADERS
        
        if add_headers:
            for key in add_headers:
                headers[key] = add_headers[key]
        
        return headers

    def _do_get(self, url, headers=None, proxies={}, cookies=None, stream=False):
        
        if not headers :
            headers = self.HEADERS
            
        if self.HOST :
            headers.update({"Referer":self.HOST})
            
        if not cookies :
            cookies = self.cookies
            
        if not proxies :
            proxies = self.PROXIES
               
        try:
            response = self.client.get(url, headers=headers, cookies=cookies, proxies=self.PROXIES, timeout=self.TIMEOUT, verify=False, stream=stream)
        except HTTPError as error:
            raise SpiderError(ERROR_CODE_IO, error.message)
        except ConnectionError as error:
            raise SpiderError(ERROR_CODE_IO, error.message)
        except HTTPConnectionPool as error:
            raise SpiderError(ERROR_CODE_IO, error.message)
    
        if response.ok:
            self.cookies.update(response.cookies)
            return response
        
        if response.status_code in self.CODE_LIST_INHIBIT:
            raise SpiderError(ERROR_CODE_INHIBIT, response.reason)
        
        raise SpiderError(ERROR_CODE_UNKNOWN, response.reason)

    def _do_post(self, url, params, headers=None, proxies={}, cookies=None, stream=False):
        
        if not headers :
            headers = self.HEADERS
            
        if self.HOST :
            headers.update({"Referer":self.HOST})
            
        if not proxies :
            proxies = self.PROXIES
            
        if not cookies :
            cookies = self.cookies
            
        try:
            response = self.client.post(url, data=params, headers=headers, cookies=cookies, proxies=self.PROXIES, timeout=self.TIMEOUT, verify=False, stream=stream)
        except HTTPError as error:
            raise SpiderError(ERROR_CODE_IO, error.message)
        except ConnectionError as error:
            raise SpiderError(ERROR_CODE_IO, error.message)
        except HTTPConnectionPool as error:
            raise SpiderError(ERROR_CODE_IO, error.message)
        
        if response.ok:
            self.cookies.update(response.cookies)
            return response
        
        if response.status_code in self.CODE_LIST_INHIBIT:
            raise SpiderError(ERROR_CODE_INHIBIT, response.reason)
        
        raise SpiderError(ERROR_CODE_UNKNOWN, response.reason)
       
    def _parse_date(self, datestr):
        datestr = datestr.strip().split(" ")[0]
        date_array = re.split(u'年|月|日|-|/', unicode(datestr))
        return datetime.date(int(date_array[0]), int(date_array[1]), int(date_array[2]))
#         return u"-".join(date_array).strip(u"-")
    
    def get_page_charset(self,page):
        if not page :
            return self.default_charset
        bs = BeautifulSoup(page,u'html5lib')
        meta_nodes = bs.find_all(u"meta", {u"content":True})
        for meta_node in meta_nodes :
            content_value = meta_node.get(u"content")
            if not u'charset' in content_value :
                continue
            result = content_value.split(u';')
            for data_str in result :
                sub_result = data_str.split(u'=')
                key = self.get_strip_string(sub_result[0])
                if not (len(sub_result) == 2 and key == u'charset' ) :
                    continue
                return self.get_strip_string(sub_result[1])
        return self.default_charset
    
    def get_tag_string(self, tag):
        if(tag is None):
            return u""
        
        return tag.get_text().strip()
    
    def get_tag_strip_string(self, tag):
        return re.sub(u"\s+|\\xc2|\\xa0|\u3000",u"",self.get_tag_string(tag))
    
    def get_strip_string(self, string):
        if(string is None):
            return u""
        #\u3000中文全角空格
        return re.sub(u"\s+|\\xc2|\\xa0|\u3000",u"",string)
    
    def get_gap_string(self, string):
        if(string is None):
            return u""
        #\u3000中文全角空格
        return re.sub(u"\s+|\\xc2|\\xa0|\u3000",u" ",string).strip()
    
    def find_children(self, tag, name=None, attrs={}, text=None):
        """
                        查找当前节点下直接子节点，中间不能有其他节点
                         如：
        <html>
         <head>
          <title>
           The Dormouse's story
          </title>
         </head>
        </html>
        html节点的直接子节点是head，head的直接子节点是title
        """
        if(tag is None) :
            return []
        return tag.find_all(name=name, attrs=attrs, text=text, recursive=False)
    
    def find_subtag(self, tag, name=None, attrs={}, text=None):
        if(tag is None) :
            return
        return tag.find(name=name, attrs=attrs, text=text)
    
    def find_subtags(self, tag, name=None, attrs={}, text=None):
        if(tag is None) :
            return []
        return tag.find_all(name=name, attrs=attrs, text=text)
    
    def find_parenttag(self, tag, name=None, attrs={}):
        if(tag is None) :
            return
        return tag.find_parent(name=name, attrs=attrs)
    
    def find_next_sibling(self, tag, name=None, attrs={}, text=None):
        if(tag is None) :
            return
        return tag.find_next_sibling(name=name, attrs=attrs, text=text)
    
    def find_next_siblings(self, tag, name=None, attrs={}, text=None):
        if(tag is None) :
            return []
        return tag.find_next_siblings(name=name, attrs=attrs, text=text)
    
    def find_previous_sibling(self, tag, name=None, attrs={}, text=None):
        if(tag is None) :
            return
        return tag.find_previous_sibling(name=name, attrs=attrs, text=text)
    
    def find_previous_siblings(self, tag, name=None, attrs={}, text=None):
        if(tag is None) :
            return []
        return tag.find_previous_siblings(name=name, attrs=attrs, text=text)
    
    def parse_date(self, date_str):
        try :
            return self._parse_date(date_str)
        except :
            return date_str
        
    def parse_timestramp(self, src_timestamp):
        try :
            return date.timestamp2str(src_timestamp/1000)
        except :
            return src_timestamp
        
    def get_timestramp(self):
        return int(time.time()*1000)
        
    def set_attribute(self, obj, field, value, parsed=False):
        if value is None or value==u"":
            return
        if hasattr(obj, field) :
            if parsed or u"date" in field or u"time" in field or u"not" in field :
                setattr(obj,field,self.parse_date(value))
            else :
                setattr(obj,field,value)
              
    def do_get(self, url, headers=None, proxies={}, cookies=None, stream=False):
        response = self._do_get(url, headers, proxies, cookies, stream)
        html = response.text
        return html
     
    def do_post(self, url, params, headers=None, proxies={}, stream=False):
        response = self._do_post(url, params, headers, proxies, stream)
        html = response.text
        return html
    
    def get_soup(self, html, charset=None, markup=u'html5lib'):
        if not html :
            return
        if not charset :
            charset = self.get_page_charset(html)
        html = html.replace(u'<br>',u'\n').replace(u'</br>',u'\n').replace(u'<br/>',u'\n')
        return BeautifulSoup(html.decode(charset,u'ignore'),markup)
    
    def get_tag_attr(self, tag, attr):
        if (tag is None) :
            return u""
        return tag.get(attr)
    
    def down_attach(self, url, filename):
        try :
            self.check_filepath(filename)
            r = self._do_get(url=url, stream=True) # here we need to set stream = True parameter  
            with open(filename, u'wb') as f:  
                for chunk in r.iter_content(chunk_size=100*1024):  
                    if chunk: # filter out keep-alive new chunks  
                        f.write(chunk)  
                        f.flush()  
                f.close()
                return True
        except :
            return False
            
    def check_filepath(self, filename):
        filepath = os.path.dirname(filename)
        if not os.path.exists(filepath) :
            os.makedirs(filepath)
            
    def save_to_file(self, filename, datastr, mode=u'w', code=u'utf-8'):
        self.check_filepath(filename)
        with open(filename, mode) as file_obj:
            file_obj.write(datastr.encode(code))
        
    def is_file_exists(self, filename):
        return os.path.isfile(filename)
    
    def remove_file(self, filename):
        if self.is_file_exists(filename):
            os.remove(filename)
    
    def get_dir_files(self, dir_path):
        dir_path = dir_path
        dirs = os.listdir(dir_path)
        files = []
        for d in dirs :
            p = os.path.join(dir_path,d)
            if os.path.isdir(p):
                next_level_files = self.get_dir_files(p)
                files.extend(next_level_files)
            elif os.path.isfile(p):
                files.append(p)
        return files
    
    def read_from_file(self, filename, mode=u'r'):
        with open(filename, mode) as file_obj:
            data = file_obj.read()
            return data
            
    def obj2json(self, obj):
        return json.dumps(obj, ensure_ascii=False, cls=MyEncoder)
    
    def json2obj(self, jsonstr):
        return json.loads(jsonstr)
            
    def get_md5(self, datastr):
        md5 = hashlib.md5()
        md5.update(datastr)
        return md5.hexdigest()
