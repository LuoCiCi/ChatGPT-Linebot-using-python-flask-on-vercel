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

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFAULT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()


def reply_with_random_image(event):
    
    image_urls = [
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_1.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_2.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_3.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_4.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_5.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_6.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_7.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_8.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_9.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_10.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_11.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_12.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_13.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_14.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_15.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_16.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_17.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_18.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_19.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_20.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_21.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_22.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_23.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_24.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E5%A4%9A%E5%A4%9A_240925_25.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_1.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_2.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_3.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_4.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_5.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_6.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_7.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_8.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_9.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_10.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_11.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_12.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_13.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2_240925_14.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_1.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_2.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_3.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_4.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_5.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_6.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_7.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_8.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_9.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_10.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_11.jpg",
    "https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_%E9%8C%A2%E9%8C%A2%E5%A4%9A%E5%A4%9A_240925_12.jpg"
    ]
    # 隨機選擇一個圖片 URL
    random_image_url = random.choice(image_urls)

    # 回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        [
            ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
        ]
    )
    
# 計算出前一個整點或半點的時間以及下一個整點或半點的時間
def get_image_name():
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
        
@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "天氣":
        working_status = True
        
        prev, prev_ = get_image_name()

        # 將 prev_time 轉換成日期字串
        prev_date_str = prev.strftime('%Y-%m-%d')
        prev_time_str = prev.strftime('%H%M')

        prev_prev_date_str = prev_.strftime('%Y-%m-%d')
        prev_prev_time_str = prev_.strftime('%H%M')

        prev_url = "https://www.cwa.gov.tw/Data/rainfall/" + prev_date_str + "_" + prev_time_str + ".QZJ8.jpg"
        prev_prev_url = "https://www.cwa.gov.tw/Data/rainfall/" + prev_prev_date_str + "_" + prev_prev_time_str + ".QZJ8.jpg"

        if (check_image_url_exists(prev_url)):
            # url = prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_url, preview_image_url=prev_url)
                ]
            )
        else:
            # url = prev_prev_url
            # 回傳訊息
            line_bot_api.reply_message(
                event.reply_token,
                [
                    ImageSendMessage(original_content_url=prev_prev_url, preview_image_url=prev_prev_url)
                ]
            )
        return
        
    if event.message.text == "說話":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我可以說話囉12，歡迎來跟我互動 ^_^ "))
        return

    if event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我繼續說話，請跟我說 「說話」 > <"))
        return

    if event.message.text == "喵喵":
        working_status = False
        reply_with_random_image()
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
