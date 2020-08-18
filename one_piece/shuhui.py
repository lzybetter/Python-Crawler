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

    url = 'https://manhua.fzdm.com/2/'
    
    try:
        reponse = requests.get(url, headers = params)
        reponse.encoding = 'utf-8'
        if reponse.status_code == 200:
            id_re = '<meta property="og:novel:latest_chapter_name" content="海贼王(.*)话">'
            count = re.findall(id_re, reponse.text)[0]
            return count
    except requests.ConnectionError:
        return None


def get_image(count, title):

    url = 'https://manhua.fzdm.com/2/' + str(count)

    params = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    }
    imgs = []
    id = 0
    try:
        reponse = requests.get(url, headers = params)
        if reponse.status_code == 200:
            base = r'var mhurl="(.*).jpg";var'
            imgs.append(re.search(base, reponse.text).group(1) + '.jpg')
            while '最后一页了' not in reponse.text:
                id = id + 1
                url = 'https://manhua.fzdm.com/2/987/index_{}.html'.format(id)
                reponse = requests.get(url, headers = params)
                imgs.append(re.search(base, reponse.text).group(1) + '.jpg')
            if not os.path.exists(title):
                os.makedirs(title)
            i = 1
            for img in imgs:
                ex = img.split('.')[-1]
                imgUrl = 'https://p5.manhuapan.com/' + img
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
        pdf = open(title + '/' + title + '.pdf','rb')
        msg_attach = MIMEApplication(pdf.read())
        pdf.close()
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
    count = get_count()
    title = '海贼王{}话'.format(count)
    print(title)
    path = os.getcwd() + '/count.txt'
    if os.path.exists(path):
        with open(path, 'r') as f:
            count_now = f.read()
    else:
        count_now = 0
    if not int(count_now) == int(count):
        with open(path, 'w') as f:
            f.write(count)
        ex = get_image(count, title)
        imgNames = get_fileName(title, ex)
        conver2pdf(imgNames, title)
        sendToKindle(title)
        reminder(title, count)
    else:
        exit()
    

if __name__ == '__main__':
    main()
