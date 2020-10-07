import sqlite3
import os
from time import sleep as wait
conn = sqlite3.connect("tickers.db") # подключаемся к БД
cursor = conn.cursor() # создаём курсор

while True:
	if 'record.txt' in os.listdir(os.getcwd() + '/flask'):
		with open('flask/record.txt' ,'r') as root:
			account, init_val, risk, data, suc_fee = root.readlines()
			cursor.execute(f"INSERT INTO Navs VALUES('{account}', {risk}, '{data}', {init_val}, {suc_fee}, 0)")
		conn.commit()
		os.remove('flask/record.txt')
		
conn.close()