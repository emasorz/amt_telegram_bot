# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 17:51:01 2020

@author: Emanuele
"""
import requests
import json
import configparser as cfg
from brain import brain
from brain import MsgType

class telegram_chatbot():

    def __init__(self, config):
        self.token = self.read_token_from_config_file(config)
        self.base = "https://api.telegram.org/bot{}/".format(self.token)
        self.brain = brain()

    def get_updates(self, offset=None):
        url = self.base + "getUpdates?timeout=100"
        if offset:
            url = url + "&offset={}".format(offset + 1)
        r = requests.get(url)
        return json.loads(r.content)

    def __send_message(self, msg, chat_id):
        url = self.base + "sendMessage?chat_id={}&text={}".format(chat_id, msg)
        if msg is not None:
            requests.get(url)
            
    def __send_image(self,img,chat_id):
        url = self.base + "sendPhoto?chat_id={}&photo={}".format(chat_id, img)
        if img :
            requests.get(url)
            
    def send_reply(self, obj, chat_id):
        reply = self.brain.prepare_reply(obj)
        if reply[0] == MsgType.IMAGE:
            self.__send_image(reply[1],chat_id)
        else:
            self.__send_message(reply[1],chat_id)
    
    def read_token_from_config_file(self, config):
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds', 'token')
    
