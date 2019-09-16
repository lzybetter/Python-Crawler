import requests
from urllib.parse import urlencode
import json
import os
import glob
import PythonMagick
from PyPDF2 import PdfFileMerger
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
#请按需求更改下面的内容
#发送邮箱地址，请提前添加到kindle的信任邮箱列表中
fromAdress = "YOUR MAIL"
#接收邮箱地址
toAdress = "YOUR MAIL"
#使用的邮箱服务器，这里是163邮箱
smtp_address = "smtp.163.com"
#密码，请注意是登陆第三方客户端的独立密码，不是邮箱的登陆密码
password = "YOUR PASSWORD"
#IFTTT的key
masterKey = 'YOUR MASTERKEY'
#用于记录最新话集数，请更改为您的地址
count_dir = 'YOUR DIR'

def get_count():
    params = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
    }

    url = 'https://prod-api.ishuhui.com/ver/b8826558/anime/detail?id=1&type=comics&.json'
    
    try:
        reponse = requests.get(url, headers = params)
        if reponse.status_code == 200:
            count = str(reponse.json()['data']['comicsIndexes']['1']['maxNum'])
            nowCate = get_nowCate(int(count))
            print(nowCate)
            id = reponse.json()['data']['comicsIndexes']['1']['nums'][nowCate][count][0]['id']
            return [count,id]
    except requests.ConnectionError:
        return [None, None]

def get_nowCate(count):
    nowCate = '1-50'
    hundred = count//100
    tens = count % 100
    if tens <= 50:
        nowCate = str(hundred*100 + 1) + '-' + str(hundred*100 + 50)
    else:
        nowCate = str(hundred * 100 + 51) + '-' + str((hundred + 1)*100)
    return nowCate


def get_image(id):

    url = 'https://prod-api.ishuhui.com/comics/detail?id=' + str(id)
    try:
        reponse = requests.get(url)
        if reponse.status_code == 200:
            title = reponse.json()['data']['title']
            print(title)
            i = 0
            if not os.path.exists(title):
                os.makedirs(title)
            for item in reponse.json()['data']['contentImg']:
                imgUrl = item['url']
                try:
                    imgReponse = requests.get(imgUrl)
                    #if i + 1 < len(item):
                    if i < 10 :
                        file_path = '{0}/{1}.{2}'.format(title,'0' + str(i),'png')
                    else:
                        file_path = '{0}/{1}.{2}'.format(title, str(i),'png')
                    #else:
                        #file_path = '{0}/{1}.{2}'.format(title,str(i),'jpg')
                    i = i + 1
                    if not os.path.exists(file_path):
                        with open(file_path,'wb') as f:
                            if imgReponse.content:
                                f.write(imgReponse.content)
                except requests.ConnectionError:
                    print('Wrong')  
            return title
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
        print('Sending Wrong')

def reminder(title,count):

    
    url = 'https://maker.ifttt.com/trigger/one_piece/with/key/' + masterKey
    data = {'value1':count,'value2':title,'value3': None}
    requests.post(url,data=data)

def main():
    [count,id] = get_count()
    print(count,id)
    get_image(id)
    dir = count_dir + '/count.txt'
    if os.path.exists(dir):
        with open(dir,'r') as f:
            count_now = f.read()
    else:
        count_now = 0
    if not int(count_now) == int(count):
        with open(dir,'w') as f:
            f.write(count)
        title = get_image(id)
        imgNames = get_fileName(title,'png')
        conver2pdf(imgNames,title)
        sendToKindle(title)
        reminder(title,count)
    else:
        exit()
    

if __name__ == '__main__':
    main()
