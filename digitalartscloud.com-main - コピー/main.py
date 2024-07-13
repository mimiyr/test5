import json
import requests
import urllib.parse
import time
import datetime
import random
from functools import lru_cache
from fastapi import FastAPI, Response, Cookie, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/css", StaticFiles(directory="./css"), name="static")
app.mount("/blog", StaticFiles(directory="./blog", html=True), name="static")
template = Jinja2Templates(directory='templates').TemplateResponse

MAX_API_WAIT_TIME = 3
MAX_TIME = 10
APIS = [
"https://youtube.076.ne.jp/",
"https://vid.puffyan.us/",
"https://inv.riverside.rocks/",
]

class APItimeoutError(Exception):
pass

def is_json(json_str):
try:
json.loads(json_str)
return True
except json.JSONDecodeError:
return False

def apirequest(api, url):
try:
res = requests.get(api + url, timeout=MAX_API_WAIT_TIME)
if res.status_code == 200 and is_json(res.text):
return res.text
except requests.RequestException:
pass
return None

@app.get("/", response_class=HTMLResponse)
def home(response: Response, request: Request, yuki: str = Cookie(None)):
if yuki != "True":
return RedirectResponse("/blog")
response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
return template("home.html", {"request": request})

@app.get('/watch', response_class=HTMLResponse)
def video(v: str, response: Response, request: Request, yuki: str = Cookie(None), proxy: str = Cookie(None)):
if yuki != "True":
return RedirectResponse("/")
response.set_cookie(key="yuki", value="True", max_age=7*24*60*60)
videoid = v
t = get_data(videoid)
response.set_cookie("yuki", "True", max_age=60 * 60 * 24 * 7)
return template('video.html', {"request": request, "videoid": videoid, "videourls": t[1], "res": t[0], "description": t[2], "videotitle": t[3], "authorid": t[4], "authoricon": t[6], "author": t[5], "proxy": proxy})

@lru_cache(maxsize=128)
def get_data(videoid):
t = json.loads(apirequest(APIS[0], r"api/v1/videos/" + urllib.parse.quote(videoid)))
return [
{"id": i["videoId"], "title": i["title"], "authorId": i["authorId"], "author": i["author"]} for i in t["recommendedVideos"]
], list(reversed([i["url"] for i in t["formatStreams"]]))[:2], t["descriptionHtml"].replace("\n", "<br>"), t["title"], t["authorId"], t["author"], t["authorThumbnails"][-1]["url"]