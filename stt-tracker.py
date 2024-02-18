import requests
from flask import Flask, request
from bs4 import BeautifulSoup
import json
import asyncio
import glob
import subprocess
import os

app = Flask(__name__)
accounts = dict()

PLAYERFILE_URL = f"https://app.startrektimelines.com/player?client_api={os.environ["STT_API"]}&only_read_state=true"
PROD_URL = "https://app.startrektimelines.com/"
LOGIN_PAGE = 'https://app.startrektimelines.com/users/auth'
LOGIN_URL = 'https://thorium.disruptorbeam.com/oauth2/token'

class STTAccount :
    def __init__(self, token) :
        self.access_token = token
        self.prodProcess = None

    def responseToJson(self, response) :
        return {
            "status_code": response.status_code, 
            "message": response.text  
        }

    async def prod(self) :
        if self.prodProcess :
            self.prodProcess.terminate()

        self.prodProcess = subprocess.Popen('firefox', '-headless', PROD_URL + '?access_token=' + self.access_token)
    
    def processRequest(self, callback) :
        response = requests.get(PLAYERFILE_URL + '&access_token=' + self.access_token)        
        return json.dumps(callback(response.json())) if response.ok else self.responseToJson(response)

def fetchAccount(callback) :
    account = accounts[request.values['account'] if request.values.has_key('account') else 'default']
    if account :
        return callback(account)

    return {"Error" : "Account not found" }, 400

def setup() :
    acc_files = glob.glob('/run/secrets/stt-tracker')

    for acc_file in acc_files :
        accounts[acc_file.split('/')[-1]] = STTAccount(json.loads(acc_file).access_token)

def processRequest(self, callback) :
    fetchAccount(lambda acc : acc.processRequest(callback))

@app.get("/")
def index() :
    return processRequest(lambda pf : pf)

toType = lambda value : value if not value.isdecimal() else int(value)
traverse = lambda path, retval : traverse(path[1:], retval[toType(path[0])]) if len(path) > 0 else retval

@app.get("/pc/<path>") 
def playerCharacterShortcut(path) :
    return processRequest(lambda pf : traverse(path.split('/'), pf['player']['character']))


@app.route('/', defaults={'path': ''})
@app.route('/')
def catch_all(path) :
    try :
        return processRequest(lambda pf : traverse(path.split('/'), pf))
    except :
        return { "error": "Invalid path" }, 400


@app.get("/voyage")
def voyage() :
    try :
        return processRequest(lambda pf : pf['player']['character']['voyage'][0])
    except :
        return { "error": "No voyage running" }, 400 

@app.get("/shuttles") 
def shuttles() :
    return processRequest(lambda pf : pf['player']['character']['shuttle_adventures'])

@app.get("/quantum")
def quantum() :
    return processRequest(lambda pf : pf['crew_crafting_root']['energy'])

@app.get("/prod")
def prod() :
    return fetchAccount(lambda acc : acc.prod())

if __name__ == "__main__" :
    app.run(host="0.0.0.0")