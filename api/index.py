from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from api.chatgpt import ChatGPT

import os

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
working_status = os.getenv("DEFAULT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
chatgpt = ChatGPT()

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
    global working_status
    if event.message.type != "text":
        return

    if event.message.text == "天氣":
        working_status = True
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="要取得天氣圖片。")
            )
        image_urls = get_weather_image_urls()  # 取得天氣圖片 URL
       
        if image_urls:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="找到天氣圖片囉"))
            # 發送圖片
            for img_url in image_urls:
                line_bot_api.reply_message(
                    event.reply_token,
                    ImageSendMessage(original_content_url=img_url, preview_image_url=img_url)
                )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="未找到天氣圖片。")
            )
        
        return

    if event.message.text == "說話":
        working_status = True
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="我可以說話囉1，歡迎來跟我互動 ^_^ "))
        return

    if event.message.text == "閉嘴":
        working_status = False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="好的，我乖乖閉嘴 > <，如果想要我繼續說話，請跟我說 「說話」 > <"))
        return

    if working_status:
        chatgpt.add_msg(f"HUMAN:{event.message.text}?\n")
        reply_msg = chatgpt.get_response().replace("AI:", "", 1)
        chatgpt.add_msg(f"AI:{reply_msg}\n")
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_msg))


# 天氣圖片抓取函式（不存圖片，只回傳圖片 URL）
def get_weather_image_urls():
    # 使用 ChromeDriverManager 自動管理 ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # 打開目標網頁
    driver.get("https://www.cwa.gov.tw/V8/C/P/Rainfall/Rainfall_QZJ.html")
    

    # 等待網頁完全加載
    time.sleep(5)

    # 查找所有圖片元素
    images = driver.find_elements(By.TAG_NAME, 'img')
    image_urls = []

    # 遍歷所有找到的圖片，並篩選來自 Data/rainfall 目錄的圖片
    for img in images:
        img_url = img.get_attribute('src')

        # 只回傳來自 Data/rainfall 的圖片 URL
        if "Data/rainfall" in img_url:
            image_urls.append(img_url)


    # 關閉瀏覽器
    driver.quit()

    return image_urls




if __name__ == "__main__":
    app.run()
