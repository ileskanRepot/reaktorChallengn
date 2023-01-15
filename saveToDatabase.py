#!/usr/bin/python3
import requests
import datetime
import mysql.connector
import xml.etree.ElementTree as ET

from math import sqrt
from time import time as tm, sleep as sleep

pswLocation = "/home/ileska/psw/mysql.txt"
lastFecthedLocation = "/home/ileska/ileska.luntti.net/reaktor/lastFetched.txt"

def getDronePositions(url):
	req = requests.get(url)

	if req.status_code != 200:
		exit()

	return (req.text)

def getViolantingDrones(xml,middle,radius):
	violanting = []
	root = ET.fromstring(xml)
	time = root[1].attrib
	time_obj = datetime.datetime.strptime(time['snapshotTimestamp'],'%Y-%m-%dT%H:%M:%S.%fZ')
	for drone in root[1]:
		y = float(drone.find('positionY').text)/1000
		x = float(drone.find('positionX').text)/1000
		# ET.dump(drone)
		dist = (middle[0] - x)**2 + (middle[1] - y)**2
		if dist <= (radius)**2:
			violanting.append([drone.find('serialNumber').text, round(x), round(y), round(sqrt(dist))])

	return (time_obj, violanting)

def writeToSql(time, drones):
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
	sql = "INSERT INTO ViolentDrones (serialNro, coordX, coordY, dist, timestamp) VALUES (%s, %s, %s, %s, %s)"
	for drone in drones:
		val = (drone[0], drone[1], drone[2], drone[3], time)
		cursor.execute(sql, val)
	mydb.commit()
	return cursor.rowcount

def removeOldSql():
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
	timeTenMinutesAgo = datetime.datetime.utcnow() - datetime.timedelta(minutes=10)
	sql = "DELETE FROM ViolentDrones WHERE timestamp < %s"
	val = (timeTenMinutesAgo.strftime("%y-%m-%d %H:%M:%S"),)
	cursor.execute(sql, val)
	mydb.commit()

	sql = "DELETE FROM ViolentUsers WHERE timestamp < %s"
	val = (timeTenMinutesAgo.strftime("%y-%m-%d %H:%M:%S"),)
	cursor.execute(sql, val)
	mydb.commit()

def main():
	middle = (250,250)
	radius = 100
	
	dronesUrl = "https://assignments.reaktor.com/birdnest/drones"
	print("Time, rows added")
	while True:
		with open(lastFecthedLocation, 'r') as fil:
			lastFetched = datetime.datetime.strptime(fil.read(),"%Y-%m-%d %H:%M:%S.%f")
		if lastFetched < datetime.datetime.now() - datetime.timedelta(minutes=60):
			sleep(10)
			continue
		drones = getDronePositions(dronesUrl)
		time, violents = getViolantingDrones(drones, middle, radius)

		affectedRows = writeToSql(time, violents)
		print(datetime.datetime.now() ,affectedRows)
		removeOldSql()
		sleep(1)

if __name__ == "__main__":
	main()

