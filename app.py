import re
from urllib import request
from datetime import datetime
from bs4 import BeautifulSoup
# from flask import Flask
import requests
import json

import schedule
import time

#for regex
def get_hangul(inputString):
    hangul = re.compile('[^ ㄱ-ㅣ가-힣+]')
    res = hangul.sub('', inputString)
    return res


tmp_breakfast = []
tmp_lunch = []
tmp_dinner = []

#slack client
slackWebhookUrl = "<insert your webhook link>"

def send_slack_webhook(str_text):
    headers = {
        "Content-type": "application/json",
        "EnablePostIconOverride": "True"
        
    }

    data = {
        "text" : str_text,
        "icon_url": "https://user-images.githubusercontent.com/63194662/196212219-ffee04ed-8f66-47c9-b9a5-1f4af13c8b4b.png"
    }
    res = requests.post(slackWebhookUrl, headers=headers, data=json.dumps(data))

    if res.status_code == 200:
        return "ok"
    else:
        return "error"

####slack client done

def crawl_meal(dinner_or_lunch):
    now = datetime.now()

    date = str(now.date())
    target = request.urlopen("https://www.kaist.ac.kr/kr/html/campus/053001.html?dvs_cd=icc&stt_dt=" + date)

    soup = BeautifulSoup(target, "html.parser")
    res = soup.findAll('td')

    # 매주 일요일 12시 이후 이후에 다음주 식단 업데이트
    breakfast = res[0].contents
    lunch = res[1].contents[1].contents
    dinner = res[2].contents[1].contents

    # (N - 3)까지가 식단
    tmp_breakfast = []
    tmp_lunch = []
    tmp_dinner = []
    for i in range(0, len(breakfast) - 2, 2):
        menu = get_hangul(breakfast[i])
        if menu == '' or menu == ' ':
            continue
        
        tmp_breakfast.append(menu)
    for i in range(0, len(lunch) - 2, 2):
        tmp_lunch.append(get_hangul(lunch[i]))
    for i in range(0, len(dinner) - 2, 2):
        tmp_dinner.append(get_hangul(dinner[i]))
    
    #breakfast
    if dinner_or_lunch == "breakfast" and tmp_breakfast:
        res = "🍚오늘 아침 메뉴 입니다!🍜\n\n"
        meal = ','.join(tmp_breakfast)
        res += meal
        print(send_slack_webhook(res))
    #lunch
    elif dinner_or_lunch == "lunch" and tmp_lunch:
        res = "🍚오늘 점심 메뉴 입니다!🍜\n\n"
        meal = ','.join(tmp_lunch)
        res += meal
        print(send_slack_webhook(res))    
    #dinner
    elif dinner_or_lunch == "dinner" and tmp_dinner:
        res = "🍚오늘 저녁 메뉴 입니다!🍜\n\n"
        meal = ','.join(tmp_dinner)
        res += meal
        print(send_slack_webhook(res))

    return 'menu has been checked'


# scrappingOncePerDay("breakfast")
schedule.every().day.at("07:00").do(lambda: crawl_meal("breakfast"))
schedule.every().day.at("11:00").do(lambda: crawl_meal("lunch"))
schedule.every().day.at("17:00").do(lambda: crawl_meal("dinner"))

while True:
    schedule.run_pending()
    time.sleep(30)
