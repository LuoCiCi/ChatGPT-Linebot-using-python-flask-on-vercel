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
        
@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "天氣":
        working_status = True
        
        prev, prev_ = get_prev30_prevprev30()

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

    if event.message.text == "溫度":
        working_status = True
        
        prev, prev_ = get_prev00_prevprev00()

        # 將 prev_time 轉換成日期字串
        prev_date_str = prev.strftime('%Y-%m-%d')
        prev_time_str = prev.strftime('%H%M')

        prev_prev_date_str = prev_.strftime('%Y-%m-%d')
        prev_prev_time_str = prev_.strftime('%H%M')

        prev_url = "https://www.cwa.gov.tw/Data/temperature/" + prev_date_str + "_" + prev_time_str + ".GTP8.jpg"
        prev_prev_url = "https://www.cwa.gov.tw/Data/temperature/" + prev_prev_date_str + "_" + prev_prev_time_str + ".GTP8.jpg"

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

    if event.message.text == "急了":
        working_status = False
        image_urls = [
            "https://memeprod.sgp1.digitaloceanspaces.com/user-wtf/1693521527021.jpg",
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQx9BFj90LO-rK98keHK6wAkEiah_McWWdVeQ&s",
            "https://stickershop.line-scdn.net/stickershop/v1/product/25440282/LINEStorePC/main.png?v=1",
            "https://p3-pc-sign.douyinpic.com/tos-cn-i-0813/bafe6270a73a4d28bd793abc57c11ec4~tplv-dy-aweme-images:q75.webp?biz_tag=aweme_images&from=327834062&s=PackSourceEnum_SEARCH&sc=image&se=false&x-expires=1729706400&x-signature=vZwXDWxIV2bYqm1TelPGbIxWLqQ%3D",
            "https://stickershop.line-scdn.net/stickershop/v1/product/25428386/LINEStorePC/main.png?v=1"
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
        return

    if event.message.text == "錢吶":
        working_status = False
        # 取隨機數
        random_number = random.randint(1, 200)
        random_number_str = str(random_number)
        image_urls ="https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/LINE_ALBUM_money_ ("+random_number_str+").jpg"
        
        # 隨機選擇一個圖片 URL
        random_image_url = random.choice(image_urls)

        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
            ]
        )
        return

    if event.message.text == "喵喵":
        working_status = False
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
        return
    
    if event.message.text == "有洞":
        working_status = False
        random_number = random.randint(1, 4)
        random_number_str = str(random_number)
        image_urls ="https://raw.githubusercontent.com/hal-chena/Line-Image/refs/heads/main/hole"+random_number_str+".jpg"

        # 回傳訊息
        line_bot_api.reply_message(
            event.reply_token,
            [
                ImageSendMessage(original_content_url=image_urls, preview_image_url=image_urls)
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
