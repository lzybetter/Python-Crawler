import requests
from urllib.parse import urlencode
import json
import os
import glob
from bs4 import BeautifulSoup
import re
import PythonMagick
from PyPDF2 import PdfFileMerger
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def get_count():
    params = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    url = 'https://one-piece.cn/comic/'
    
    try:
        reponse = requests.get(url, headers = params)
        reponse.encoding = 'utf-8'
        soup = BeautifulSoup(reponse.text, 'lxml')
        if reponse.status_code == 200:
            title = soup.title.string
            print(title)
            title_re = '海贼王漫画全集【更新至(\d\d\d)话，第(\d\d\d)话预计(\d.*?)月(\d.*?)日更新】_连载中丨海贼小站'
            count, nextCount, month, day = re.findall(title_re, title)[0]
            id = str(soup.find_all(name='a'))
            id_re = '<a href="/post/(\d{5})/" target="_blank">第' + str(count) + '话 (.*?)</a>'
            id, title = re.findall(id_re, id)[0]
            return [count,id, title]
    except requests.ConnectionError:
        return [None, None]

# def get_nowCate(count):
#     nowCate = '1-50'
#     hundred = count//100
#     tens = count % 100
#     if tens <= 50:
#         nowCate = str(hundred*100 + 1) + '-' + str(hundred*100 + 50)
#     else:
#         nowCate = str(hundred * 100 + 51) + '-' + str((hundred + 1)*100)
#     return nowCate


def get_image(count, id, title):

    url = 'https://one-piece.cn/post/' + str(id)
    params = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Origin':'https://one-piece.cn/comic/'
    }

    try:
        reponse = requests.get(url, headers = params)
        if reponse.status_code == 200:
            i = 0
            reponse.encoding = 'utf-8'
            soup = BeautifulSoup(reponse.text, 'lxml')
            imgUrls = str(soup.find_all(name='img'))
            imgUrls_re = ' <img alt="海贼王 第' + str(count) + '话 ' + title +'" src="(.*?)"/>'
            imgUrls = re.findall(imgUrls_re, imgUrls)
            if not os.path.exists(title):
                os.makedirs(title)
            for imgUrl in imgUrls:
                ex = imgUrl.split('.')[-1]
                try:
                    imgReponse = requests.get(imgUrl)
                    #if i + 1 < len(item):
                    if i < 10 :
                        file_path = '{0}/{1}.{2}'.format(title,'0' + str(i), ex)
                    else:
                        file_path = '{0}/{1}.{2}'.format(title, str(i), ex)
                    #else:
                        #file_path = '{0}/{1}.{2}'.format(title,str(i),'jpg')
                    i = i + 1
                    if not os.path.exists(file_path):
                        with open(file_path, 'wb') as f:
                            if imgReponse.content:
                                f.write(imgReponse.content)
                except requests.ConnectionError:
                    print('Wrong')  
            return ex
        return None
    except requests.ConnectionError:
        print('Wrong')
        return None

def get_fileName(title,fileType):

    return sorted(glob.glob(title + "/*." + fileType))

def conver2pdf(imgNames,title):
    
    for imgName in imgNames:
        img = PythonMagick.Image(imgName)
        img.write(imgName.split('.')[0] + '.pdf')
    pdfNames = get_fileName(title,'pdf')
    pdf_merger = PdfFileMerger()
    i = 0
    for pdfName in pdfNames:
        if not i == 0:
            pdf_merger.merge(i+1,pdfName)
        else:
            pdf_merger.append(pdfNames[i])
        i = i + 1
    pdf_merger.write(title + '/' + title + '.pdf')

def sendToKindle(title):

    fromAdress = "lzy178171973@163.com"
    toAdress = "lzydeppytyddab-9080@kindle.cn"
    smtp_address = "smtp.163.com"
    password = "AcZ4aJoKQqVgSFj"
    try:
        msg = MIMEMultipart()
        msg['From'] = fromAdress
        msg['To'] = toAdress
        msg['Subject'] = title

        #msg_text = "one piece!"
        #print(type(title))
        #msg.attach(msg_text)

        pdf = open(title + '/' + title + '.pdf','rb')
        msg_attach = MIMEApplication(pdf.read())
        pdf.close()
            #print(open(title + '/' + title + '.pdf','rb').read())
        msg_attach.add_header('Content-Disposition','attachment', filename = title + '.pdf')
        msg.attach(msg_attach)

        server = smtplib.SMTP(smtp_address,25)
        server.login(fromAdress,password)
        server.sendmail(fromAdress, toAdress, msg.as_string())
        server.quit()
        print('Sending success')

    except Exception as e:
        print('Sending Wrong', e)

def reminder(title,count):

    masterKey = 'e7jTsWj1ciUupzkuTIMBogacAwMh7N8zo2coUUo0cWK'
    url = 'https://maker.ifttt.com/trigger/one_piece/with/key/' + masterKey
    data = {'value1':count,'value2':title,'value3': None}
    requests.post(url,data=data)

def main():
    [count, id, title] = get_count()
    print(count, id, title)
    # get_image(count, id, title)
    path = os.getcwd() + '/count.txt'
    print(path)
    if os.path.exists(path):
        with open(path, 'r') as f:
            count_now = f.read()
    else:
        count_now = 0
    if not int(count_now) == int(count):
        with open(path, 'w') as f:
            f.write(count)
        ex = get_image(count, id, title)
        imgNames = get_fileName(title, ex)
        conver2pdf(imgNames, title)
        sendToKindle(title)
        reminder(title, count)
    else:
        exit()
    

if __name__ == '__main__':
    main()
