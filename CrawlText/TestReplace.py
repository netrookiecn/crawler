#coding = utf-8
str = 'this is a string'
str2 = str.replace('string','').\
    replace('is','jiang')
print(str2)


weiboData = open('CrawlWeibo/微博用户id.txt','r',encoding='utf-8')
for line in weiboData.readlines():
    tmp  = int(line)
    print(tmp)