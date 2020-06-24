
# インポートするライブラリ
from flask import Flask, request, abort
from linebot import (
   LineBotApi, WebhookHandler
)
from linebot.exceptions import (
   InvalidSignatureError
)
from linebot.models import (
   SourceUser,FollowEvent, MessageEvent, TextMessage, TextSendMessage,
   TemplateSendMessage, ButtonsTemplate,
   PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
import RPi.GPIO as GPIO
import os
import requests
import urllib.request
import base64
import sqlite3
import time
import datetime
import userInfo

# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)
#環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
   # get X-Line-Signature header value
   signature = request.headers['X-Line-Signature']
   # get request body as text
   body = request.get_data(as_text=True)
   app.logger.info("Request body: " + body)
   # handle webhook body
   try:
       handler.handle(body, signature)
   except InvalidSignatureError:
       abort(400)
   return 'OK'


# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    if isinstance(event.source, SourceUser):

        profile = line_bot_api.get_profile(event.source.user_id)

        user_id = profile.user_id

        userid_list = userInfo.USER_ID_LIST

        open_key_words = ["開けて","開ける","開","open","開け","開く","解除","あ","あけて","あける"]

        close_key_words = ["閉めて","閉める","閉","close","閉じろ","閉まる","施錠","し","しめる","しめて"]


        def send_message(message):
            line_bot_api.reply_message(
                event.reply_token,TextSendMessage(text=message)
            )


        def getNewMessage():
            conn = sqlite3.connect("history.db")

            c = conn.cursor()

            c.execute("select message from user order by id desc limit 1;")

            data = c.fetchall()
            data = str(data)
            data = data[3:]
            data = data[:-4]
            conn.close()
            return data
        
        def openedFlg():
            lastMessage = getNewMessage()
            if lastMessage in close_key_words:
                return False
            else:
                return True

        def open_key(angle,mess):
            data = getNewMessage()

            if mess in close_key_words and data in close_key_words:
                return False
            if mess in open_key_words and data in open_key_words:
                return False
            else:
                GPIO.setmode(GPIO.BCM)
                
                gp_out = 2
                GPIO.setup(gp_out, GPIO.OUT)
                motor = GPIO.PWM(gp_out, 50)
                motor.start(0.0)
                motor.ChangeDutyCycle(angle)
                time.sleep(0.5)

                GPIO.cleanup()
                return True


        def database_history(name,mess):

            dt_now = datetime.datetime.now()
            dt_now = str(dt_now)
            dt_now = dt_now[:20]

            conn = sqlite3.connect('history.db')

            c = conn.cursor()

            profile = line_bot_api.get_profile(event.source.user_id)
            userid = profile.user_id

            c.execute('insert into user\
                    (datetime,username,message,user_id)values("%s","%s","%s","%s");'%(dt_now,name,mess,userid))

            conn.commit()
            conn.close()

        def check_history():

            conn = sqlite3.connect("history.db")

            c = conn.cursor()

            c.execute("select datetime, username, message from user order by id desc limit 20;")

            data = list(c)
            strData = "< 履歴 >\n"
            for data in data:
                for i in range(3):
                    if i == 0:
                        date = str(data[i])
                        date = date[5:]
                        date = date[:-4]
                        strData = strData + date
                    else:
                        strData = strData + " - " +  data[i]

                strData = strData + "\n"
            strData = strData[:-1]

            # data = c.fetchall()
            data = str(strData)
            conn.close()

            send_message(data)

        text = event.message.text

        if user_id in userid_list:

            text = event.message.text
            text = text.replace(" ","")

            profile = line_bot_api.get_profile(event.source.user_id)
            userid = profile.user_id

            username = profile.display_name

            if text in open_key_words:
                openKey = open_key(7.2,"あ")
                if openKey == True:
                    send_message("鍵を開けました")
                    database_history(username,text)
                else:
                    send_message("既に実行済みです")

            elif text in close_key_words:
                closeKey = open_key(2.5,"し")
                if closeKey == True:
                    send_message("鍵を閉めました")
                    database_history(username,text)
                else:   
                    send_message("既に実行済みです")

            elif text == "い":
                if openedFlg() == True:
                    send_message("開錠されています")
                else:
                    send_message("施錠されています")
            
            elif text == "ヘルプ":
                send_message("あける → ドアが開きます\nしめる → ドアが閉まります\nい → 現在の施錠状況を確認します\n履歴 → 履歴が観覧できます")   

            elif text == "履歴":
                check_history()   

            elif text == "こんにちは":
                send_message("こんにちは!")
            
            else:
                send_message("無効なコマンドです\n< ヘルプ >コマンドで参照できます")


        else:
            send_message("家族以外のメッセージは受け付けません")


if __name__ == "__main__":
   port = int(os.getenv("PORT"))
   app.run(host="0.0.0.0", port=port,debug=True)
