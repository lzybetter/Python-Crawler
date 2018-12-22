import requests
import time
import json

#请按需要修改下面的内容
#出发城市
departureInformations = [["SHA","2","上海"]]
#到达城市
acityInformations = [["DLC","6","大连"],["SHE","451","沈阳"]]
#出发时间
dates=["2019-01-31","2019-02-01","2019-02-02"]
#理想价格
enoughPrice = 800
#IFTTT的key
masterKey = 'YOUR MASTERKEY'
#IFTTT触发事件名
eventName = 'YOUR EVENTNAME'

def get_routeList(date,acityInformation,departureInformation):

    acity = acityInformation[0]
    acityId = acityInformation[1]
    acityName = acityInformation[2]
    dcity = departureInformation[0]
    dcityid = departureInformation[1]
    dcityname = departureInformation[2]

    url='http://flights.ctrip.com/itinerary/api/12808/products'

    payloadData = {
        "classType" : "ALL",
        "flightWay" : "Oneway",
        "hasBaby" : "false",
        "hasChild" : "false",
        "searchIndex" : "1",
        "airportParams": [{"acity":acity,"acityid":acityId,"acityname":acityName,"date":date,"dcity":dcity,"dcityid":dcityid,"dcityname":dcityname}]
    }
    dumpJsonData = json.dumps(payloadData)
    payloadHeader = {
        "Referer":"http://flights.ctrip.com/itinerary/oneway/sha-dlc?date=" + date,
        "Origin":"http://flights.ctrip.com",
        "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        'Content-Type': 'application/json'
    }

    res = requests.post(url, data=dumpJsonData, headers=payloadHeader)
    routeList = res.json()['data']['routeList']
    time.sleep(10)

    return routeList

def get_routeLists(dates, acityInformations,departureInformations):

    routeLists = []

    for date in dates:
        for acityInformation in acityInformations:
            for departureInformation in departureInformations:
                routeList = get_routeList(date, acityInformation, departureInformation)
                routeLists.extend(routeList)
    return routeLists

def getAirlineDetail(leg):
        information = {}
        airlineInformation = leg['flight']['airlineName'] + leg['flight']['flightNumber']
        information['airlineInformation'] = airlineInformation
        departureAirport = leg['flight']['departureAirportInfo']['airportName'] + leg['flight']['departureAirportInfo']['terminal']['name'] + '航站楼'
        information['departureAirport'] = departureAirport
        departureDate = leg['flight']['departureDate'].split(' ')[0]
        information['departureDate'] = departureDate
        departureTime = leg['flight']['departureDate'].split(' ')[1]
        information['departureTime'] = departureTime
        arrivalTime = leg['flight']['arrivalDate'].split(' ')[1]
        information['arrivalTime'] = arrivalTime
        mealType = leg['flight']['mealType']
        isMeal = '有餐食'
        if mealType == "None":
            isMeal = '无餐食'
        else :
            isMeal = '有餐食'
        information['isMeal'] = isMeal
        punctualityRate = leg['flight']['punctualityRate']
        information['punctualityRate'] = punctualityRate
        return information

def isCheapeEnough(routeLists):

    for routeList in routeLists:
        legs = routeList['legs']
        for leg in legs:
            if(leg['characteristic']['lowestPrice'] == None):
                continue
            lowestPrice = int(leg['characteristic']['lowestPrice'])
            if lowestPrice < int(enoughPrice):
                value1 = str(lowestPrice) + "元"
                information = getAirlineDetail(leg)
                value2 = information['airlineInformation'] + "，" + "出发机场为:" + information['departureAirport']
                value3 = "出发日期:" + information['departureDate'] + "，" + "起飞时间:" + information['departureTime'] + "，" +"到达时间:" + information['arrivalTime'] \
                + "，" + "餐食情况:" + information['isMeal'] + "，" + "准点率:" + information['punctualityRate']
                url = 'https://maker.ifttt.com/trigger/' + eventName +'/with/key/' + masterKey
                data = {'value1':value1,'value2':value2,'value3': value3}
                requests.post(url,data=data)





def main():
    routeLists = get_routeLists(dates,acityInformations,departureInformations)
    isCheapeEnough(routeLists)

if __name__ == '__main__':
    main()
