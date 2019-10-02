#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import time
import datetime
import os

import requests
from bs4 import BeautifulSoup

import Config as Config
import Utils as Utils


class Main(object):
    # 初始化爬虫
    def __init__(self, config):
        self.config = config
        self.douban_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,en-GB;q=0.2,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'DNT': '1',
            'HOST': 'www.douban.com',
            'Cookie': self.config.douban_cookie
        }
    # 运行爬虫
    def run(self):
        result_file_name = 'results/result_' + str(spider.file_time)
        try:
            print('Connecting database...  打开数据库...')
            # 创建数据库sqlite
            conn = sqlite3.connect(result_file_name + '.sqlite')
            conn.text_factory = str
            cursor = conn.cursor()
            cursor.execute(
                'CREATE TABLE IF NOT EXISTS rent(id INTEGER PRIMARY KEY, title TEXT, url TEXT UNIQUE, itemtime timestamp, crawtime timestamp, source TEXT, keyword TEXT, note TEXT)')
            cursor.close()
            cursor = conn.cursor()

            # 读取配置文件
            search_list = self.config.key_search_word_list
            custom_black_list = self.config.custom_black_list
            start_time = Utils.Utils.getTimeFromStr(self.config.start_time)
            must_have_images = self.config.must_have_images
            must_have_qr_images = self.config.must_have_qr_images
            max_price = int(self.config.max_price)
            min_price = int(self.config.min_price)

            def urlList(page_number):
                num_in_url = str(page_number * 50)
                douban_url = ['https://www.douban.com/group/search?start=' + num_in_url +'&group=146409&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=523355&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=557646&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=383972&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=283855&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=76231&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=196844&cat=1013&sort=time&q=',
                              'https://www.douban.com/group/search?start=' + num_in_url +'&group=259227&cat=1013&sort=time&q=']
                return douban_url
            douban_url_name = [u'上海租房', u'上海招聘，租房', u'上海租房(2)', u'上海合租族_魔都租房', u'上海租房@浦东租房', \
                               u'上海租房---房子是租来的，生活不是', u'上海租房@长宁租房/徐汇/静安租房', u'上海租房（不良中介勿扰）']

            def crawl(i, douban_url, keyword, douban_headers):
                url_link = douban_url[i] + keyword
                print('url_link: ', url_link)
                # url获取到列表HTML源码
                r = requests.get(url_link, headers=douban_headers)
                if r.status_code == 200:
                    try:
                        if i == 0:
                            self.douban_headers['Cookie'] = r.cookies.items()[0][1]
                        soup = BeautifulSoup(r.text, "lxml")
                        paginator = soup.find_all(attrs={'class': 'paginator'})[0]

                        if (page_number != 0) and not paginator:
                            return False
                        else:
                            try:
                                table = soup.find_all(attrs={'class': 'olt'})[0]
                                tr_count_for_this_page = 0
                                spider.ok = True

                                for tr in table.find_all('tr'):
                                    td = tr.find_all('td')
                                    title_element = td[0].find_all('a')[0]
                                    title_text = title_element.get('title')
                                    # 忽略不符合条件的URL
                                    if Utils.Utils.isInBalckList(custom_black_list, title_text):
                                        continue
                                    time_text = td[1].get('title')

                                    if (page_number != 0) and (Utils.Utils.getTimeFromStr(time_text) < start_time):
                                        spider.ok = False
                                        break
                                    # 忽略指定日期之前的数据
                                    if Utils.Utils.getTimeFromStr(time_text) < start_time:
                                        continue
                                    link_text = title_element.get('href');

                                    print('link_text:',link_text)

                                    reply_count = td[2].find_all('span')[0].text
                                    tr_count_for_this_page += 1

                                    # 获取详情页网页源码
                                    htmlContent = Utils.Utils.getHtmlContentFromURL(link_text)
                                    if htmlContent.strip():
                                        # 价格判断
                                        if min_price > 0 or max_price > 0:
                                            # 获取正文文本和标题文本
                                            title_text_1, content_text_1 = Utils.Utils.getTitleAndContentTextFromURL(
                                                htmlContent)

                                            titleMinPrice,titleMaxPrice = Utils.Utils.getPriceFromText(title_text_1)
                                            contentMinPrice, contentMaxPrice = Utils.Utils.getPriceFromText(content_text_1)
                                            # 最小值
                                            minPrice = min(titleMinPrice,contentMinPrice)
                                            # 最大值
                                            maxPrice = max(titleMaxPrice,contentMaxPrice)
                                            # 获取标题和正文的文字内容
                                            # 期望值
                                            print('min_price:',min_price)
                                            # 真实值
                                            print('minPrice:', minPrice)
                                            # 期望值
                                            print('max_price:', max_price)
                                            # 真实值
                                            print('maxPrice:', maxPrice)
                                            if min_price <= minPrice and max_price<= maxPrice:
                                                # 不符合条件，跳过
                                                continue
                                        imglist = []
                                        # 是否必须有图片
                                        if int(must_have_images)!=0:
                                            imglist = Utils.Utils.getImageURLNotUserHeadFromURL(htmlContent)
                                            if len(imglist) <=0:
                                                continue
                                        # 是否必须有二维码
                                        if int(must_have_qr_images)!=0:
                                            if Utils.Utils.isNotExitQRImages(imglist) :
                                                continue
                                    try:
                                        cursor.execute(
                                            'INSERT INTO rent(id, title, url, itemtime, crawtime, source, keyword, note) VALUES(NULL, ?, ?, ?, ?, ?, ?, ?)',
                                            [title_text, link_text, Utils.Utils.getTimeFromStr(time_text),
                                             datetime.datetime.now(), keyword,
                                             douban_url_name[i], reply_count])
                                        print('add new data:', title_text, time_text, reply_count, link_text, keyword)
                                    except sqlite3.Error as e:
                                        print('data exists:', title_text, link_text, e) # URL should be unique
                            except Exception as e:
                                print('error match table:', e)
                    except Exception as e:
                        print('error match paginator:', e)
                        spider.ok = False
                        return False
                else:
                    print('request url error %s -status code: %s:' % (url_link, r.status_code))
                time.sleep(self.config.douban_sleep_time)
            print('The spider begins to work...  爬虫开始运行...')

            # 爬虫运行
            douban_url = urlList(0)
            for i in range(len(douban_url)):
                page_number = 0

                print('start i ->',i)
                for j in range(len(search_list)):
                    spider.ok = True
                    page_number = 0
                    keyword = search_list[j]
                    print('start i->j %s -> %s %s' %(i, j, keyword))
                    print('>>>>>>>>>> Search %s  %s ...' % (douban_url_name[i].encode('utf-8'), keyword))

                    while spider.ok:
                        print('i, j, page_number: ', i, j, page_number)

                        douban_url = urlList(page_number)
                        crawl(i, douban_url, keyword, self.douban_headers)
                        page_number += 1

            cursor.close()

            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rent ORDER BY itemtime DESC ,crawtime DESC')
            values = cursor.fetchall()
            # 将符合条件的，写入HTML文件
            print('The spider has finished working. Now begin to write the data in the result HTML.   爬虫运行结束。开始写入结果文件')

            file = open(result_file_name + '.html', 'w', encoding='utf-8')
            with file:
                file.write('''<html>
                    <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
                    <title>上海租房信息 | 豆瓣</title>
                    <link rel="stylesheet" type="text/css" href="../lib/resultPage.css">
                    </head>
                    <body>''')
                file.write('<h1>Shanghai Renting Information 上海租房信息 | </h1>')
                file.write('''
                    <a href="https://www.douban.com/" target="_black">
                    <img src="https://img3.doubanio.com/f/shire/8977fa054324c4c7f565447b003ebf75e9b4f9c6/pics/nav/lg_main@2x.png" alt="豆瓣icon"/>
                    </a>
                    ''')
                file.write('<table>')
                file.write(
                    '<tr><th>Index<br>索引</th><th>Title<br>标题</th><th>Posting Time<br>发帖时间</th><th>Scrawling Time<br>抓取时间</th><th>Keyword<br>关键字</th><th>Group<br>来源</th><th>Number of reply<br>回复数</th></tr>')

                for row in values:
                    file.writelines('<tr>')
                    for i in range(len(row)):
                        if i == 2:
                            i += 1
                            continue
                        file.write('<td class="column%s">' % str(i))
                        if i == 1:
                            file.write('<a href="' + str(row[2]) + '" target="_black">' + str(row[1]) + '</a>')
                            i += 1
                            continue
                        file.write(str(row[i]))
                        i += 1
                        file.write('</td>')
                    file.write('</tr>')
                file.write('</table>')
                file.write('<script type="text/javascript" src="../lib/resultPage.js"></script>')
                file.write('</body></html>')
            cursor.close()
        except Exception as e:
            print('Error:', e)
        finally:
            conn.commit()
            conn.close()
            print('==============================================')
            print('Finished writing the result HTML. Please open "' + result_file_name + '.html" to check the result')
            print('结果文件写入完毕。请打开"' + result_file_name + '.html"查看结果。')


# 爬虫配置导入
class Spider(object):
    def __init__(self):
        this_file_dir = os.path.split(os.path.realpath(__file__))[0]
        config_file_path = os.path.join(this_file_dir, 'config.ini')
        self.ok = True
        self.config = Config.Config(config_file_path)
        FILETIMEFORMAT = '%Y%m%d_%X'
        self.file_time = time.strftime(FILETIMEFORMAT, time.localtime()).replace(':', '')
        results_path = os.path.join(sys.path[0], 'results')
        if not os.path.isdir(results_path):
            os.makedirs(results_path)

    def run(self):
        # 开始执行爬虫与整理
        main = Main(self.config)
        main.run()



if __name__ == '__main__':
    spider = Spider()
    spider.run()

