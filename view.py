import sqlite3 as sql

def get_previous_smses():
    conn = sql.connect("../database.db")
    c = conn.cursor()
    c.execute('SELECT * FROM smses')
    all_rows = c.fetchall()
    c.close()
    return [row[0] for row in all_rows]

def get_registered_numbers():
    conn = sql.connect('../database.db')
    c = conn.cursor()
    c.execute('SELECT phone_number FROM phone_numbers')
    all_rows = [row[0] for row in c.fetchall()]
    return all_rows


nums = get_registered_numbers()

print len([n for n in nums])
