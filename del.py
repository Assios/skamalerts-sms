import sqlite3 as sql

def delete_number_from_database(number):
    con = sql.connect("../database.db")
    cur = con.cursor()
    cur.execute("DELETE FROM smses WHERE sms=?", (number,))
    con.commit()

delete_number_from_database("1482176662")
