#!/usr/bin/env python
# -*- coding: utf-8 -*-

# encoding=utf8

import sqlite3 as sql
import sys

from bs4 import BeautifulSoup
from datetime import datetime
import urllib
import threading
import requests
from multiprocessing import Pool
from keys import LOLTEL_AUTHENTICATION_TOKEN

reload(sys)
sys.setdefaultencoding('utf8')


def fetch_sms_recipients():
    conn = sql.connect("../database.db")
    c = conn.cursor()
    c.execute('SELECT phone_number FROM phone_numbers')
    all_rows = c.fetchall()
    c.close()
    rows = [row[0] for row in all_rows if row[0]]
    return rows


class Post:
    def get_type(self, article):
        link = article.find("a")
        href = link["href"]

        if article.find("div", class_="nrk-video"):
            return "video"
        if "insta" in href:
            return "instagram-post"
        else:
            return "chat"

    def convert_time(self, norwegian):
        norwegian = norwegian.split(" ", 1)[1]
        return datetime.strptime(norwegian, '%d.%m.%y kl %H.%M')

    def __init__(self, article):
        self.article = article
        self.link = article.find("a")
        self.href = self.link["href"]
        self.original_time = self.link.get_text()
        self.original_time = self.original_time.replace("ø", "o")
        self.time = self.convert_time(self.original_time)
        self.type = self.get_type(self.article)
        try:
            self.title = article.find("h2").find("a")["title"]
        except:
            self.title = ""


def fetch_previous_skam_posts():
    conn = sql.connect("../database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM posts')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]


def add_post(post):
    con = sql.connect("../database.db")
    c = con.cursor()
    c.execute("INSERT INTO posts (post) VALUES (?)", (post,))
    con.commit()
    con.close()


def send_sms((recipient, message)):
    recipient = str(recipient)
    if len(recipient) == 8:
        recipient = "47" + recipient

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % LOLTEL_AUTHENTICATION_TOKEN}
    data = {"to_msisdn": str(recipient), "message": message}

    r = requests.post('https://loltelapi.com/api/sms', headers=headers, json=data)
    print(r.url)
    print(r)
    return r


def generate_sms(_type, time, href):
    return "SKAM ALERT! En ny " + _type + " ble publisert " + time + "! Her kan du gå direkte til innlegget: " + href


pool = Pool()


def skam():
    r = urllib.urlopen('http://skam.p3.no').read()
    soup = BeautifulSoup(r, "html.parser")
    articles = soup.find_all("article", class_="post")
    posts = [Post(article) for article in articles]

    if not posts or len(posts) == 0:
        print("EMPTY POSTS")
    else:
        last = posts[0]
        _id = last.original_time.lower() + "_sms"

        if not _id in fetch_previous_skam_posts():
            add_post(_id)

            sms_recipients = fetch_sms_recipients()
            sms = generate_sms(last.type, last.original_time, last.href)
            smses = [sms for _ in range(len(sms_recipients))]

            pool.map_async(send_sms, zip(sms_recipients, smses))

            print(sms_recipients)
            print("SMS SENT")
        else:
            print(_id)

    threading.Timer(10.0, skam).start()

def send_custom_message_to_all_recipients():
    sms_recipients = fetch_sms_recipients()
    sms = "da var denne seSongen av skAm over. vi seNder deg en sms når neste esong kommer! mvh sAmalerts.com"

    for recipient in sms_recipients:
	#send_sms((recipient, sms))
	print("Sent %s to %s" % (sms, recipient))

    print(sms_recipients)
    print("SENT CUSTOM MESSAGE")

send_custom_message_to_all_recipients()
