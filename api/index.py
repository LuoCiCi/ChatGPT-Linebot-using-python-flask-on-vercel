from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from api.chatgpt import ChatGPT
import os
from datetime import datetime, timedelta
import requests
import random
import pytz
#import yfinance as yf

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFAULT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

# 計算出前一個10分倍數的時間以及前前一個10分倍數的時間以及前前前一個10分倍數的時間
def get_prev10_4():
    # 設定台灣時間
    tz = pytz.timezone('Asia/Taipei')
    # 取得當前系統日期和時間
    now = datetime.now(tz)

    # 取出當前時間的分鐘數
    minute = now.minute

    # 計算前一個10分倍數的時間
    prev_minute = (minute // 10) * 10  # 取最接近的 10 分倍數
    prev_time = now.replace(minute=prev_minute, second=0, microsecond=0)

    # 如果當前時間已經是整10分倍數，則需要再往前推一個10分倍數
    if minute % 10 == 0:
        prev_time = prev_time - timedelta(minutes=10)

    # 計算前前一個10分倍數的時間
    prev_prev_time = prev_time - timedelta(minutes=10)

    # 計算前前前一個10分倍數的時間
    prev_prev_prev_time = prev_prev_time - timedelta(minutes=10)

    # 計算前前前一個10分倍數的時間
    prev_prev_prev_prev_time = prev_prev_prev_time - timedelta(minutes=10)

    # 回傳結果
    return prev_time, prev_prev_time, prev_prev_prev_time, prev_prev_prev_prev_time

# 計算出前一個10分倍數的時間以及前前一個10分倍數的時間
def get_prev10_prevprev10():
    # 設定台灣時間
    tz = pytz.timezone('Asia/Taipei')
    # 取得當前系統日期和時間
    now = datetime.now(tz)

    # 取出當前時間的分鐘數
    minute = now.minute

    # 計算前一個10分倍數的時間
    prev_minute = (minute // 10) * 10  # 取最接近的 10 分倍數
    prev_time = now.replace(minute=prev_minute, second=0, microsecond=0)

    # 如果當前時間已經是整10分倍數，則需要再往前推一個10分倍數
    if minute % 10 == 0:
        prev_time = prev_time - timedelta(minutes=10)

    # 計算前前一個10分倍數的時間
    prev_prev_time = prev_time - timedelta(minutes=10)

    # 回傳結果
    return prev_time, prev_prev_time
    
# 計算出前一個整點或半點的時間以及前前一個整點或半點的時間
def get_prev30_prevprev30():
    # 設定台灣時間
    tz = pytz.timezone('Asia/Taipei')
    # 取得當前系統日期和時間
    now = datetime.now(tz)

    # 計算前一個整點或半點時間
    minutes = now.minute
    if minutes >= 30:
        prev_time = now.replace(minute=30, second=0, microsecond=0)
        prev_prev_time = now.replace(minute=0, second=0, microsecond=0)
    else:
        prev_time = now.replace(minute=0, second=0, microsecond=0)
        prev_prev_time = (now - timedelta(hours=1)).replace(minute=30, second=0, microsecond=0)

    # 回傳結果
    return prev_time, prev_prev_time

# 計算出前一個整點的時間以及前前一個整點的時間
def get_prev00_prevprev00():
    # 設定台灣時間
    tz = pytz.timezone('Asia/Taipei')
    # 取得當前系統日期和時間
    now = datetime.now(tz)

    # 計算前一個整點的00分時間
    if now.minute >= 30:
        prev_time = now.replace(minute=0, second=0, microsecond=0)
    else:
        prev_time = (now - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    # 計算前前一個整點的00分時間
    prev_prev_time = prev_time - timedelta(hours=1)

    # 回傳結果
    return prev_time, prev_prev_time
    
# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 確認 URL 是否有效
def check_image_url_exists(url):
    try:
        # 發送 HEAD 請求以確認 URL 是否有效
        response = requests.head(url)
        
        # 檢查 HTTP 狀態碼
        if response.status_code == 200:
            return True  # URL 存在
        else:
            return False  # URL 不存在或無法存取
    except requests.RequestException as e:
        # 捕捉各種異常情況（例如網絡錯誤，無法連線等）
        print(f"Error: {e}")
        return False

# 雨量圖
def get_rain_pic():
    prev, prev_ = get_prev30_prevprev30()

    # 將 prev_time 轉換成日期字串
    prev_date_str = prev.strftime('%Y-%m-%d')
    prev_time_str = prev.strftime('%H%M')

    prev_prev_date_str = prev_.strftime('%Y-%m-%d')
    prev_prev_time_str = prev_.strftime('%H%M')

    prev_url = "https://www.cwa.gov.tw/Data/rainfall/" + prev_date_str + "_" + prev_time_str + ".QZJ8.jpg"
    prev_prev_url = "https://www.cwa.gov.tw/Data/rainfall/" + prev_prev_date_str + "_" + prev_prev_time_str + ".QZJ8.jpg"
    
    return prev_url, prev_prev_url

# 溫度圖
def get_temperature_pic():
    prev, prev_ = get_prev00_prevprev00()

    # 將 prev_time 轉換成日期字串
    prev_date_str = prev.strftime('%Y-%m-%d')
    prev_time_str = prev.strftime('%H%M')

    prev_prev_date_str = prev_.strftime('%Y-%m-%d')
    prev_prev_time_str = prev_.strftime('%H%M')

    prev_url = "https://www.cwa.gov.tw/Data/temperature/" + prev_date_str + "_" + prev_time_str + ".GTP8.jpg"
    prev_prev_url = "https://www.cwa.gov.tw/Data/temperature/" + prev_prev_date_str + "_" + prev_prev_time_str + ".GTP8.jpg"
    
    return prev_url, prev_prev_url

# 紫外線圖
def get_uvrays_pic():
    prev, prev_ = get_prev10_prevprev10()

    # 將 prev_time 轉換成日期字串
    prev_datetime_str = prev.strftime('%Y%m%d%H%M')
    prev_minute_str = prev.strftime('%M')

    prev_prev_datetime_str = prev_.strftime('%Y%m%d%H%M')
    prev_prev_minute_str = prev_.strftime('%M')        

    prev_url = "https://www.cwa.gov.tw/Data/UVI/UVI_CWB.png?t=" + prev_datetime_str + "-" + prev_minute_str[0] + ".GTP8.jpg"
    prev_prev_url = "https://www.cwa.gov.tw/Data/UVI/UVI_CWB.png?t=" + prev_prev_datetime_str + "-" + prev_prev_minute_str[0] + ".GTP8.jpg"
    
    return prev_url, prev_prev_url

# 衛星圖
def get_satellite_pic():
    prev, prev_, prev_3, prev_4 = get_prev10_4()

    # 將 prev_time 轉換成日期字串
    prev_date_str = prev.strftime('%Y-%m-%d')
    prev_time_str = prev.strftime('%H-%M')

    prev_prev_date_str = prev_.strftime('%Y-%m-%d')
    prev_prev_time_str = prev_.strftime('%H-%M')

    prev_3_date_str = prev_3.strftime('%Y-%m-%d')
    prev_3_time_str = prev_3.strftime('%H-%M')

    prev_4_date_str = prev_4.strftime('%Y-%m-%d')
    prev_4_time_str = prev_4.strftime('%H-%M')

    prev_url = "https://www.cwa.gov.tw/Data/satellite/LCC_IR1_CR_2750/LCC_IR1_CR_2750-" + prev_date_str + "-" + prev_time_str + ".jpg"
    prev_prev_url = "https://www.cwa.gov.tw/Data/satellite/LCC_IR1_CR_2750/LCC_IR1_CR_2750-" + prev_prev_date_str + "-" + prev_prev_time_str + ".jpg"
    prev_3_url = "https://www.cwa.gov.tw/Data/satellite/LCC_IR1_CR_2750/LCC_IR1_CR_2750-" + prev_3_date_str + "-" + prev_3_time_str + ".jpg"
    prev_4_url = "https://www.cwa.gov.tw/Data/satellite/LCC_IR1_CR_2750/LCC_IR1_CR_2750-" + prev_4_date_str + "-" + prev_4_time_str + ".jpg"
    
    return prev_url, prev_prev_url, prev_3_url, prev_4_url

# 雷達圖
def get_radar_pic():
    prev, prev_, prev_3, prev_4 = get_prev10_4()

    # 將 prev_time 轉換成日期字串
    prev_date_str = prev.strftime('%Y%m%d')
    prev_time_str = prev.strftime('%H%M')

    prev_prev_date_str = prev_.strftime('%Y%m%d')
    prev_prev_time_str = prev_.strftime('%H%M')

    prev_3_date_str = prev_3.strftime('%Y%m%d')
    prev_3_time_str = prev_3.strftime('%H%M')

    prev_4_date_str = prev_4.strftime('%Y%m%d')
    prev_4_time_str = prev_4.strftime('%H%M')

    prev_url = "https://www.cwa.gov.tw/Data/radar/CV1_3600_" + prev_date_str + prev_time_str + ".png"
    prev_prev_url = "https://www.cwa.gov.tw/Data/radar/CV1_3600_" + prev_prev_date_str + prev_prev_time_str + ".png"
    prev_3_url = "https://www.cwa.gov.tw/Data/radar/CV1_3600_" + prev_3_date_str + prev_3_time_str + ".png"
    prev_4_url = "https://www.cwa.gov.tw/Data/radar/CV1_3600_" + prev_4_date_str + prev_4_time_str + ".png"
    
    return prev_url, prev_prev_url, prev_3_url, prev_4_url
        
@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "雨量" or event.message.text == "濕度":
        working_status = True

        prev_url, prev_prev_url = get_rain_pic()

        if (check_image_url_exists(prev_url)):
            # url = prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_url, preview_image_url=prev_url)
                ]
            )
        elif (check_image_url_exists(prev_prev_url)):
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_prev_url, preview_image_url=prev_prev_url)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得雨量圖"))
        return

    if event.message.text == "溫度" or event.message.text == "氣溫":
        working_status = True

        prev_url, prev_prev_url = get_temperature_pic()

        if (check_image_url_exists(prev_url)):
            # url = prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_url, preview_image_url=prev_url)
                ]
            )
        elif (check_image_url_exists(prev_prev_url)):
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_prev_url, preview_image_url=prev_prev_url)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得溫度圖"))
        return

    if event.message.text == "紫外線":
        working_status = True

        prev_url, prev_prev_url = get_uvrays_pic()

        if (check_image_url_exists(prev_url)):
            # url = prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_url, preview_image_url=prev_url)
                ]
            )
        elif (check_image_url_exists(prev_prev_url)):
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_prev_url, preview_image_url=prev_prev_url)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得紫外線圖"))
        return

    if event.message.text == "衛星" or event.message.text == "衛星雲圖":
        working_status = True
        
        prev_url, prev_prev_url, prev_3_url, prev_4_url = get_satellite_pic()

        if (check_image_url_exists(prev_url)):
            # url = prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_url, preview_image_url=prev_url)
                ]
            )
        elif (check_image_url_exists(prev_prev_url)):
            # url = prev_prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_prev_url, preview_image_url=prev_prev_url)
                ]
            )
        elif (check_image_url_exists(prev_3_url)):
            # url = prev_3_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_3_url, preview_image_url=prev_3_url)
                ]
            )
        elif (check_image_url_exists(prev_4_url)):
            # url = prev_4_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_4_url, preview_image_url=prev_4_url)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得衛星雲圖"))
        return

    if event.message.text == "雷達":
        working_status = True
        
        prev_url, prev_prev_url, prev_3_url, prev_4_url = get_radar_pic()

        if (check_image_url_exists(prev_url)):
            # url = prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_url, preview_image_url=prev_url)
                ]
            )
        elif (check_image_url_exists(prev_prev_url)):
            # url = prev_prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_prev_url, preview_image_url=prev_prev_url)
                ]
            )
        elif (check_image_url_exists(prev_3_url)):
            # url = prev_3_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_3_url, preview_image_url=prev_3_url)
                ]
            )
        elif (check_image_url_exists(prev_4_url)):
            # url = prev_4_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_4_url, preview_image_url=prev_4_url)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得雷達圖"))
        return

    if event.message.text == "颱風":
        working_status = True
        typhoon_url = "https://www.cwa.gov.tw/V8/C/P/Typhoon/TY_WARN.html"

        if (check_image_url_exists(typhoon_url)):
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{typhoon_url}"))
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得颱風消息"))
        return          
    
    if event.message.text == "天氣" or event.message.text == "氣象" or event.message.text == "所有天氣圖":
        messages = []  # 存放所有訊息的列表

        # 取雨量圖
        rain_err = None
        rain_prev_url, rain_prev_prev_url = get_rain_pic()
        if (check_image_url_exists(rain_prev_url)):
            rain_url = rain_prev_url
        elif (check_image_url_exists(rain_prev_prev_url)):
            rain_url = rain_prev_prev_url
        else:
            rain_err = "無法取得雨量圖"

        # 取溫度圖
        temp_err = None
        temp_prev_url, temp_prev_prev_url = get_temperature_pic()
        if (check_image_url_exists(temp_prev_url)):
            temp_url = temp_prev_url
        elif (check_image_url_exists(temp_prev_prev_url)):
            temp_url = temp_prev_prev_url
        else:
            temp_err = "無法取得溫度圖"

        # 取紫外線圖
        uvrays_err = None
        uvrays_prev_url, uvrays_prev_prev_url = get_uvrays_pic()
        if (check_image_url_exists(uvrays_prev_url)):
            uvrays_url = uvrays_prev_url
        elif (check_image_url_exists(uvrays_prev_prev_url)):
            uvrays_url = uvrays_prev_prev_url
        else:
            uvrays_err = "無法取得紫外線圖"

        # 取衛星圖
        sat_err = None
        sat_prev_url, sat_prev_prev_url, sat_prev_3_url, sat_prev_4_url = get_satellite_pic()
        if (check_image_url_exists(sat_prev_url)):
            sat_url = sat_prev_url
        elif (check_image_url_exists(sat_prev_prev_url)):
            sat_url = sat_prev_prev_url
        elif (check_image_url_exists(sat_prev_3_url)):
            sat_url = sat_prev_3_url
        elif (check_image_url_exists(sat_prev_4_url)):
            sat_url = sat_prev_4_url
        else:
            sat_err = "無法取得衛星雲圖圖"

        # 取雷達圖
        radar_err = None
        radar_prev_url, radar_prev_prev_url, radar_prev_3_url, radar_prev_4_url = get_radar_pic()
        if (check_image_url_exists(radar_prev_url)):
            radar_url = radar_prev_url
        elif (check_image_url_exists(radar_prev_prev_url)):
            radar_url = radar_prev_prev_url
        elif (check_image_url_exists(radar_prev_3_url)):
            radar_url = radar_prev_3_url
        elif (check_image_url_exists(radar_prev_4_url)):
            radar_url = radar_prev_4_url
        else:
            radar_err = "無法取得雷達圖"

        # 錯誤訊息
        if rain_err is not None:
            messages.append(TextSendMessage(text=f"{rain_err}"))
        else:
            messages.append(ImageSendMessage(original_content_url=rain_url, preview_image_url=rain_url))
        
        if temp_err:
            messages.append(TextSendMessage(text=f"{temp_err}"))
        else:
            messages.append(ImageSendMessage(original_content_url=temp_url, preview_image_url=temp_url))

        if uvrays_err:
            messages.append(TextSendMessage(text=f"{uvrays_err}"))
        else:
            messages.append(ImageSendMessage(original_content_url=uvrays_url, preview_image_url=uvrays_url))

        if sat_err:
            messages.append(TextSendMessage(text=f"{sat_err}"))
        else:
            messages.append(ImageSendMessage(original_content_url=sat_url, preview_image_url=sat_url))

        if radar_err:
            messages.append(TextSendMessage(text=f"{radar_err}"))
        else:
            messages.append(ImageSendMessage(original_content_url=radar_url, preview_image_url=radar_url))

        # 最後一次性回傳所有訊息
        line_bot_api.reply_message(event.reply_token, messages)
        return
            

    # 暫時使用line設定功能，將此隱藏
    # if event.message.text == "選單" or event.message.text == "功能" or event.message.text == "menu":
    #     working_status = True
    #     menu = "目前功能如下：\n[1] 雨量=天氣=濕度\n[2] 溫度=氣溫\n[3] 衛星=衛星雲圖\n[4] 紫外線\n[5] 急了\n[6] 錢錢=錢吶=錢啊\n[7] 多多=多吶=多啊\n[8] 錢錢多多=錢多\n[9] 抽\n[10] 抽奶=抽大奶"
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=f"{menu}"))
    #     return
        
    if event.message.text == "說話":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我可以說話囉，歡迎來跟我互動 ^_^ "))
        return

    if event.message.text == "扯" or event.message.text == "好扯" or event.message.text == "超扯":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你最扯~"))
        return

    if event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="你才閉嘴，就你最吵"))
        return

    if event.message.text == "早安" or event.message.text == "早":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="大家早安，今天又是美好的一天~"))
        return

    if event.message.text == "晚安":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="各位晚安，夢裡見囉~"))
        return

    if event.message.text == "下班":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我也可以下班了嗎？"))
        return

    if event.message.text == "抽女友" or event.message.text == "抽老婆":
        working_status = False
        ts = [
            "你沒有!!",
            "你作夢!",
            "離你太遙遠了，別想了",
            "總是想太多~"
        ]
        # 隨機選擇一個文字
        random_ts_url = random.choice(ts)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{random_ts_url}"))
        return

    if event.message.text == "急了":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        image_urls = [
            "https://memeprod.sgp1.digitaloceanspaces.com/user-wtf/1693521527021.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQx9BFj90LO-rK98keHK6wAkEiah_McWWdVeQ&s",
            "https://stickershop.line-scdn.net/stickershop/v1/product/25440282/LINEStorePC/main.png?v=1",
            "https://p3-pc-sign.douyinpic.com/tos-cn-i-0813/bafe6270a73a4d28bd793abc57c11ec4~tplv-dy-aweme-images:q75.webp?biz_tag=aweme_images&from=327834062&s=PackSourceEnum_SEARCH&sc=image&se=false&x-expires=1729706400&x-signature=vZwXDWxIV2bYqm1TelPGbIxWLqQ%3D",
            "https://stickershop.line-scdn.net/stickershop/v1/product/25428386/LINEStorePC/main.png?v=1"
        ]

        # 進行圖片URL檢查
        while attempts < max_attempts:
            # 隨機選擇一個圖片 URL
            random_image_url = random.choice(image_urls)
            
            # 檢查圖片是否存在
            if check_image_url_exists(random_image_url):
                # 如果圖片存在，回傳訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
                    ]
                )
                break  # 找到圖片後退出迴圈
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法找到對應的圖片，請稍後再試。")
            )
        return

        # # 回傳訊息
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     [
        #         ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
        #     ]
        # )
        # return

    if event.message.text == "抽":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        image_urls_1 = [
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBOlQL3xJsiB0rdZ07j0tUmJUdrLgZdC29HQ&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTZksY8fVOYn57iAGHhJxokGgdtGc3mugmk4-QmLe_vLyS-7Jgna_sya8PYzFW5QUCW70Q&usqp=CAU",
            "https://p5.itc.cn/images01/20230705/986a790ba34a4fb194422611cb684eda.jpeg",
            "https://p9.itc.cn/q_70/images03/20230904/f4fe0b05119b4ab8b0075b4c41c46ce7.jpeg",
            "https://thumb.photo-ac.com/cb/cb52df139e3d6b14fdc28b7dc38fbb6c_t.jpeg",
            "https://i.pinimg.com/736x/c1/50/9a/c1509a675399f9a81b2722e793c55c7e.jpg",
            "https://png.pngtree.com/thumb_back/fh260/background/20210903/pngtree-beautiful-girl-with-long-hair-image_790986.jpg",
            "https://png.pngtree.com/thumb_back/fh260/background/20230424/pngtree-female-asian-woman-posing-with-hands-clasped-korean-beauty-image_2502163.jpg",
            "https://images.pexels.com/photos/3866556/pexels-photo-3866556.png?cs=srgb&dl=pexels-clarango-3866556.jpg&fm=jpg",
            "https://i.pinimg.com/originals/d8/49/fe/d849feca8b1e452f840cd45e1e31b163.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_ZbEiVdlzz-LVsiudO626mKI3iN9o2Lu37A&s",
            "https://watermark.lovepik.com/photo/20211207/large/lovepik-charming-red-lips-beauty-makeup-hands-covering-picture_501537693.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ-YRmizhoGV2jW1m0DJePQo5Kw6f8qYyCJbA&s",
            "https://thumb.photo-ac.com/14/14886183fe43fdff6afbce9a742b5e60_t.jpeg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR2yV--oN6ZLT4UAGvSs5aCbrrSADVSaNaUug&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEMq-GKWGod1OV1EjDV5OUVnn0VZ-NWsFJyg&s",
            "https://img2.imagemore.com.tw/imagemore_dir/comp/bn1504/bji04280063.jpg",
            "https://thumb.photo-ac.com/4d/4d78cf21bc9d02efdd012e8ae1f4efee_t.jpeg",
            "https://en.pimg.jp/106/598/334/1/106598334.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTTrcKOP-UfwqGp85dACa_kBzHR-Qw-8h-99A&s",
            "https://upload.wikimedia.org/wikipedia/commons/1/1f/20240911_Lisa_MTV_VMAs_06_%28cropped%29.png",
            "https://hips.hearstapps.com/hmg-prod/images/271508239-713379336294330-3130045077370608684-n-640614eb1701a.jpg?crop=1xw:1xh;center,top&resize=980:*",
            "https://media.nownews.com/nn_media/thumbnail/2023/05/1683468042856-67eec361d1d74dda99f998189eb5096e-800x450.jpg?unShow=false",
            "https://hips.hearstapps.com/hmg-prod/images/254548076-625165548500065-8965182106882304688-n-1636619991.jpg?crop=1xw:1xh;center,top&resize=980:*",
            "https://i.pinimg.com/736x/66/c6/df/66c6df8128d654db74ffd1496d4fb3bf.jpg",
            "https://today-obs.line-scdn.net/0hmUYOwfdbMnpkNiXWpihNLVxgPgtXUChzRlR0SBVka0JLGnQvUAdhGURjZVZADnZ4RFl1H0Jkbx0dACEvWg/w644",
            "https://media.nownews.com/nn_media/thumbnail/2022/04/1649131065438-58adaef36d3d455096b168c087908bf5-800x534.jpg?unShow=false",
            "https://s.yimg.com/zp/MerchandiseImages/28DA6596E9-SP-7775353.jpg",
            "https://dynamic.zacdn.com/Xgdy0k_T5AnP6XBxcbfeH2V5Cmo=/filters:quality(70):format(webp)/https://static-tw.zacdn.com/p/lycka-9583-0408471-2.jpg",
            "https://img.cloudimg.in/uploads/shops/7094/products/b0/b02c2e7c86d787f1138c05f32a7e14c7.jpg",
            "https://down-tw.img.susercontent.com/file/215b170d984ed3f48837e7336d3dfab0",
            "https://s.yimg.com/zp/MerchandiseImages/983BEFE4F1-SP-7781092.jpg",
            "https://api.harpersbazaar.com.hk/var/site/storage/images/_aliases/img_640_w/fashion/girl-next-door-fashion/node_191249/2628795-1-chi-HK/_1.jpg",
            "https://api.harpersbazaar.com.hk/var/site/storage/images/_aliases/img_640_w/fashion/girl-next-door-fashion/node_191248/2628787-1-chi-HK/_1.jpg",
            "https://api.harpersbazaar.com.hk/var/site/storage/images/_aliases/img_640_w/fashion/girl-next-door-fashion/node_191250/2628803-1-chi-HK/_1.jpg",
            "https://obs.line-scdn.net/0htuo9wA1RK1pSQANnU3JUDWsWJythJD5cPDgxOXBAJm95dnANaXZiIHIQdDhjIGkLPTpsaHVFcz4odT5ZaSY",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTw9h5m6bRDSVpkP8C4zIOpqLusnVB8tca6Nw&s",
            "https://img.ltn.com.tw/Upload/ent/page/800/2021/05/24/phpUOn8z7.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSIHTgsn5HbW1H6UuN4AB32DN4tI3mWAaupHA&s",
            "https://cdn.ftvnews.com.tw/manasystem/FileData/News/7476b1eb-3f66-4c50-b186-0fc4ab52bdb0.jpg",
            "https://sw.cool3c.com/article/2018/32151241-adf9-4d94-a9be-c24b5597d209.jpg?fit=max&w=1400&q=80",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTJpAg8wQDXbbZNkAZ9fsbwr6BNTQUwQfhvTg&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGchDhH0FLs53qrVu_VDFAQ80tM-H_Bq2EBg&s",
            "https://gw.alicdn.com/imgextra/i1/66032415/O1CN01zhQHU01Ti7U2FRA9d_!!66032415.jpg_Q75.jpg_.webp",
            "https://images.chinatimes.com/newsphoto/2019-05-09/656/20190509004041.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/%E5%90%B3%E5%87%BD%E5%B3%AE.jpg/640px-%E5%90%B3%E5%87%BD%E5%B3%AE.jpg",
            "https://img.ltn.com.tw/Upload/style/bphoto/normal/2020/06/09/20200609-90916-15.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTUJddb7UyHriUBwVyFRuoAbeo-Z34kunXWEw&s",
            "https://attach.setn.com/newsimages/2021/11/23/3417554-PH.jpg",
            "https://cdn2.ettoday.net/images/6174/6174968.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRzS7XpSVx0jUw-5UdgFvd2a4-aMraSuoYXGw&s",
            "https://upload.wikimedia.org/wikipedia/commons/1/13/LAN202301_%28cropped%29.jpg",
            "https://modelmodel.com.tw/mdimg/20190826220110_7Q9GAg5HW8gk.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTB6uye2-GrBp9-svkQvvdi1-8ZO9W08vmJZg&s",
            "https://media.vogue.com.tw/photos/6617b306e7da7d48983fb9bc/2:3/w_2560%2Cc_limit/599d0d09cf8e47d674f5c87aebf16762.jpeg",
            "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/240807_IU_at_Estee_Lauder_Photo_Call.png/800px-240807_IU_at_Estee_Lauder_Photo_Call.png",
            "https://www.mtv.com.tw/uploads/files/14194/conversions/1%E5%8D%97%E9%9F%93%E6%A8%82%E5%A3%87%E5%B9%B4%E5%BA%A6%E7%9B%9B%E4%BA%8BMMAIU%E7%A2%BA%E5%AE%9A%E5%87%BA%E5%B8%AD-xl.jpg",
            "https://cdn-www.cw.com.tw/article/202206/article-62b828626ffbe.jpg",
            "https://cdn2.ettoday.net/images/7845/d7845319.jpg",
            "https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2020/03/30/20200330-110019_U17218_M602112_6203.jpg?itok=5uNGlzuu",
            "https://cc.tvbs.com.tw/img/upload/2024/09/20/20240920125905-3e3e23ed.jpg",
            "https://news.agentm.tw/wp-content/uploads/326634-750x422.jpg",
            "https://obs.line-scdn.net/0hfBvTKJXtOW1LLSre5AJGOnN7NRx4SyNkaRxxAmctYlU2AX87JExqDmx9NEFvSS06axghDTsrZgo1GH08cw/w644",
            "https://media.nownews.com/nn_media/thumbnail/2023/06/1687418756134-e51115403f6c44eab41228a99473be56-800x450.jpg?unShow=false",
            "https://static.ctwant.com/images/content/10/60210/48e0146163f958082ae0c7903c103645.jpg",
            "https://media.vogue.com.tw/photos/63651fc449bac8ec3af84118/2:3/w_2560%2Cc_limit/288993936_580506253445260_541891399734496910_n.jpeg",
            "https://im.marieclaire.com.tw/m800c533h100b0/assets/mc/202007/5F23C2421896A1596179010.jpeg",
            "https://attach.setn.com/newsimages/2023/07/26/4255502-PH.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEPBywmA39tptDq3a7cNG4u3O0utt18FVIYg&s",
            "https://image1.gamme.com.tw/news2/2010/81/34/qpuYoJ2XlaaWqQ.jpg",
            "https://images.chinatimes.com/newsphoto/2018-06-23/656/20180623002206.jpg",
            "https://cdn2.ettoday.net/images/5512/5512050.jpg",
            "https://img2.focustech.com.tw/wswed/knowledge/uploads/2015/08/2022022210192062.jpg",
            "https://images.chinatimes.com/newsphoto/2022-12-07/656/20221207002701.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTzolZ_BFSbZdm7m-CN2Ij8KikM4Rt7M9hafQ&s",
            "https://api.cosmopolitan.com.hk/var/site/storage/images/_aliases/img_767_959/4/0/0/1/3601004-4-chi-HK/420.jpg",
            "https://images-tw.girlstyle.com/wp-content/uploads/2023/03/7716b064.jpg?auto=format&w=1053",
            "https://4gtvimg.4gtv.tv/4gtv-Image/Production/Article/2022052611000006/202205261156481402.jpg",
            "https://today-obs.line-scdn.net/0h3UaKDcKSbHpcMn6ceAcTLWRkYAtvVHZzflNxS3xiNkxzHiN-aAc_GXAyMVZ5ViMkfARzFXgwYUolV3x8Zw/w644",
            "https://media.vogue.com.tw/photos/5f71b27cd34b04d5b4a7f1da/master/w_1600%2Cc_limit/FA20_CKU_APAC_AD_W_PF%2520FLEX%2520PUSH%2520UP_1_FINAL.jpg",
            "https://photo.518.com.tw/selfmedia/articles/1954/167048254259173.jpeg",
            "https://api.cosmopolitan.com.hk/var/site/storage/images/3/2/2/3/7323223-1-chi-HK/8.jpg",
            "https://today-obs.line-scdn.net/0hxJVAUw7SJ2VrOA95GUxYMlFuJApYVDRmDw52ZihWeVESDjM1AF1qC0g6eAAVDWA7BQthBU89PFQVW2ZjUF5q/w644",
            "https://intl.rakuten-static.com/b/tw/assets/magazine/img/women/2017/061301/1.jpg",
            "https://today-obs.line-scdn.net/0hxuco7K3VJ1peFg5VyaZYDWRAJDVtejRZOiB2WR14eW4kIWkEMiRuNH1DeW91dWAEN3BsNXwVPGshdmVeYiVu/w644",
            "https://cdn.hk01.com/di/media/images/dw/20210430/464754444941135872403172.jpeg/HUYrHGY9ZENqwjVYL54aOEQmBYfwwlN9EfOFLBHzhSw?v=w1920",
            "https://s.yimg.com/ny/api/res/1.2/11MBnVhdaDbnZRDjzrnFHg--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MDtoPTgyNw--/https://media.zenfs.com/en/ftvn.com.tw/a4d2c2cefe5ad6f5a96559df03577fe8",
            "https://today-obs.line-scdn.net/0hm2Y71hs8Mh1kTiU3x7hNSlwYPmxXKCgURi51fhVPPH9MYiFCCHxhfkBJPzFBKXdLRHstfxQcbClJeidCUA/w644",
            "https://cdn.ftvnews.com.tw/summernotefiles/News/4caca4e4-48b2-42fb-8f41-3a7b94af3c77.jpg",
            "https://cdn.bella.tw/index_image/Dbun59UIUk1lcsMZQzdI1IqKoa4RRaHv288ziMlX.jpeg",
            "https://api.cosmopolitan.com.hk/var/site/storage/images/_aliases/img_767_959/9/4/4/8/7608449-1-chi-HK/kv-v.jpg",
            "https://rimage.gnst.jp/livejapan.com/public/article/detail/a/00/04/a0004852/img/zh-tw/a0004852_main.jpg",
            "https://cdn2.ettoday.net/images/1985/d1985418.jpg",
            "https://images-my.girlstyle.com/wp-content/uploads/2022/08/a8f88d39.jpg?auto=format&w=1053",
            "https://cdn2.ettoday.net/images/5320/5320485.jpg",
            "https://images-tw.girlstyle.com/wp-content/uploads/2022/09/598eb5ba.jpg?auto=format&w=1053",
            "https://assets.juksy.com/files/articles/59310/61ba276f9479b.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ0nM2UeOrWFWM_wUvM8fHrC1FSuZOUsc2c9A&s",
            "https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2022/02/22/20220222-113855_U20102_M746087_42f0.jpg?itok=feLP6_jB",
            "https://obs.line-scdn.net/0hKo59rqF_FEAIQDx_jkRrFzEWGDE7JAFGZjgJcXoSS3AneU9FZ3ZdOihJGHg5eVRBNDpYJn5HHSUjI1pDMy8",
            "https://megapx-assets.dcard.tw/images/1797d523-7b7c-4516-aa86-0d2f6c5427a7/640.jpeg",
            "https://media.nownews.com/nn_media/thumbnail/2023/05/1684735679192-49effc5c389d4585b6028e8264b8b8eb-800x600.png?unShow=false",
            "https://api.cosmopolitan.com.hk/var/site/storage/images/love/eight-characteristics-of-cute-girl/20171127004843/3241487-1-chi-HK/20171127004843.jpg",
            "https://cdn.beautyexchange.com.hk/wp-content/uploads/2022/04/25193732/WhatsApp-Image-2022-04-25-at-7.35.22-PM.jpeg",
            "https://picture.smartweb.tw/3601/prod/title_204330.jpg?1032",
            "https://lovepicture.nosdn.127.net/-1646481156464263096?imageView&thumbnail=560x0&quality=85",
            "https://imgs.699pic.com/images/600/624/902.jpg!detail.v1",
            "https://img.chilling.tw/images/author/Ivy/0707005.jpg",
            "https://image.cache.storm.mg/styles/smg-800x533-fp/s3/media/image/2018/06/05/20180605-061621_U3927_M419757_1c11.png?itok=fg6OkDtW",
            "https://cdn.bella.tw/index_image/VjehePRYUksdh6Us9FM3Srh98DIdYizwkBlljkQw.jpeg",
            "https://images.chinatimes.com/newsphoto/2023-01-27/656/20230127001685.jpg",
            "https://www.10500.com.tw/wp-content/uploads/__www_10500_com_tw_uploads_tadgallery_2020_03_25_734_309c9c653ff8e49ffa5ba6a8c46c7ba2_jpg.jpg",
            "https://cdn.bella.tw/images/Macariopei/0522/girl0.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/a/a7/%E7%9C%8B%E5%AE%8C%E4%B8%AD%E9%A4%90%E5%8E%85%E5%A5%BD%E6%84%9Fup_%E5%BE%88%E5%8F%AF%E7%88%B1%E7%9A%84%E5%B0%8F%E5%A5%B3%E7%94%9F_%28%E5%91%A8%E5%86%AC%E9%9B%A8_%E5%BE%AE%E5%8D%9A%E7%94%B5%E5%BD%B1%E4%B9%8B%E5%A4%9C%29_%285%29_%28cropped%29.jpg",
            "https://img.6tu.com/2023/11/20231101064831358.jpg",
            "https://www.10500.com.tw/wp-content/uploads/2021/12/432_191_1logo16-683x1024.jpg",
            "https://www.eton.com.tw/img/index/banner%20(16).jpg",
            "https://i-photo7.com/image/data/11A/269-min.jpg",
            "https://mhstyle.tw/wp-content/uploads/2023/01/P-8-3.jpg",
            "https://liliwed.tw/wp-content/uploads/2020/08/%E7%B6%B2%E9%A0%81%E7%89%88-5.jpg",
            "https://img.ltn.com.tw/Upload/ent/page/800/2019/02/15/phpWyNntS.jpg",
            "https://www.eton.com.tw/img/personal/Hsieh/personal%20(2).jpg",
            "https://imgs.699pic.com/images/501/631/888.jpg!list1x.v2",
            "https://megapx-assets.dcard.tw/images/6d67a98a-9985-447d-b1d0-0bc215281354/1280.jpeg",
            "https://hellohellophoto.com.tw/wp-content/uploads/2022/09/HEN_2410-2.jpg",
            "https://cdn.hk01.com/di/media/images/dw/20230820/769991776164384768762843.jpeg/aJV4MZMp1BhWlsHpJyfXZgkfXnj8HNmmZ8-nU2fPp1M?v=w1920",
            "https://images.chinatimes.com/newsphoto/2023-04-26/656/20230426004923_20230426183745.jpg",
            "https://image1.gamme.com.tw/news2/2021/56/21/pZmSpqCYmKOYqA.jpg",
            "https://shinphotos.com/wp-content/uploads/2020-11-05-180724-78.jpg",
            "https://s3.ap-southeast-1.amazonaws.com/ohmostudio/pet%20photo-11jpg.jpg",
            "https://express.adobe.com/page/UwSBgPnnvIDdx/images/e6f8b815-2235-4fbb-aeca-e69f8750b4c2.jpg?asset_id=1ff25959-63a6-409b-b769-809a0eb31905&img_etag=1dea946a7c6dd345f1e5b55c5ffbaf29&size=1024",
            "https://watermark.lovepik.com/photo/20211209/large/lovepik-beautiful-woman-with-fashion-makeup-picture_501695280.jpg",
            "https://i-photo7.com/image/data/11A/270-min.jpg",
            "https://i-photo7.com/image/data/11A/269-min.jpg",
            "https://i1.kknews.cc/_zvD1mWIYS_QpOAjKYXPFiNE6kDbUhIzd5Iep5U/0.jpg",
            "https://lh6.googleusercontent.com/proxy/PNZjK5kw_Xfsamu0etWi1eCPQubc0igjLPq5LLM_kmE0_MRUAB42HD7xmGeFWRuxzqpt07PJwvyxoGGQK6uQio1z1d5RKzG_4jcZQnJ9ow_nf1UD_OI",
            "https://i1.kknews.cc/EvSLxcrB_ANowxAjloZFvLIdqjQmXY6v3Dxx4LY/0.jpg",
            "https://media.gq.com.tw/photos/5dbc6b4a801fc800083f56c4/master/w_1600%2Cc_limit/2017062062377685.jpg",
            "https://i.getjetso.com/month_1501/20150129_76aa6a1b831aff162d82p8dMgv.jpg?name=%E7%BE%8E%E8%85%BF%7EDudu+Wu%E5%AF%AB%E7%9C%9F",
            "https://media.gq.com.tw/photos/5dbc68e7801fc800083f538e/3:2/w_1600%2Cc_limit/2017050958686269.jpg",
            "https://img.win3000.com/m00/5f/ce/51f30a11ea329d3eb4b07a06fe16cbf6.jpg",
            "https://img.ttshow.tw/images/author/ron/FotoJet6556.jpg",
            "https://today-obs.line-scdn.net/0h4efrlPi9a0pbC3tjX_cUHWNdZztobXFDeT8leXxZMX0kJy4eMG84KSkMNGYlOioYez0iKH1cMilyaS0cMA/w644",
            "https://cdn2.ettoday.net/images/6862/d6862322.jpg",
            "https://imgs.699pic.com/images/501/427/671.jpg!list1x.v2"
        ]
        
   
        # 進行圖片URL檢查
        while attempts < max_attempts:    
            
            random_number_image_urls_2 = random.randint(1,60)
            image_urls_2 = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/Drawing/Drawing%20({random_number_image_urls_2}).jpg"
            random_value = random.random()        
            if random_value < 0.08:  # 8% 機率
                
                random_image_url = image_urls_2
                
                if check_image_url_exists(image_urls_2):
                # 如果圖片存在，回傳訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            TextSendMessage(f"恭喜抽中彩蛋編號: {random_number_image_urls_2}"),
                            ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
                        ]
                    )
                    break  # 找到圖片後退出迴圈
            else:
                
                random_image_url = random.choice(image_urls_1)
                
                if check_image_url_exists(random_image_url):
                # 如果圖片存在，回傳訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
                        ]
                    )
                    break  # 找到圖片後退出迴圈        
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法找到對應的圖片，請稍後再試。")
            )
        return

        # # 回傳訊息
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     [
        #         ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
        #     ]
        # )
        # return

    if event.message.text == "抽奶" or event.message.text == "抽大奶":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        image_urls = [
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTZksY8fVOYn57iAGHhJxokGgdtGc3mugmk4-QmLe_vLyS-7Jgna_sya8PYzFW5QUCW70Q&usqp=CAU",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBOlQL3xJsiB0rdZ07j0tUmJUdrLgZdC29HQ&s",
            "https://p9.itc.cn/q_70/images03/20230904/f4fe0b05119b4ab8b0075b4c41c46ce7.jpeg",
            "https://thumb.photo-ac.com/cb/cb52df139e3d6b14fdc28b7dc38fbb6c_t.jpeg",
            "https://st.depositphotos.com/3546173/5116/i/950/depositphotos_51163333-stock-photo-beautiful-slim-body-of-woman.jpg",
            "https://media.nownews.com/nn_media/thumbnail/2022/04/1649131065438-58adaef36d3d455096b168c087908bf5-800x534.jpg?unShow=false",
            "https://s.yimg.com/zp/MerchandiseImages/28DA6596E9-SP-7775353.jpg",
            "https://dynamic.zacdn.com/Xgdy0k_T5AnP6XBxcbfeH2V5Cmo=/filters:quality(70):format(webp)/https://static-tw.zacdn.com/p/lycka-9583-0408471-2.jpg",
            "https://i1.momoshop.com.tw/1712812024/goodsimg/0009/457/451/9457451_R_m.webp",
            "https://img.cloudimg.in/uploads/shops/7094/products/b0/b02c2e7c86d787f1138c05f32a7e14c7.jpg",
            "https://s.yimg.com/zp/MerchandiseImages/983BEFE4F1-SP-7781092.jpg",
            "https://img.alicdn.com/imgextra/i3/190954632/O1CN01vxrocX1k5VMB7ranX_!!190954632.jpg",
            "https://gw.alicdn.com/imgextra/i3/2532877733/O1CN01xz4xuX26zlbYAJj0S_!!0-item_pic.jpg_Q75.jpg_.webp",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgHMKS3ryrpSrZvnHWfpiyBEmnF1Oy1Tw3IQ&s",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSGchDhH0FLs53qrVu_VDFAQ80tM-H_Bq2EBg&s",
            "https://media.zenfs.com/en/nownews.com/b34d3759f2b1382430bfa18cac22ced9",
            "https://dailyview.tw/_next/image?url=https%3A%2F%2Fdvblobcdnjp.azureedge.net%2FContent%2FUpload%2FPopular%2FImages%2F2019-02%2F9265b389-0aca-4318-9f2f-226397be36e9_m.jpg&w=1920&q=75",
            "https://img.ltn.com.tw/Upload/ent/page/800/2023/10/27/phpa06t7k.jpg",
            "https://attach.setn.com/newsimages/2020/09/04/2755061-PH.jpg",
            "https://cbu01.alicdn.com/img/ibank/O1CN01TEZ0qm1pCtlUIyYSx_!!3838865325-0-cib.jpg",
            "https://images.chinatimes.com/newsphoto/2019-12-20/656/20191220000037.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTHYOlCa3bDBjypmH-LDK549Y2K_Y6hR7Saaw&s",
            "https://i.imgur.com/iq67SPm.jpg",
            "https://cdn.hk01.com/di/media/images/dw/20210707/489482591276109824637408.jpeg/sOkuWkg6jdkim0jZYtkbEChKJv3A3Kpw3Pjr2dz469k?v=w1920",
            "https://tshop.r10s.com/b27/50c/cfec/baef/3073/d808/4e76/1145ed930c0242ac110005.jpg?_ex=486x486",
            "https://media.nownews.com/nn_media/thumbnail/2022/03/1647937976105-2ed3e95d6cad43238ed07dcc941aff2b-500x625.jpg?unShow=false&waterMark=false",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEPBywmA39tptDq3a7cNG4u3O0utt18FVIYg&s",
            "https://s.yimg.com/zp/images/9DA66C9F780B61728BCB58F044CF4AF6F6ABBCA4",
            "https://img.cdn.91app.hk/webapi/imagesV3/Cropped/SalePage/361662/0/638616321323030000?v=1",
            "https://diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Cropped/SalePage/8085430/0/638580602488200000?v=1",
            "https://tshop.r10s.com/627/448/7fce/3c59/4041/e841/dfd1/116fed83c30242ac110003.jpg?_ex=486x486",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTp3dixUyncHWWwFb93xc3ap0AMfwFEdxuLYQ&s",
            "https://down-tw.img.susercontent.com/file/222b1cddcc028fca6be43a23c469121d",
            "https://tshop.r10s.com/9d1/dea/5403/d6d2/308b/3e64/7ca6/11f5eeb5570242ac110002.jpg?_ex=486x486",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTOu8MbM1UM9f2qoBFArh01bLef3L2AcAbhVw&s",
            "https://img.ltn.com.tw/Upload/ent/page/800/2021/04/22/phpqElaYW.jpg",
            "https://images.chinatimes.com/newsphoto/2018-06-23/656/20180623002206.jpg",
            "https://down-tw.img.susercontent.com/file/tw-11134201-7qukz-lhyil61k8nm8c0_tn.webp",
            "https://im2.book.com.tw/image/getImage?i=https://www.books.com.tw/img/001/081/57/0010815753.jpg&v=5c7666aek&w=375&h=375",
            "https://img.ltn.com.tw/Upload/ent/page/800/2020/03/25/phpFHoymZ.jpg",
            "https://cdn.hk01.com/di/media/images/dw/20240531/873078137703895040261407.jpeg/NNjtWk7r1hvScy8dyFMWXQJIMf8k79cvIsXtPiLF7T4?v=w1920",
            "https://bee-men.com/uploads/ckeditor/pictures/25032/content_wendy__624_209358671_322462809344373_4100224133141901654_n.jpg",
            "https://fs2.my-bras.com/upload/ftp/00_Product/22037000W-207-1.jpg",
            "https://image.hkhl.hk/f/1024p0/0x0/100/none/ce50202910d349d7f7ce14913be6456f/2023-06/_alyciac_343289471_538879431656306_1742365294561665946_n.jpg",
            "https://images.chinatimes.com/newsphoto/2020-07-08/656/20200708005597.jpg",
            "https://thumbs.dreamstime.com/z/%E6%BC%82%E4%BA%AE%E7%9A%84%E8%82%96%E5%83%8F%EF%BC%8C%E6%80%A7%E6%84%9F%E7%9A%84%E4%BA%9A%E6%B4%B2%E5%A5%B3%E4%BA%BA%EF%BC%8C%E7%9C%8B%E8%B5%B7%E6%9D%A5%E6%80%A7%E6%84%9F%E8%BF%B7%E4%BA%BA-245021896.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8NdHEyL0EmoU8Yy-Llnwt9Y6kJoSfzkT8gA&s",
            "https://diz36nn4q02zr.cloudfront.net/webapi/imagesV3/Original/SalePage/9501574/0/638503534754030000?v=1",
            "https://hk.on.cc/cnt/entertainment/20230625/photo/bkn-20230625210127720-0625_00862_001_02p.jpg?20230625210127",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTzolZ_BFSbZdm7m-CN2Ij8KikM4Rt7M9hafQ&s",
            "https://4gtvimg2.4gtv.tv/4gtv-Image/Production/Article/2022052611000006/202205261149480304.jpg",
            "https://images.chinatimes.com/newsphoto/2023-09-15/1024/20230915003039_20230915144323.jpg",
            "https://s.yimg.com/ny/api/res/1.2/Ah4NjV.AOKa.b3tVnQ5Mvg--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MA--/https://media.zenfs.com/zh-tw/nownews.hk/61f741eb6c0da77dcd1b78729907cf3f",
            "https://www.cangai.tw/wp-content/uploads/2021/06/01-3.jpg",
            "https://www.etonwedding.com/pre-wedding-photo/img/%E5%80%8B%E4%BA%BA%E5%AF%AB%E7%9C%9F_%E9%96%A8%E8%9C%9C%E5%AF%AB%E7%9C%9F/6-%E5%80%8B%E4%BA%BA%E5%AF%AB%E7%9C%9F_%E9%96%A8%E8%9C%9C%E5%AF%AB%E7%9C%9F%20(6).jpg",
            "https://media.nownews.com/nn_media/thumbnail/2024/06/1718362541052-136d076b9ae543be8c0f6f75bd032495-800x1200.webp?unShow=false&waterMark=false",
            "https://s.yimg.com/ny/api/res/1.2/qJHMvzmdgYYx5hIypNXnsw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTY0MDtoPTgwMA--/https://media.zenfs.com/en/ftvn.com.tw/e5132eb34101fffdae201a88d6c30f49",
            "https://today-obs.line-scdn.net/0hyK1CZDb3JmQMOjIUBE9ZMzRsKhU_XDxtLlxpASg4KAcpFjIwNFp1BykycEhxAjU3LFs9VX1ofV0gX2lgNA/w644",
            "https://img.ltn.com.tw/Upload/news/600/2019/05/29/phpb85WtL.jpg",
            "https://atctwn.com/wp-content/uploads/2021/07/main-4.jpg",
            "https://atctwn.com/wp-content/uploads/2021/07/WNM.jpg",
            "https://cdn2.ettoday.net/images/7803/d7803868.jpg",
            "https://cdn2.ettoday.net/images/4243/d4243363.jpg",
            "https://i1.kknews.cc/OZLWpFd7Sdd6e5Cj0RPSHbH-oLsCiEs_iyR54Sk/0.jpg",
            "https://www.etonwedding.com/img/photo/personal/music/personal%20(1).jpg",
            "https://i.getjetso.com/month_1612/20161209_28719cd2b8a32cd51239FeUOK7.jpg?name=%E6%96%B9%E7%B7%A9%E5%AF%AB%E7%9C%9F",
            "https://media-proc.singtao.ca/photo.php?s=https://media.singtao.ca/wp-content/uploads/master_sandbox/2020/02/s1000702362.jpg&f=jpeg&w=815&q=75&v=1",
            "https://cdn2.ettoday.net/images/6862/d6862321.jpg",
            "https://static.wixstatic.com/media/931713_32eb7c8072ef49fb9628c18caeb9e143~mv2.jpg/v1/fill/w_250,h_375,al_c,q_90,enc_auto/931713_32eb7c8072ef49fb9628c18caeb9e143~mv2.jpg",
            "https://img.ltn.com.tw/Upload/ent/page/800/2024/07/08/phpk9uyxg.jpg",
            "https://atctwn.com/wp-content/uploads/2020/02/yoda-1.jpg",
            "https://static.wixstatic.com/media/931713_d0f31e419e9f4099b00ac74dbc9190f6~mv2.jpg/v1/fill/w_250,h_375,al_c,q_90,enc_auto/931713_d0f31e419e9f4099b00ac74dbc9190f6~mv2.jpg",
            "https://i2.kknews.cc/tNTbLd-nwHY_0AvlNEFZWF-wVJJztVi9Ap6WzLg/0.jpg",
            "https://i.pinimg.com/1200x/96/c6/23/96c623821b53e8eb00e12ddabef911dd.jpg"
        ]
            
        # 進行圖片URL檢查
        while attempts < max_attempts:
            # 隨機選擇一個圖片 URL
            random_image_url = random.choice(image_urls)
            
            # 檢查圖片是否存在
            if check_image_url_exists(random_image_url):
                # 如果圖片存在，回傳訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
                    ]
                )
                break  # 找到圖片後退出迴圈
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法找到對應的圖片，請稍後再試。")
            )
        return

        # # 回傳訊息
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     [
        #         ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
        #     ]
        # )
        # return

    if event.message.text == "錢吶" or event.message.text == "錢啊" or event.message.text == "錢錢":       
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 500)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/MoneyMoney/LINE_ALBUM_money_%20({random_number}).jpg"
            
            # 檢查圖片是否存在
            if check_image_url_exists(image_url):
                # 如果圖片存在，回傳訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                    ]
                )
                break  # 找到圖片後退出迴圈
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法找到對應的圖片，請稍後再試。")
            )
        return
        
        # # 取隨機數
        # random_number = random.randint(1, 250)
        # random_number_str = str(random_number)
        # image_urls = "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_money_%20("+random_number_str+").jpg"

        # # 回傳訊息
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     [
        #         ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)
        #     ]
        # )
        # return

    if event.message.text == "多吶" or event.message.text == "多啊" or event.message.text == "多多":       
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 500)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/ManyMany/LINE_ALBUM_many_%20({random_number}).jpg"
            
            # 檢查圖片是否存在
            if check_image_url_exists(image_url):
                # 如果圖片存在，回傳訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                    ]
                )
                break  # 找到圖片後退出迴圈
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法找到對應的圖片，請稍後再試。")
            )
        return
        
        # # 取隨機數
        # random_number = random.randint(1, 250)
        # random_number_str = str(random_number)
        # image_urls = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_many_%20("+random_number_str+").jpg"

        # # 回傳訊息
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     [
        #         ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)
        #     ]
        # )
        # return

    if event.message.text == "錢多" or event.message.text == "錢錢多多":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 500)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/MoneyMany/LINE_ALBUM_moneymany_%20({random_number}).jpg"
            
            # 檢查圖片是否存在
            if check_image_url_exists(image_url):
                # 如果圖片存在，回傳訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                    ]
                )
                break  # 找到圖片後退出迴圈
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法找到對應的圖片，請稍後再試。")
            )
        return
        
        # # 取隨機數
        # random_number = random.randint(1, 250)
        # random_number_str = str(random_number)
        # image_urls = "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_moneymany_%20("+random_number_str+").jpg"

        # # 回傳訊息
        # line_bot_api.reply_message(
        #     event.reply_token,
        #     [
        #         ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)
        #     ]
        # )
        # return

    # if event.message.text == "洞":
    #     working_status = False
    #     random_number = random.randint(1, 4)
    #     random_number_str = str(random_number)
    #     image_urls ="https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/hole"+random_number_str+".jpg"

    #     # 回傳訊息
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         [
    #             ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)
    #         ]
    #     )
    #     return
    
    if event.message.text == "珮綺" or event.message.text == "綺綺":
        working_status = False
        messages = [
        TextSendMessage(text="好正"),
        TextSendMessage(text="貪吃的豬豬"),
        TextSendMessage(text="好可愛"),
        TextSendMessage(text="好漂亮"),
        TextSendMessage(text="美麗動人"),
        TextSendMessage(text="清新脫俗"),
        TextSendMessage(text="嬌美如花"),
        TextSendMessage(text="只會睡覺"),
        TextSendMessage(text="閉月羞花"),
        TextSendMessage(text="傾國傾城"),
        TextSendMessage(text="玉潔冰清"),
        TextSendMessage(text="花容月貌"),
        TextSendMessage(text="沒有D")
        ]
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )
        return
    
    if event.message.text == "健豪" or event.message.text == "黃健豪":
        working_status = False
        messages = [
        TextSendMessage(text="帥哥"),
        TextSendMessage(text="母胎單身"),
        TextSendMessage(text="飢渴難耐"),
        TextSendMessage(text="帥到分手"),
        TextSendMessage(text="桃園妹手到擒來"),
        TextSendMessage(text="帥到懷孕")
        ]
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )
        return 
    # if event.message.text.startswith("!"):
    #     working_status = False#喵喵我可愛
    #     stock_symbol = event.message.text[1:]  # 移除第一個字元「!」
    #     stock = yf.Ticker(stock_symbol)
    #     stock_info = stock.info
        
    #     #可愛的回應訊息
    #     response_message = (
    #         f"股票名稱: {stock_info.get('longName', '無法獲取')}\n"
    #         f"當日開盤價: {stock_info.get('regularMarketOpen', '無法獲取')}\n"
    #         f"當天的最高價: {stock_info.get('regularMarketDayHigh', '無法獲取')}\n"
    #         f"當天的最低價: {stock_info.get('regularMarketDayLow', '無法獲取')}\n"
    #         f"當前價格: {stock_info.get('regularMarketPrice', '無法獲取')}\n"
    #         f"市場價值: {stock_info.get('marketCap', '無法獲取')}"
    #     )
        
    #     # 回傳股票資訊給用戶
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=response_message)
    #     )
    #     return
  

    if working_status:
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))

if __name__ == "__main__":
    app.run()
