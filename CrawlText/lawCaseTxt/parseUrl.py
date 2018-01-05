#coding:utf-8
import re

ttt = re.match('www', 'www.runwwwowwwobwww.comwww')
print(ttt.group())


pattern = 'content\/\d-\d\/\d\/content_\d.htm\?node=40882'
file = open('lawCaseUrl', 'r+', encoding='utf-8')
string = file.read()
result = re.match(r'content/[0-9]-[0-9]/[0-9]/content_[0-9]\.htm\?node=40882', string,flags=0)
print(result)
if result:
    resultList = result.group()
    print(resultList)
