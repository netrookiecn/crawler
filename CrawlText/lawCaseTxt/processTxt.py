#coding:utf-8
for i in range(0,500):
    f = open('txt/'+str(i)+'.txt','r',encoding='utf-8')
    new = open('txt1/'+str(i)+'.txt','a',encoding='utf-8')
    st = ''
    while 1:
        line = f.readline()
        if not line:
            break
        tmp = line.replace('<p>','').\
            replace('[<div id="ShowContent" style="font-size:14px;line-height:1.5;"><!--enpcontent-->','').\
            replace('<!--/enpcontent--></div>]','').\
            replace('</p>','').\
            replace('<center><img border="0" id="3740010" sourcedescription="编辑提供的本地文件" sourcename="本地文件" src="../../../images/attachement/jpg/site82/20170807/8c89a5754a871af25bb71f.jpg" style="WIDTH: 600px; HEIGHT: 337px" title=""/></center>',"").\
            replace('</div>','')
        st += tmp
    new.write(st)





