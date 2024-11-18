from linebot.models import TextSendMessage

def handle_instruction_message(event, line_bot_api):

    if event.message.text in ["指令", "選單", "列表", "help", "Help"]:
        # 定義指令訊息
        instruction_message = (
            "🚀【一番賞】\n"
            "Reset(A~C)\n"
            "一番賞(A~C)(1~5)連抽\n"
            "庫存(A~C)\n\n"
            "☀️【問問台灣還好嗎?】\n"
            "天氣\n"
            "颱風\n"
            "地震\n"
            "雨量\n"
            "溫度\n"
            "紫外線\n"
            "衛星\n"
            "雷達\n\n"
            "🙏🏻【求神問佛】\n"
            "抽籤\n"
            "擲筊\n\n"
            "🔥【提振精神】\n"
            "抽\n"
            "抽奶\n"
            "抽梗圖\n"
            "錢錢\n"
            "多多\n"
            "錢多\n"
            "多多三連抽\n"
            "錢錢三連抽\n"
            "抽寶可夢\n"
            "抽寶可夢-(0~1025)\n\n"
            "🍔【點餐】\n"
            "抽晚餐\n"
            "抽午餐"
        )
        # 回傳訊息到 LINE
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=instruction_message)
        )
        return