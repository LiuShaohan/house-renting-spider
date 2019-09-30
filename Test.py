import Utils
from w3lib import html
import re
import requests
from lxml import etree
import bs4

# ID= link-report

'''
def getImageURLNotUserHeadFromURL(url, tag='', attrs={}):
    htmlContent = Utils.Utils.getHtmlContentFromURL(url)
    soup = bs4.BeautifulSoup(htmlContent, 'html.parser')
    #[i.extract() for i in (soup.findAll(name=tag, attrs=attrs))]
    soup = soup.findAll(name=tag, attrs=attrs)
    print(soup)

    #soup.findAll(name=tag, attrs=attrs)
    return soup
'''
title,content = Utils.Utils.getTitleAndContentTextFromURL(Utils.Utils.getHtmlContentFromURL('https://www.douban.com/group/topic/153273054/'))
print(title)
print(content)
