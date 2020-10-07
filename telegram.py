import sqlite3
import requests
import schedule

def send(data):
    #Replace token, chat_id & text variables
    text = '\n'.join(data)
    
    token = '1329829542:AAFgVA7YwS89N99R-s90VA7A9XV5EKgAM8A'
    params = {'chat_id': 413813117, 'text': text, 'parse_mode': 'HTML'}
    resp = requests.post('https://api.telegram.org/bot{}/sendMessage'.format(token), params)
    resp.raise_for_status()


def get_data():
	acc_TagPrice = dict()
	with open('navs.txt', 'r') as root:
		for line in root.readlines():
			acc, tag, price, fucker = line.split()
			acc_TagPrice[acc] = [tag, float(price)]

		conn = sqlite3.connect("tickers.db")
		cursor = conn.cursor()
		cursor.execute('SELECT * FROM Navs')
		records = cursor.fetchall()

	for acc in acc_TagPrice.keys():
		information = [acc, acc_TagPrice[acc][0]]
		for record in records:
			if acc in record:
				information.append(record[2])
				information.append(acc_TagPrice[acc][1] - record[-1])
				information.append((acc_TagPrice[acc][1] - record[-1]) * record[-2])
				information.append((record[-1] * record[1]) / record[-1] * 100 + (acc_TagPrice[acc][1] - record[-1])/ record[-1] * 100)

	send([str(item) for item in information])

schedule.every(30).minutes.do(get_data)
while True:
	schedule.run_pending()
