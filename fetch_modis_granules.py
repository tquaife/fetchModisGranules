#!/usr/bin/python

import re
import os
import datetime as dt
import subprocess

from HTMLParser import HTMLParser

SERVER="https://e4ftl01.cr.usgs.gov/"
TOPDIR="/media/tqu/data/MODIS"

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class LinkGetter(HTMLParser):
    def __init__(self):
        self.reset()
        self.links = []    
    def handle_starttag(self, tag, attrs):
        if tag=="a":
            for (i,attr) in enumerate(attrs):
                if attr[0]=="href":
                    self.links.append(attr[1])    
    def get_data(self):
        return self.links

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
        
def get_links(html):
    p=LinkGetter()
    p.feed(html)
    return p.get_data()        
        
def run_wget(url,fetch_to_stdout=False):    
    args=["wget",url]
    if fetch_to_stdout==True:
        args=["wget","-O","-",url]    
    p=subprocess.Popen(args,stdout=subprocess.PIPE)  
    return p.communicate()
    
def get_mission_code(product):
    if product[:3]=="MOD":
        return "MOLT"
    if product[:3]=="MYD":
        return "MOLA"
    if product[:3]=="MCD":
        return "MOTA"
    
def get_date_list(product):
    """Given a valid product code parse the html
    returned by the server and extract the links
    that correspond to dates"""
    c=get_mission_code(product)
    url=SERVER+"/"+c+"/"+product
    html=run_wget(url,fetch_to_stdout=True)[0]
    links=get_links(html)
    dates=[]
    for link in links:
        if re.match('[0-9]{4}\.[0-9]{2}\.[0-9]{2}', link):
            dates.append(link[:10])
    return dates


def convert_date(d):
    """Assumes d is a string with the format yyyy.mm.dd"""
    return dt.date(year=int(d[0:4]),month=int(d[5:7]),day=int(d[8:10]))


def subset_date_list(dates, beg_date=None, end_date=None):
    """Remove dates outsides requested range.
    Assumes dates are strings with the format yyyy.mm.dd"""

    beg=convert_date('1000.01.01')
    if beg_date!=None:
        beg=convert_date(beg_date)
    end=convert_date('3000.01.01')
    if end_date!=None:
        end=convert_date(end_date)
    
    out=[]
    for date in dates:
        d=convert_date(date)
        if d <= end and d >= beg:
            out.append(date)
    return out

def get_granule_urls(product, dates, tiles):
    
    urls=[]
    for date in dates:
        c=get_mission_code(product)
        url=SERVER+"/"+c+"/"+product+"/"+date+"/"
        html=run_wget(url,fetch_to_stdout=True)[0]
        links=get_links(html)
        for link in links:
            for t in tiles:
                if re.match('.*'+t+'.*hdf$', link):
                    urls.append(url+"/"+link.rstrip("/"))
    return urls 

def remove_double_slash(url):
    new="abcd"
    p=re.compile("//")
    q=re.compile(":/")
    while new != url:
        new=p.sub("/",url)
        url=new
    url=q.sub("://",url)
    return url

def fetch_modis_granules(urls):

    for u in urls:
        u=remove_double_slash(u)
        fnam=u.split("/")[-1]
        date=u.split("/")[-2]
        prod=u.split("/")[-3]
        code=u.split("/")[-4]
    
        directory=TOPDIR+"/"+code+"/"+prod+"/"+date+"/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        os.chdir(directory)
        if not os.path.isfile(fnam):
            run_wget(u)
        else:
            print "skipping: "+fnam

if __name__=="__main__":

    product="MOD13A1.006"
    dates=get_date_list(product)
    dates=subset_date_list(dates,'2016.01.01','2016.01.10')
    tiles=['h18v08']
    url_list=get_granule_urls(product, dates, tiles)
    fetch_modis_granules(url_list)
    

    
    
