import matplotlib.pyplot as plt
from wordcloud import WordCloud
import PIL
import numpy as np

jmask = np.array(PIL.Image.open('jiangxl.png'))
wordcloud = WordCloud(font_path="微软vista雅黑.ttf", background_color="white", max_font_size=80,mask=jmask)

wordmap = {'亡灵': 144,'动画': 142, '梦想': 130,'音乐': 110, '哭': 100, '家庭': 100, '死亡': 96,  '文化': 76, '感动': 72, '记忆': 68, '亲情':68, 'coco': 66, '剧情' : 66, '迪士尼' : 62, '爱': 62, '泪': 58, '设定': 56, '动人' : 52, '煽情':50, '遗忘':48}
print(wordmap)
wordcloud = wordcloud.fit_words(wordmap)
wordcloud.to_file("j.jpg")
plt.imshow(wordcloud)
plt.show()