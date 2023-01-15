#!/usr/bin/python3
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import mysql.connector

pswLocation = "/home/ileska/psw/mysql.txt"
lastFecthedLocation = "/home/ileska/ileska.luntti.net/reaktor/lastFetched.txt"

def printHeaders():
	print("Content-type: text/json")
	print("Cache-Control: no-cache, no-store, must-revalidate")
	print("Pragma: no-cache")
	print("Expires: 0")
	print("")

def saveFecthDate():
	with open(lastFecthedLocation, 'w') as fil:
		fil.write(str(datetime.now()))


def getUserInfo(user):
	serial, coordX, coordY, dist, timestamp = user
	ret = {
		"id": serial,
		"x": coordX,
		"y": coordY,
		"min dist": dist,
		"firstName": "",
		"lastName": "",
		"email": "",
		"phoneNro": "",
		"time": str(timestamp)
	}
	try:
		req = requests.get(f"https://assignments.reaktor.com/birdnest/pilots/{serial}")
		if req.status_code == 200:
			driver = req.json()
			ret["firstName"] = driver['firstName']
			ret["lastName"] = driver['lastName']
			ret["email"] = driver['email']
			ret["phoneNro"] = driver['phoneNumber']
	except requests.exceptions.RequestException:
		pass
	return ret

def main():
	psw = ""

	with open(pswLocation, 'r') as fil:
		psw = fil.read().replace('\n','')

	mydb = mysql.connector.connect(
		host="sql.ileska.luntti.net",
		user="sql_ileska",
		password=psw,
		database="train_sql_ileska"
	)

	cursor = mydb.cursor()

	query = ("SELECT serialNro, coordX, coordY, MIN(dist), timestamp from ViolentDrones group by serialNro;")

	cursor.execute(query)

	printHeaders()

	
	queryLocal = ("SELECT firstName, lastName, email, phoneNro from ViolentUsers WHERE serialNro = %s")

	with ThreadPoolExecutor(max_workers=100) as pool:
		dronesJson = list(pool.map(getUserInfo, cursor))

	print(json.dumps(dronesJson))
	saveFecthDate()

if __name__ == "__main__":
	main()
# print(f"""{{'1':{psw}}}""")
# print(f"""{{'1':1}}""")
