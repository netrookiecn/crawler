#coding:utf-8
import warnings
warnings.filterwarnings("ignore")
from urllib import request
from bs4 import BeautifulSoup as bs

#分析网页函数
def getNowPlayingMovie_list():
    resp = request.urlopen('https://movie.douban.com/nowplaying/shanghai/')
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')
    nowplaying_movie = soup.find_all('div', id='nowplaying')
    nowplaying_movie_list = nowplaying_movie[0].find_all('li', class_='list-item')
    nowplaying_list = []
    for item in nowplaying_movie_list:
        nowplaying_dict = {}
        nowplaying_dict['id'] = item['data-subject']
        for tag_img_item in item.find_all('img'):
            nowplaying_dict['name'] = tag_img_item['alt']
            nowplaying_list.append(nowplaying_dict)
    return nowplaying_list

#爬取评论函数
def getCommentsById(movieId, pageNum):
    eachCommentList = [];
    if pageNum>0:
         start = (pageNum-1) * 20
    else:
        return False
    requrl = 'https://movie.douban.com/subject/' + movieId + '/comments' +'?' +'start=' + str(start) + '&limit=20'
    print(requrl)
    resp = request.urlopen(requrl)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data, 'html.parser')
    comment_div_lits = soup.find_all('div', class_='comment')
    for item in comment_div_lits:
        if item.find_all('p')[0].string is not None:
            eachCommentList.append(item.find_all('p')[0].string)
    return eachCommentList

def main():
    #循环获取第一个电影的前10页评论
    commentList = []
    NowPlayingMovie_list = getNowPlayingMovie_list()
    for i in range(10):
        num = i + 1
        commentList_temp = getCommentsById(NowPlayingMovie_list[0]['id'], num)
        commentList.append(commentList_temp)

    #将列表中的数据转换为字符串
    comments = ''
    f = open("qianren3.txt", 'a', encoding='utf-8')
    for k in range(len(commentList)):
        comments = comments + (str(commentList[k])).strip()
        print((str(commentList[k])).strip()+"\n")
        f.write((str(commentList[k])).strip()+"\n")
#主函数
main()
