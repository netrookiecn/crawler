#coding:utf-8
#抓取中国法律援助网法援案例
from urllib import request
from bs4 import BeautifulSoup as bs

for num in range(2,11):
    resp = request.urlopen('http://www.chinalegalaid.gov.cn/China_legalaid/node_40882_'+str(num)+'.htm')
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data,'html.parser')
    tmp = soup.findAll('a','f14 blue001')
    print(tmp)
    f = open('lawCaseUrl','a',encoding='utf-8')
    for x in tmp:
        f.write(str(x)+"\n")

