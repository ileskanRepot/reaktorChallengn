#!/usr/bin/python3
import json
import requests
from datetime import datetime
import mysql.connector

def printHeaders():
	print("Content-type: text/json")
	print("Cache-Control: no-cache, no-store, must-revalidate")
	print("Pragma: no-cache")
	print("Expires: 0")
	print("")

def main():
	psw = ""

	with open("../../psw/mysql.txt", 'r') as fil:
		psw = fil.read().replace('\n','')

	mydb = mysql.connector.connect(
		host="sql.ileska.luntti.net",
		user="sql_ileska",
		password=psw,
		database="train_sql_ileska"
	)

	cursor = mydb.cursor(buffered=True)

	query = ("SELECT serialNro, coordX, coordY, MIN(dist), timestamp from ViolentDrones group by serialNro;")

	cursor.execute(query)

	printHeaders()

	
	queryLocal = ("SELECT firstName, lastName, email, phoneNro from ViolentUsers WHERE serialNro = %s")

	dronesJson = []
	for ii, (serial, coordX, coordY, dist, timestamp) in enumerate(cursor):
		cursorLocal = mydb.cursor(buffered=True)
		dronesJson.append({
			"id": serial,
			"x": coordX,
			"y": coordY,
			"min dist": dist,
			"firstName": "",
			"lastName": "",
			"email": "",
			"phoneNro": "",
			"time": str(timestamp)
		})
		cursorLocal.execute(queryLocal, (serial,))
		if cursorLocal.rowcount > 0:
			# firstName, lastName, email, phoneNro = cursorLocal
			for items in cursorLocal:
				firstName, lastName, email, phoneNro = items
				dronesJson[ii]["firstName"] = firstName
				dronesJson[ii]["lastName"] = lastName
				dronesJson[ii]["email"] = email
				dronesJson[ii]["phoneNro"] = phoneNro
				break
		else:
			try:
				req = requests.get(f"https://assignments.reaktor.com/birdnest/pilots/{serial}")
				if req.status_code == 200:
					driver = req.json()
					dronesJson[ii]["firstName"] = driver['firstName']
					dronesJson[ii]["lastName"] = driver['lastName']
					dronesJson[ii]["email"] = driver['email']
					dronesJson[ii]["phoneNro"] = driver['phoneNumber']
					cursorLocal.execute("INSERT INTO ViolentUsers (serialNro, firstName, lastName, email, phoneNro, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",(serial, driver['firstName'], driver['lastName'],driver['email'],driver['phoneNumber'],datetime.now().strftime("%y-%m-%d %H:%M:%S")))
					mydb.commit()
			except requests.exceptions.RequestException:
				pass
		cursorLocal.close()

	print(json.dumps(dronesJson))

if __name__ == "__main__":
	main()
# print(f"""{{'1':{psw}}}""")
# print(f"""{{'1':1}}""")
