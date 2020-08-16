import json
import requests
import time
import pyttsx3
import cn2an

CITYCODE = ['101020500001'] #城市code，可以在中国气象网的url中找到

def getWeather(CITYCODE):

    baseUrl = 'http://d1.weather.com.cn/dingzhi/'
    t = str(time.time()).split('.')[0]
    url = baseUrl + CITYCODE + '.html?_=' + t
    header = {
        'Referer': 'http://www.weather.com.cn/weather/' + CITYCODE + '.shtml', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'
    }

    res = requests.get(url, headers = header)
    res = res.text.encode(res.encoding)
    res = res.decode('utf-8')

    res = res.split('var')[1]
    res = res.split('=')[-1].strip(';')
    res_json = json.loads(res)

    weatherinfo = res_json['weatherinfo']
    city = weatherinfo['cityname']
    temp1 = int(weatherinfo['temp'].strip('℃'))
    temp2 = int(weatherinfo['tempn'].strip('℃'))
    top = temp1 if temp1 > temp2 else temp2
    down = temp2 if temp1 > temp2 else temp1
    top = cn2an.an2cn(str(top)) + '度'
    down = cn2an.an2cn(str(down)) + '度'
    wind = weatherinfo['wd']
    ws = weatherinfo['ws']
    if '<' in ws:
        ws = ws.replace('<','小于')
    if '-' in ws:
        ws = ws.replace('-', '到')
    weather = weatherinfo['weather']

    today = '今天{}{}, 最高温度{},最低温度{},{},{}'.format(city, weather, top, down, wind, ws)
    return today


def speak(today):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-50)
    engine.setProperty('voice', 'zh')


    engine.say(today)
    if '雨' in today:
        engine.say('今天有雨，出门记得带伞')
    engine.runAndWait()
    engine.stop()

if __name__ == "__main__":
    
    for city in CITYCODE:
        today = getWeather(city)
        print(today)
        speak(today)

