import sqlite3 as sql

conn = sql.connect('database.db')
conn.execute('CREATE TABLE IF NOT EXISTS phone_numbers (phone_number TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS posts (post TEXT)')
conn.execute('CREATE TABLE IF NOT EXISTS smses (sms TEXT)')
conn.close()
