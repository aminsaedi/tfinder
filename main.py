from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import csv
import mysql.connector
import datetime
import random
import os

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    'https://home.aminsaedi.bio/'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="example",
    database="twitter"
)


@app.get("/")
def read_root():
    print("Hello World")
    with open('temp/search.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        # strucre of csv file:
        # ID,Posted at,Screen name,Text
        # db structure:
        # id, posted_at, screen_name, text

        # read each row if it doesn't exist in db, insert it
        db.reconnect()
        cursor = db.cursor()
        total = 0
        for row in reader:
            if row[0] == 'ID':
                continue
            query = f"SELECT COUNT(*) FROM search WHERE id='{row[0]}'"
            cursor.execute(query)
            result = cursor.fetchone()
            # date time format: 2023-06-08 21:31:36 +0000
            if result[0] == 0:
                query = f"INSERT INTO search(id, posted_at, screen_name, text) VALUES('{row[0]}', '{datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S %z')}', '{row[2]}', '{row[3]}')"
                cursor.execute(query)
                db.commit()
                total += 1
            else:
                print(f"ID: {row[0]} already exists in db")
                print(random.randint(0, 100))

    return {"total": total}


@app.get("/whois/{screen_name}")
def read_whois(screen_name: str):
    # run "t whois <screen_name>" and return the result
    os.system(f"t whois {screen_name} > temp/whois.txt")
    with open('temp/whois.txt', 'r') as file:
        data = file.read()
    return {"result": data}


@app.get("/run")
def run():
    # run "t whois <screen_name>" and return the result
    os.system(f't search all "مونترال" -n 100 --csv > temp/search.csv')
    return {"result": "done"}
