#-*-coding:utf8;-*-


#import site
import urllib2
import urllib
import cookielib
import sys
import os
import re
from bs4 import BeautifulSoup

print "载入中......"

username='';
password='';
defaultdownloadpath=sys.path[0]+'/';
cookiefilename=sys.path[0]+'/cookie.txt';
user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0";
header={'User-Agent':user_agent,
'referer':'http://e-hentai.org'};
#报错函数
def HTTPError (error):
  if hasattr(error, 'code'):    
    print '出现了HTTP错误！'    
    print '错误代码: ', error.code
  elif hasattr(error, 'reason'):    
    print '出现了URL错误'
    print '原因:', error.reason
#登录函数
def Login (username,password):
  cookie=cookielib.MozillaCookieJar(cookiefilename);
  opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie));
  urllib2.install_opener(opener);
  url="https://forums.e-hentai.org/index.php";
  print "请输入用户名"
  username=raw_input();
  print "请输入密码"
  password=raw_input();
  postdata={'UserName':username,
'PassWord':password,
'referer':'http://e-hentai.org',
'b':'',
'bt':'',
'CookieDate':'1'};
  postdata=urllib.urlencode(postdata);
  getdata={'act':'Login',
'CODE':'01'
};
  getdata=urllib.urlencode(getdata);
  req=urllib2.Request(url+'?'+getdata,postdata,header);
  try:
    html=urllib2.urlopen(req);
    html=urllib2.urlopen("http://exhentai.org");
  except urllib2.URLError,err:
    HTTPError(err);
  #跟踪是否成功登录
  for item in cookie:
    if (item.name=='ipb_pass_hash'):
      cookie.save(ignore_discard=True, ignore_expires=True);
      header['referer']='http://exhentai.org';
      return True;
  return False;
#从文件读取Cookie
def LoadCookie ():
  cookie = cookielib.MozillaCookieJar();
  try:
    cookie.load(cookiefilename,ignore_discard=True, ignore_expires=True);
  except:
    return False;
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie));
  #判断是否成功读取
  for item in cookie:
    if (item.name=='ipb_pass_hash'):
      urllib2.install_opener(opener);
      header['referer']='http://exhentai.org';
      return True;
  return False;
#下载图片函数
def DownloadImage (imagelink,downloadpath):
  if (imagelink=="" or imagelink==None):
    return False;
  if (downloadpath[len(downloadpath)-1]!='/'):
    downloadpath+='/';
  arr=imagelink.split('/');
  imagefilename=arr[len(arr)-1];
  '''''''''
  if (os.path.isfile(imagefilename)==True):
    print "存在同名文件，继续覆盖请输入y，否则跳过:";
    tempin=raw_input();
    if (tempin!='y'):
      return True;
  '''''''''
  req=urllib2.Request(imagelink,None,header);
  try:
    image=urllib2.urlopen(req);
  except urllib2.URLError,err:
    HTTPError(err);
    return False;
  imagefile=open(downloadpath+imagefilename,'wb');
  imagefile.write(image.read());
  return True
#抓取页面图片下载并返回下一页链接函数
def DownloadPageImage (pagelink,filepath):
  if (pagelink=="" or pagelink==None):
    return None;
  req=urllib2.Request (pagelink,None,header);
  try:
    page=urllib2.urlopen(req);
  except urllib2.URLError,err:
    HTTPError(err);
    return None;
  document=BeautifulSoup(page,"html.parser");
  imgtag=document.find('img',id='img');
  nexttag=document.find('a',id='next');
  DownloadImage(imgtag['src'],filepath);
  if (nexttag['href']==pagelink):
    return None;
  return nexttag['href'];
#下载所有图片函数
def DownloadAll (indexlink):
  req=urllib2.Request(indexlink,None,header);
  try:
    page=urllib2.urlopen(req);
  except urllib2.URLError,err:
    HTTPError (err);
    return False;
  document=BeautifulSoup(page,"html.parser");
  title=document.find('h1',id='gn').string;
  title=title.split('\n')[0];
  title=re.sub(r'\\|\[|\]|\/|\?|\*|<|>|\||`|\|\~|"|\.|:',"",title);
  if (indexlink[len(indexlink)-1]!='/'):
    indexlink+='/';
  indexlink+=' ';
  #print title;
  if (len(title)>254):
    temp=indexlink.split('/');
    title=temp[len(temp)-2];
  if (not os.path.exists(defaultdownloadpath+title)):
    os.makedirs(defaultdownloadpath+title);
  else:
    invalue="";
    print "目标文件夹已经存在，是否继续?(y/n)";
    while (invalue!='y'):
      invalue=raw_input();
      if (invalue=='n'):
        print "用户停止.";
        return True;
      elif (invalue!='y'):
        print "输入错误！请重新输入"
  downloadpath=defaultdownloadpath+title+'/';
  temp=document.find_all('td',class_='gdt2');
  pagecount=temp[len(temp)-2].string.split(' ')[0];
  detaillink=document.find('div',class_='gdtm').a['href'];
  count=1;
  while detaillink!=None:
    print "正在下载第",count,"张图片，总",pagecount,"张图片"
    detaillink=DownloadPageImage(detaillink,downloadpath);
    count+=1;
  return True;
#主程序
#获取Cookie
if (LoadCookie()):
  print "读取Cookie成功";
else:
  print "读取Cookie失败，尝试登录";
  if (Login (username,password)):
    print "登录成功！";
  else:
    print "登录失败！";
url="";
print "请输入你要下载的详情页连接，例如:http://exhentai.org/g/xxxxxxx:"
url=raw_input();
print "请选择保存目录，不输入默认保存到本脚本所在目录:";
path=raw_input();
if (path!=""):
  defaultdownloadpath=path;
DownloadAll (url);
print "完成!"