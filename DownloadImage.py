# coding: utf8
from Utils import Utils as Utils

imagesURLs = Utils.getImageURLFromURL(url="https://www.douban.com/group/topic/152890720/")
flag = Utils.isNotExitQRImages(imagesURLs)



print(flag)
