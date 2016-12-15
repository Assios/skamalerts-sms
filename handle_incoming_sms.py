#!/usr/bin/env python
# -*- coding: utf-8 -*-

# encoding=utf8

import requests
import sqlite3 as sql
import threading
import datetime
from keys import LOLTEL_AUTHENTICATION_TOKEN


def add_number_to_database(number):
    con = sql.connect("../database.db")
    cur = con.cursor()
    cur.execute("INSERT INTO phone_numbers (phone_number) VALUES (?)", (number,))
    con.commit()


def delete_number_from_database(number):
    con = sql.connect("../database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM phone_numbers WHERE phone_number=?", (number,))
    con.commit()


def get_registered_numbers():
    conn = sql.connect('../database.db')
    c = conn.cursor()
    c.execute('SELECT phone_number FROM phone_numbers')
    all_rows = [row[0] for row in c.fetchall()]
    return all_rows


def get_previous_smses():
    conn = sql.connect("../database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM smses')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]


def add_sms(sms):
    con = sql.connect("../database.db")
    c = con.cursor()
    c.execute("INSERT INTO smses (sms) VALUES (?)", (sms,))
    con.commit()
    con.close()


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


def get_previous_skam_posts():
    conn = sql.connect("../database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM posts')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]


def add_skam_post(post):
    con = sql.connect("../database.db")
    c = con.cursor()
    c.execute("INSERT INTO posts (post) VALUES (?)", (post,))
    con.commit()
    con.close()


def insert(num, db="phone_numbers.db"):
    con = sql.connect(db)
    cur = con.cursor()
    cur.execute("INSERT INTO phone_numbers (phone_number) VALUES (?)", (num,))
    con.commit()


def view_inbox(starts_with="SKAM", limit=30):
    """
    http://docs.loltelapi.com.s3-website-eu-west-1.amazonaws.com/reference/#sms
    """

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % LOLTEL_AUTHENTICATION_TOKEN}
    data = {"starts_with": starts_with, "limit": limit}

    r = requests.post("https://loltelapi.com/api/sms/search", headers=headers, json=data)

    return r.json()["data"]


def send_sms(recipient, sms):
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % LOLTEL_AUTHENTICATION_TOKEN}
    data = {"to_msisdn": str(recipient), "message": sms}

    r = requests.post('https://loltelapi.com/api/sms', headers=headers, json=data)
    print(r)
    return r


def handle_new_sms(number, text):
    nums = get_registered_numbers()
    message = text[4:].lower().strip()

    if message.startswith("foodora"):
        return send_sms(number, "Et sykkelbud vil nå oppsøke og varsle deg når det kommer nye Skam-innlegg. NB: GPS må være påslått. https://skamalerts.com")

    if number in nums:
        print("Number already added.")
        if message == "" or message == "start":
            return send_sms(number, "Dette nummeret er allerede registrert, og du vil motta SMS når det kommer nye SKAM-innlegg.")
        elif message.startswith("stop"):
            delete_number_from_database(number)
            return send_sms(number, "don't cry because it's over. smile because it happened :)\n\nhttps://skamalerts.com")
        else:
            return send_sms(number, "%s er ikke en gyldig kommando, ass ;)" % message)
    else:
        print("New number.")
        if message == "" or message == "start":
            add_number_to_database(number)
            return send_sms(number, "Du vil nå motta gratis SMS når det kommer nye Skam-innlegg. Send SKAM STOPP til 90300095 for å melde deg av. Denne tjenesten er levert av https://skamalerts.com")
        elif message.startswith("stop"):
            return send_sms(number, "Dette nummeret er ikke registrert hos skamalerts.com")
        else:
            return send_sms(number, "%s er ikke en gyldig kommando, ass. For å registrere deg, send SKAM til 90 3000 95" % message)


def main():
    for message in view_inbox(limit=30):
        timestamp = str(message["meta"]["timestamp"])
        if timestamp in get_previous_smses():
            print("Reached a message seen before at %s" % datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d.%m.%Y %H:%M:%S'))
            break
        else:
            add_sms(timestamp)
            print("FROM_NUMBER %s CONTENT %s" % (message["from_number"], message["content"]))
            handle_new_sms(message["from_number"], message["content"])

    threading.Timer(20, main).start()

main()
