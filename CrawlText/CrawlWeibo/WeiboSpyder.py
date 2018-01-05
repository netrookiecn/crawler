import requests
from lxml import etree

weiboid = open('微博用户id.txt','r',encoding='utf-8')
for line in weiboid.readlines():
    user_id = int(line)
    cookie = {"Cookie":"d76e41231f7648d097fb05b43738f9e7; SUB=_2A253QDm7DeRhGeNM7VoZ9SnIyD-IHXVUy0fzrDV6PUJbkdBeLUGkkW1NThAtCk0eQ7kcV6Ut3Ogf-x4e7ny_Ort1; SUHB=0QSJ_LQdT4ir4n; SCF=AifkKiWrhLxPRTL3jtkzObGInYZFT1X2HZwkeoJ9BPUmK8BiDjtTj_gkuFxbevpaD_JCjBPw_ut287tw8QHKoAE.; SSOLoginState=1514424812"}
    url = 'https://weibo.cn/u/%d?filter=1&page=1'%user_id
    html = requests.get(url,cookies=cookie).content
    selector = etree.HTML(html)
    pageNum = (int)(selector.xpath('//input[@name="mp"]')[0].attrib['value'])

    result =""
    urllist_set = set()
    word_count = 1
    image_count = 1

    print('begin')

    for page in range(1,pageNum+1):
        url = 'https://weibo.cn/u/%d?filter=1&page=%d'%(user_id,page)
        lxml = requests.get(url,cookies=cookie).content

        selector = etree.HTML(lxml)
        content = selector.xpath('//span[@class="ctt"]')
        for each in content:
            text = each.xpath('string(.)')
            if(word_count >=1):
                text = "%d :"%(word_count-3) + text + "\n"
            else:
                text = text + "\n"
            result = result + text
            word_count += 1

    resultTxt = open('weiboData/'+str(user_id)+'.txt','a',encoding='utf-8')
    resultTxt.write(result)
    print('end')