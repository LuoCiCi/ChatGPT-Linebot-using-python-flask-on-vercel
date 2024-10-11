from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, VideoSendMessage
from api.chatgpt import ChatGPT
import os
from datetime import datetime, timedelta
import requests, json
import random
import pytz
import textwrap

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

# 減少日期天數
def reduce_days(date, days):
    return date - timedelta(days=days)

# 至中央氣象屬開放資料平台取得地震資訊
def earth_quake():
    result = []
    code = 'CWA-84D9233C-12BC-4CD7-B744-7C7F35F7AE48'
    try:
        # 小區域 https://opendata.cwa.gov.tw/dataset/earthquake/E-A0016-001
        url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001?Authorization={code}'
        req1 = requests.get(url)  # 爬取資料
        data1 = req1.json()       # 轉換成 json
        eq1 = data1['records']['Earthquake'][0]           # 取得第一筆地震資訊
        t1 = data1['records']['Earthquake'][0]['EarthquakeInfo']['OriginTime']
        # 顯著有感 https://opendata.cwa.gov.tw/dataset/all/E-A0015-001
        url2 = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001?Authorization={code}'
        req2 = requests.get(url2)  # 爬取資料
        data2 = req2.json()        # 轉換成 json
        eq2 = data2['records']['Earthquake'][0]           # 取得第一筆地震資訊
        t2 = data2['records']['Earthquake'][0]['EarthquakeInfo']['OriginTime']
        
        result = [eq1['ReportContent'], eq1['ReportImageURI']] # 先使用小區域地震
        if t2>t1:
          result = [eq2['ReportContent'], eq2['ReportImageURI']] # 如果顯著有感地震時間較近，就用顯著有感地震
    except Exception as e:
        print(e)
        result = ['抓取失敗...','']
    return result

# Google drive影片連結轉換
def convert_drive_link_to_download_url(drive_link):
    # 驗證輸入的連結是否是 Google Drive 的格式
    if "drive.google.com" not in drive_link:
        raise ValueError("這不是有效的 Google Drive 連結")
    
    # 提取 FILE_ID (通常位於 /d/ 和 /view 之間)
    try:
        file_id = drive_link.split('/d/')[1].split('/')[0]
    except IndexError:
        raise ValueError("無法提取 FILE_ID，請確認連結格式")

    # 構建可下載的連結
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    return download_url

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

@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 回應訊息，自動已讀
    reply_message = "test OK~"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )

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
        # typhoon_url = "https://www.cwa.gov.tw/V8/C/P/Typhoon/TY_WARN.html"
        typhoon_url = "https://www.cwa.gov.tw/V8/C/P/Typhoon/TY_NEWS.html"
        typhoon_pic = "https://www.cwa.gov.tw/Data/typhoon/TY_WARN/B20.png"

        if (check_image_url_exists(typhoon_url)):
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text=f"{typhoon_url}"),
                    ImageSendMessage(original_content_url=typhoon_pic, preview_image_url=typhoon_pic)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="無法取得颱風消息"))
        return

    # if event.message.text == "颱風":
    #     working_status = True

    #     api_url = "https://api.typhoon.example.com/data"
    #     response = requests.get(api_url)

    #     if response.status_code == 200:
    #         typhoon_data = response.json()
    #         line_bot_api.reply_message(event.reply_token,
    #                 [
    #                     TextSendMessage(f"{typhoon_data['records']}")  # 傳送解碼後的文字
    #                     # ImageSendMessage(original_content_url=reply[1], preview_image_url=reply[1])
    #                 ]) # 傳送文字
    #     else:
    #         line_bot_api.reply_message(event.reply_token,
    #                 [
    #                     TextSendMessage(f"抓不到資訊")  # 傳送解碼後的文字
    #                     # ImageSendMessage(original_content_url=reply[1], preview_image_url=reply[1])
    #                 ]) # 傳送文字
    #     return
    
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

    if event.message.text == "地震":
        working_status = True
    
        reply = earth_quake()   # 執行函式，讀取數值
        text_message = TextSendMessage(text=reply[0])        # 取得文字內容

        # 確保 text_message 是正確的文字格式（Python 會自動處理 Unicode）
        text_message_decoded = text_message  # 這裡的 text_message 應該是正常的字串
        if (check_image_url_exists(reply[1])):
            line_bot_api.reply_message(event.reply_token,
                    [
                        TextSendMessage(f"地震監視畫面\nhttps://www.youtube.com/live/Owke6Quk7T0?si=CQYm0rJ3Mq_UnQEv"),
                        ImageSendMessage(original_content_url=reply[1], preview_image_url=reply[1])
                    ]) # 傳送文字
        else:
            line_bot_api.reply_message(event.reply_token,
                    [
                        TextSendMessage(f"抓不到地震資訊")  # 傳送解碼後的文字
                    ]) # 傳送文字
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
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        ts = [
            "大家早安，今天又是美好的一天~",
            "早安，工作奴隸認真上班喔！"
        ]

        # 隨機選擇一個文字
        random_ts_url = random.choice(ts)
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 22)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/MemeImage/goodmorning{random_number}.jpg"

            # 檢查圖片是否存在
            if check_image_url_exists(image_url):
                # 如果圖片存在，回傳訊息
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                        TextSendMessage(text=f"{random_ts_url}"),
                        ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
                    ]
                )
                break  # 找到圖片後退出迴圈
            attempts += 1
        else:
            # 如果在max_attempts次內未找到有效圖片
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"{random_ts_url}")
            )
        return

    if event.message.text == "晚安":
        working_status = False
        messages = [
            TextSendMessage(text="晚什麼安，我巴不得你想我想到夜不能寐"),
            TextSendMessage(text="快睡吧！不然等會我又要想你了"),
            TextSendMessage(text="好晚安，換一個世界想你"),
            TextSendMessage(text="我希望你做個甜甜的夢，然後甜甜是我"),
            TextSendMessage(text="趁星星不注意，我再想你一下下～"),
            TextSendMessage(text="晚上不要夢到我，夢裡陪睡也是要收費的呦～"),
            TextSendMessage(text="晚安，晚安！離別是多麼甜蜜的悲傷，我要說晚安，直到明天"),
            TextSendMessage(text="我希望現在就可以擁抱你，但既然我不能，那麼就只能度過一個美好的夜晚了"),
            TextSendMessage(text="我希望你成為我睡前最後想到的事。晚安"),
            TextSendMessage(text="讓我們互道一聲晚安 送走這匆匆的一天值得懷念的請你珍藏 應該忘記的莫再留戀"),
            TextSendMessage(text="晚安尻尻睡了"),
            TextSendMessage(text="各位晚安，夢裡見囉~")
        ]
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )        
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

    if event.message.text == "問號" or event.message.text == "?" or event.message.text == "??" or event.message.text == "???" or event.message.text == "？" or event.message.text == "？？":       
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 14)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/MemeImage/questionmark{random_number}.jpg"
            
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

    if event.message.text == "傻眼" or event.message.text == "傻眼貓咪":       
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 6)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/MemeImage/dumbfounded{random_number}.jpg"
            
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

    if event.message.text == ".." or event.message.text == "\u2026":       
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 10)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/MemeImage/dot{random_number}.jpg"
            
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

    if event.message.text == "抽":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0        
   
        # 進行圖片URL檢查
        while attempts < max_attempts:    
            
            random_value = random.random()        
            if random_value < 0.08787:  # 8.787% 機率
                
                random_number_image_urls_2 = random.randint(1,60)
                image_urls_2 = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/Drawing/Drawing%20({random_number_image_urls_2}).jpg"
                
                if check_image_url_exists(image_urls_2):
                # 如果圖片存在，回傳訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            TextSendMessage(f"恭喜抽中彩蛋編號: {random_number_image_urls_2}"),
                            ImageSendMessage(original_content_url=image_urls_2, preview_image_url=image_urls_2)
                        ]
                    )
                    break  # 找到圖片後退出迴圈
            else:
                
                random_number_image_urls_1 = random.randint(1,250)
                image_urls_1 = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/OtherDrawing/image%20({random_number_image_urls_1}).jpg"
                
                if check_image_url_exists(image_urls_1):
                # 如果圖片存在，回傳訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            ImageSendMessage(original_content_url=image_urls_1, preview_image_url=image_urls_1)
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

    if event.message.text == "抽奶" or event.message.text == "抽大奶":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        image_urls = [
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

    if "錢吶" in event.message.text or "錢啊" in event.message.text or "錢錢" in event.message.text:       
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

    if "多吶" in event.message.text or "多啊" in event.message.text or "多多" in event.message.text:       
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

    if "錢多" in event.message.text or "錢錢多多" in event.message.text:
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
        
    
    if "珮綺" in event.message.text or "綺綺" in event.message.text:
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
    
    if "健豪" in event.message.text:
        working_status = False
        messages = [
            TextSendMessage(text="帥哥"),
            TextSendMessage(text="母胎單身"),
            TextSendMessage(text="飢渴難耐"),
            TextSendMessage(text="帥到分手"),
            TextSendMessage(text="桃園妹手到擒來"),
            TextSendMessage(text="小公舉"),
            TextSendMessage(text="陳年法師"),
            TextSendMessage(text="這是小技巧"),
            TextSendMessage(text="啊不然要怎樣"),
            TextSendMessage(text="台南貴公子"), 
            TextSendMessage(text="皇家禮炮"),
            TextSendMessage(text="單身狗"),                      
            TextSendMessage(text="帥到懷孕"),
            TextSendMessage(text="新竹單身漢"),
            TextSendMessage(text="又再台北？"),
            TextSendMessage(text="早餐吃600元"),
            TextSendMessage(text="放線大濕"),
            TextSendMessage(text="玩草男孩")
        ]
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )
        return 

    if "聖博" in event.message.text or event.message.text == "洞":
        working_status = False
        messages = [
            TextSendMessage(text="快生孩子"),
            TextSendMessage(text="孟柔小狼狗"),
            TextSendMessage(text="人夫"),
            TextSendMessage(text="閃婚狗"),
            TextSendMessage(text="偷偷買公仔"),
            TextSendMessage(text="窮到賣公仔"),
            TextSendMessage(text="法號悅群"),
            TextSendMessage(text="有洞"),
            TextSendMessage(text="悅群師兄"),
            TextSendMessage(text="。"),
            TextSendMessage(text="喜歡大內內"),
            TextSendMessage(text="沒有30cm"),
            TextSendMessage(text="大概3cm?"),
            TextSendMessage(text="睡覺很吵"),
            TextSendMessage(text="再打呼阿"),
            TextSendMessage(text="竹北有房")
        ]
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )
        return 

    if "宇洋" in event.message.text or event.message.text == "洋" or event.message.text == "羊":
        working_status = False
        messages = [
            TextSendMessage(text="珮綺行動錢包"),
            TextSendMessage(text="宅"),
            TextSendMessage(text="鏟屎官1號"),
            TextSendMessage(text="雷喔"),
            TextSendMessage(text="汪"),
            TextSendMessage(text="積積陰陰的"),
            TextSendMessage(text="馬子狗"),
            TextSendMessage(text="馬桶沒在刷"),
            TextSendMessage(text="啥時換工作"),
            TextSendMessage(text="蟀")
        ]
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )
        return 
    
    if event.message.text == "抽籤":       
        working_status = False
        url = "https://gist.githubusercontent.com/mmis1000/d94bb0a9f37cfd362453/raw/0e3a7b06688fd7950a8d5f1ae858b27be2be7e09/%25E6%25B7%25BA%25E8%258D%2589%25E7%25B1%25A4.json"
        response = requests.get(url)
        lottery_data = response.json()
        random_lottery = random.choice(lottery_data)
        poem_text = textwrap.dedent(
        f"""籤詩號碼: {random_lottery.get('id', '未知')}
               
                                    
        籤詩類型: {random_lottery.get('type', '未知')}
        籤詩內容: {random_lottery.get('poem', '無內容')}

        解釋: {random_lottery.get('explain', '無解釋')}

        結果:
        願望: {random_lottery['result'].get('願望', '未知')}
        疾病: {random_lottery['result'].get('疾病', '未知')}
        盼望的人: {random_lottery['result'].get('盼望的人', '未知')}
        遺失物: {random_lottery['result'].get('遺失物', '未知')}
        蓋新居: {random_lottery['result'].get('蓋新居', '未知')}
        搬家: {random_lottery['result'].get('搬家', '未知')}
        嫁娶: {random_lottery['result'].get('嫁娶', '未知')}
        旅行: {random_lottery['result'].get('旅行', '未知')}
        交往: {random_lottery['result'].get('交往', '未知')}

        註解: {random_lottery.get('note', '無註解')}
        """)
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=poem_text)
            ]
        )
        return 

    if "擲筊" in event.message.text:
        working_status = False
        messages = [
            TextSendMessage(text="陰筊 - 表示神明否定、憤怒，或者不宜行事"),
            TextSendMessage(text="笑筊 - 表示神明一笑、不解"),
            TextSendMessage(text="笑筊 - 考慮中，行事狀況不明"),
            TextSendMessage(text="聖筊 - 表示神明允許、同意，或行事會順利"),
        ]
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
        )
        return 
    
    if working_status:
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))

if __name__ == "__main__":
    app.run()
