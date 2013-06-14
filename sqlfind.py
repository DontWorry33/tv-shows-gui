#!/usr/bin/python2.6

import sqlite3 as sql


conn = sql.connect('keys.db')
cur = conn.cursor()

show = '-modern-family'
cur.execute('DELETE FROM shows WHERE names="-modern-family"')
conn.commit()
for x in cur.execute('SELECT * FROM shows'):
        print x[0]
