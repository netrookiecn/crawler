from urllib import request
from bs4 import BeautifulSoup as bs

file = open('allurl.txt','r+')
list = []
while 1:
    line = file.readline()
    if not line:
        break
    list.append(line)

print(list.__len__())
tmp = []
for i in range(len(list)):
    resp = request.urlopen(list[i])
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')

    condiv = soup.find('div',{'id':'ShowContent'})
    conres = condiv.get_text()
    #print(conres)

        #tmp = soup.findAll('div', id='ShowContent')

        #print(tmp)
    xxtmp = open('txt/' + str(i) + ".txt", 'a', encoding='utf-8')
    xxtmp.write(str(conres))
    print('第' + str(i) + '个了。。。')