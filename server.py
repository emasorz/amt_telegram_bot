# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 18:15:25 2020

@author: Emanuele
"""
from bot import telegram_chatbot
import datetime

bot = telegram_chatbot("config.cfg")
update_id = None


while True:
    updates = bot.get_updates(offset=update_id)
    updates = updates["result"]
    if updates:
        for item in updates:
            from_ = item["message"]["from"]["id"]
            update_id = item["update_id"]
            try:
                message = str(item["message"]["text"])
            except:
                try:
                    message = str(item["message"]["location"]["latitude"]) + "-" + str(item["message"]["location"]["longitude"])
                except:
                    message="sticker"
            file = open("log.txt","a+") 
            #try:
                #file.write("\n"+ str(datetime.datetime.now()) + ": " + item['message']['from']['username'] + "> " + message)
            #except:
                #file.write("\n"+ str(datetime.datetime.now()) + ": " + item['message']['from']['first_name'] + " " + item['message']['from']['last_name'] + "> " + message)
            file.close() 
            bot.send_reply(message, from_)
#            
            
            
            
            
            
            
            
            