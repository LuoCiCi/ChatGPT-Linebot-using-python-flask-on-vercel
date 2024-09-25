import random
from linebot.models import TextSendMessage, ImageSendMessage

# 定義 GitHub 上圖片的 URL 列表
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

# LINE Bot 回應，隨機選取一張圖片
def reply_with_random_image(event):
    # 隨機選擇一個圖片 URL
    random_image_url = random.choice(image_urls)

    # 回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        [
            ImageSendMessage(original_content_url=random_image_url, preview_image_url=random_image_url)
        ]
    )