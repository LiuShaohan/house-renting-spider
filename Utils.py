import datetime

import bs4
import zxing
import requests
import time
import os, sys
import urllib.request
import re

class Utils(object):

    @staticmethod
    def isInBalckList(blacklist, toSearch):
        if blacklist is None:
            return False
        for item in blacklist:
            if toSearch.find(item) != -1:
                return True
        return False

    @staticmethod
    def getTimeFromStr(timeStr):
        # 13:47:32 or 2016-05-25 or 2016-05-25 13:47:32
        # all be transformed to datetime
        if '-' in timeStr and ':' in timeStr:
            return datetime.datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
        elif '-' in timeStr:
            return datetime.datetime.strptime(timeStr, "%Y-%m-%d")
        elif ':' in timeStr:
            date_today = datetime.date.today()
            date = datetime.datetime.strptime(timeStr, "%H:%M:%S")
            # date.replace(year, month, day)：生成一个新的日期对象
            return date.replace(year=date_today.year, month=date_today.month, day=date_today.day)
        else:
            return datetime.date.today()

    # 该image是否为二维码
    def isQRImages(image_paths):
        if image_paths is None:
            return False
        reader = zxing.BarCodeReader()
        # print(image_paths)
        for image_path in image_paths:
            image_path = str(image_path).replace("\\", "/")
            print(image_path)
            barcode = reader.decode(image_path)
            if barcode is None:
                print("is None")
                continue
            QR_content = barcode.parsed
            if QR_content != '':
                print("这个是二维码")
                return True
            else:
                print("这个不是二维码")
        print("不存在二维码")
        return False

    # 该图片herf是不是二维码
    @staticmethod
    def isNotExitQRImages(imageURLs):
        if imageURLs is None:
            return True
        results_path = os.path.join(sys.path[0], "stemp")
        if not os.path.isdir(results_path):
            os.makedirs(results_path)

        imagePathAndImageNames = []
        imageRealPathAndNames = []
        i = 1
        for url in imageURLs:
            # 下载图片
            # 本地保存的地址
            FILETIMEFORMAT = '%Y%m%d_%X'
            file_time = 'c' + time.strftime(FILETIMEFORMAT, time.localtime()).replace(':', '')
            imageName = file_time + "_" + str(i) + '.png'.strip(' ')
            imageRealPathAndName = os.path.join(results_path, imageName).strip(' ')
            i = i + 1
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                open(imageRealPathAndName, 'wb').write(r.content)  # 将内容写入图片
            del r
            imageRealPathAndNames.append(imageRealPathAndName)
            path = str(os.path.join("stemp", str(imageName)))
            imagePathAndImageNames.append(path)
        isExitQRImages = Utils.isQRImages(imagePathAndImageNames)
        # 删除本地图片
        for imageRealPathAndName in imageRealPathAndNames :
            os.remove(imageRealPathAndName)
        if isExitQRImages:
            return False
        else:
            return True

    # 通过网页地址获取网页内容
    def getHtmlContentFromURL(url):
        # 获取HTML内容
        return urllib.request.urlopen(url).read().decode('utf-8')

    # 通过网页内容获取网页内的图片地址
    def getImageURLFromURL(url):
        htmlContent = Utils.getHtmlContentFromURL(url)
        # 获取HTML内容的图片URL
        reg = r'src="(.*?\.(jpg|png|gif))"'
        img = re.compile(reg)
        imglist = re.findall(img, htmlContent)
        return imglist

    # 通过网页内容获取网页内的图片地址(不包含用户头像)
    ##调用方式
    # htmlContent = Utils.Utils.getImageURLNotUserHeadFromURL("https://www.douban.com/group/topic/151841534/", tag='div', attrs={'class': {'user-face','side-reg'}})
    def getImageURLNotUserHeadFromURL(htmlContent, tag='div', attrs={'class': {'user-face','side-reg'}}):
        # 去除头像标签
        soup = bs4.BeautifulSoup(htmlContent, 'html.parser')
        [i.extract() for i in (soup.findAll(name=tag, attrs=attrs))]
        # 获取HTML内容的图片URL
        reg = r'src="(.*?\.jpg)"'
        img = re.compile(reg)
        imglist = re.findall(img, str(soup))
        return imglist

    #获取标题和正文的文字内容
    def getTitleAndContentTextFromURL(htmlContent, titleTag='h1', titleAttrs={}, contentTag='div',
                                      contentAttrs={'id': 'link-report'}):
        # 源代码转换格式   	BeautifulSoup(htmlContent, "html.parser")
        htmlContentParser = bs4.BeautifulSoup(htmlContent, 'lxml')
        # title区域
        titleText = htmlContentParser.findAll(name=titleTag)

        titleText = Utils.subTab(titleText)
        # 正文区域
        contentText = htmlContentParser.findAll(name=contentTag, attrs=contentAttrs)
        contentText = Utils.subTab(contentText)

        return titleText, contentText

    # 处理文档，去除标签
    @staticmethod
    def subTab(html):
        rc = re.compile("\<.*?\>")
        return rc.sub('', str(html))

    # 获取价格区间
    def getPriceFromText(htmlContentText):
        if (htmlContentText is None):
            return -1
        # 处理文档，去除标签
        contentText = Utils.subTab(htmlContentText)

        price = re.findall('\d+', contentText)
        price = list(map(int, price))
        if price:
            if len(price) >= 2:
                maxPrice = max(price)
                print(maxPrice)
                minPrice = min(price)
            else:
                maxPrice = minPrice = max(price)
        else:
            return -1
        return minPrice, maxPrice
