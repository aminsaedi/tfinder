import aiohttp
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from typing import Union
from pyppeteer import launch

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import csv
import mysql.connector
import datetime
import random
import os
import uvicorn
import time
import requests
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    host="192.168.0.121",
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


MAX_RESPONSE_TOKENS = 1000


async def fetch_tweets(name: str):
    params = {
        "api_key": os.getenv("SCRAPER_API_KEY"),
        "user_id": name.strip(),
    }
    tweets = []
    result = requests.get(
        "https://api.scraperapi.com/structured/twitter/v2/tweets", params=params)
    data = result.json()
    tweets.extend([tweet["text"] for tweet in data.get(
        "tweets", []) if not tweet["text"].startswith("RT")])

    params = {
        "api_key": os.getenv("SCRAPER_API_KEY"),
        "user_id": name.strip(),
        "next_cursor": data.get("next_cursor")
    }
    result = requests.get(
        "https://api.scraperapi.com/structured/twitter/v2/tweets", params=params)
    data = result.json()
    tweets.extend([tweet["text"] for tweet in data.get(
        "tweets", []) if not tweet["text"].startswith("RT")])

    return tweets[:2000]


async def get_personality(name: str):
    tweets = await fetch_tweets(name)
    amin = "\n".join(tweets)[:2000]
    prompt = f"متن های توییت کاربر توییتر به صورت زیر است. براساس این متن‌ها شخصیت اون رو با متد یونگی تحلیل کن. همچنین باید تخمین سن و جنسیت کاربر را هم گزارش دهی : \n {amin}"
    max_tokens = MAX_RESPONSE_TOKENS
    chat_completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=[{"role": "system", "content": prompt},
                                         {"role": "user", "content": amin}
                                         ], max_tokens=max_tokens)
    response_text = chat_completion.choices[0].message.content
    return response_text


@app.post("/twitter")
async def analyze_twitter_user(request: Request):
    data = await request.json()

    os.system(
        f"t whois {data['name']} | head -1 | tr -d ' ' | tr -d 'ID' > temp/whois.txt")
    with open('temp/whois.txt', 'r') as file:
        name = file.read().strip()

    result = await get_personality(name)

    print(result)

    return result

    # return result.json()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
