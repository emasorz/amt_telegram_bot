# -*- coding: utf-8 -*-
from rivescript import RiveScript
import requests
from bs4 import BeautifulSoup
import configparser as cfg
import json
from enum import Enum

class MsgType(Enum):
        CODE=1
        LOCATION=2
        LINE=3
        CHAT=4
        IMAGE=5
        ERROR=6
        TELEGRAM = 7

class brain():
    def __init__(self):
        self.chat_brain = self.__init_chat_brain()
        self.amt_base_url = "https://www.amt.genova.it/amt/simon.php"
        self.google_base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        self.APIKEY = self.read_APIKEY_from_config_file('config.cfg')
        self.db = self.load_db('db.txt')
        self.images_set = self.load_db('images.txt')

    def read_APIKEY_from_config_file(self, config):
        parser = cfg.ConfigParser()
        parser.read(config)
        return parser.get('creds','APIKEY')
    
    def load_db(self,db):
        with open(db) as json_file:
            result = json.load(json_file)
            return result
    
    def get_code_from_name(self, name):
        for fermata in self.db['fermate']:
            if fermata['name'] == name :
                return fermata['id']
    
    def msg_contains_trigger(self, msg):
        for image in self.images_set['images']:
            if image['trigger'] in msg.lower() :
                return image['url']
        return None
    
    
    def get_stop_bus_time(self,code):
        url = self.amt_base_url + "?CodiceFermata={}".format(code)
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = []      
        for tr in soup.find_all('tr'):
            td = list(tr.children)
            try:
                rows.append(td[1].string + " " + td[3].string + " " + td[5].string +  " " + td[7].string)
            except:
                continue
        reply = ""
        for row in rows:
            reply += row + "\n"
        return reply

    def find_nearby_transit_station(self, loc ,radius = 150, types = "transit_station"):
        lat, lng = loc
        url = self.google_base_url + "?location={},{}&radius={}&type={}&key={}".format(lat, lng, radius, types, self.APIKEY)
        response = requests.get(url)
        res = json.loads(response.text)
        reply = ""
        for result in res["results"]:
            info = result["name"].upper()
            code = self.get_code_from_name(result["name"].upper()) 
            if code :
                info += " " + code
                reply += info + "\n"
        return reply      
    
    def __init_chat_brain(self):
        brain = RiveScript()
        brain.load_directory(".")
        brain.sort_replies()
        return brain
    
    def define_msg_type(self,msg):
        if msg[0] == '/':
            return MsgType.TELEGRAM
        try:
            int(msg)
            if len(msg) == 4:
                return MsgType.CODE
            else:
                return MsgType.LINE
        except:
            if len(msg.split("-")) == 2:
                return MsgType.LOCATION
            elif self.msg_contains_trigger(msg):
                return MsgType.IMAGE
            else:
                return MsgType.CHAT
                
        return MsgType.ERROR
    
    def prepare_reply(self,msg):
        msg_type = self.define_msg_type(msg)
        if msg_type == MsgType.CODE:
            reply = (msg_type,self.get_stop_bus_time(msg))
        elif msg_type == MsgType.TELEGRAM:
            reply = (msg_type, "Hey, Ciao! Come posso aiutati?")
        elif msg_type == MsgType.LOCATION:
            loc = msg.split('-')
            reply = (msg_type,self.find_nearby_transit_station(loc))
        elif msg_type == MsgType.IMAGE:
            reply = (msg_type,self.msg_contains_trigger(msg))
        elif msg_type == MsgType.LINE:
            reply = (msg_type,"Funzione su linee ancora da IMPLEMENTARE")
        elif msg_type == MsgType.CHAT:
            reply = (msg_type,self.chat_brain.reply("localuser", msg))
        elif msg_type == MsgType.ERROR:
            reply = (msg_type,"Comando non riconsociuto")
        else:
            reply = (msg_type,"Non so che dire")
        return reply