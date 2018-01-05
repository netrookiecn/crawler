from CrawlText import addJieba
from wordcloud import WordCloud
import numpy as np
import PIL
def CommentWordTerm(filePath):
    f = open(filePath, 'r', encoding='utf-8')
    wordDict = {}
    while 1:
        line = f.readline()
        if not line:
            break
        afterSeg = addJieba.parseWithStopwords(line)
        for word in afterSeg:
            if word == ' ':
                continue
            if word in wordDict:
                wordDict[word] = int(wordDict.get(word)) + 1
            else:
                wordDict[word] = 1
    #dic = sorted(wordDict.items(),key=lambda item:item[1],reverse=True)
    return wordDict
#jmask = np.array(PIL.Image.open('jiangxl.png'))
jiang = CommentWordTerm('qianren3.txt')
print(jiang)
wordcloud = WordCloud(font_path="Semibold.ttf", background_color="black", max_font_size=80)
wordcloud.fit_words(jiang)
wordcloud.to_file("qianren3.jpg")

