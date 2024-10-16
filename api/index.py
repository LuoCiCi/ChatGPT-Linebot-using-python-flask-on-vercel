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
        TextSendMessage(text=f"{reply_message}")
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

    # 獲取 userId
    user_id = event.source.user_id

    if event.message.text == "text":
        # line_bot_api.push_message(user_id, TextSendMessage(text='test....'))
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"user_id:{user_id}"))
        return

    if event.message.text == "QQQ":
        # line_bot_api.push_message(user_id, TextSendMessage(text='test....'))
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"@user_id:@{user_id}"))
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

    if event.message.text == "午安":
        working_status = False
        messages = [
            TextSendMessage(text="午安，順心如意！"),
            TextSendMessage(text="午安，來杯下午茶吧~"),
            TextSendMessage(text="午安唷~吃飽了嗎？"),
            TextSendMessage(text="午安，小睡一下，繼續加油喔！"),
            TextSendMessage(text="各位午安，記得吃飯喔！")
        ]
        line_bot_api.reply_message(
            event.reply_token,
            [
                random.choice(messages)
            ]
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
            random_number = random.randint(1, 17)
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
            if random_value < 0.1:  # 10% 機率
                
                random_number_image_urls_2 = random.randint(1,65)
                image_urls_2 = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/Drawing/SR%20({random_number_image_urls_2}).jpg"
                
                if check_image_url_exists(image_urls_2):
                # 如果圖片存在，回傳訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            TextSendMessage(f"抽中稀有SR彩蛋編號: {random_number_image_urls_2}"),
                            #TextSendMessage(f"{image_urls_2}"),
                            ImageSendMessage(original_content_url=image_urls_2, preview_image_url=image_urls_2)
                        ]
                    )
                    break  # 找到圖片後退出迴圈
            elif random_value < 0.1 + 0.03: #3% 機率
                
                random_number_image_urls_3 = random.randint(1,24)
                image_urls_3 = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/Drawing/SSR%20({random_number_image_urls_3}).jpg"
                
                if check_image_url_exists(image_urls_3):
                # 如果圖片存在，回傳訊息
                    line_bot_api.reply_message(
                        event.reply_token,
                        [
                            TextSendMessage(f"恭喜抽中超稀有SSR彩蛋編號: {random_number_image_urls_3}"),
                            #TextSendMessage(f"{image_urls_3}"),
                            ImageSendMessage(original_content_url=image_urls_3, preview_image_url=image_urls_3)
                        ]
                    )
                    break  # 找到圖片後退出迴圈
            else:
                
                random_number_image_urls_1 = random.randint(1,330)
                image_urls_1 = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/OtherDrawing/Draw%20({random_number_image_urls_1}).jpg"
                
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
            
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 90)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/BigBusted/bigbusted%20({random_number}).jpg"
            
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

    if event.message.text == "抽梗圖":
        working_status = False
        max_attempts = 5  # 設定最多嘗試的次數
        attempts = 0
        
        # 進行圖片URL檢查
        while attempts < max_attempts:
            random_number = random.randint(1, 90)
            image_url = f"https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/meme/meme%20({random_number}).jpg"
            
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
    
    if event.message.text == "抽晚餐" or event.message.text == "抽午餐":
        working_status = False       
        
        # 使用相對路徑讀取 data/config.json
        json_path = os.path.join(os.path.dirname(__file__), '/var/task/data/foodmenu.json')

        # 開啟並讀取 JSON 檔案
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 從 'food' 清單中隨機選取一個項目
        random_food = random.choice(data['food'])
            
        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"{random_food}")
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
            TextSendMessage(text="又長又大"),
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
