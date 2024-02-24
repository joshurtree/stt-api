import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import json
import subprocess
import os
import traceback
from dataclasses import asdict, dataclass 

app = Flask('stt-api')
prods = dict()

class ClientException(Exception) :
    def __init__(self, message) :
        self.message = message

PLAYERFILE_URL = f"https://app.startrektimelines.com/player?only_read_state=true&client_api={os.environ['STT_API_VERSION']}"
PROD_URL = "https://app.startrektimelines.com/"
LOGIN_PAGE = 'https://app.startrektimelines.com/users/auth'
LOGIN_URL = 'https://thorium.disruptorbeam.com/oauth2/token'

@dataclass
class NumModifier :
    short: str
    long: str


def prettyNumber(value, modType = "long") :
    modifiers = [
        NumModifier("", ""),
        NumModifier("K", " Thousand"),
        NumModifier("M", " Million"),
        NumModifier("B", " Billion"),
        NumModifier("T", " Trillion")
    ]

    numSize = min((len(f"{value}")-1)//3, len(modifiers)-1)
    val = f"{value/(10**(numSize*3)):.3g}"
    mod = asdict(modifiers[numSize])[modType]
    return val + mod

def responseToJson(response) :
    return {
        "status_code": response.status_code, 
        "message": response.text  
    }

def fetchAccessToken() :
    if 'access_token' in request.args :
        return request.args['access_token']
    raise Exception("Access token is required.")

def processRequest(callback) :
    try :
        response = requests.get(PLAYERFILE_URL + '&access_token=' + fetchAccessToken())
        return jsonify(callback(response.json())) if response.ok else responseToJson(response)
    except ClientException as e:
        return {"Error": e.message}, 400
    except Exception as e:
        traceback.print_exception(e)
        return {"Error": "Internal server error"}, 500

# Return whole player file
@app.get("/")
def index() :
    return processRequest(lambda pf : pf)

toType = lambda value : value if not value.isdecimal() else int(value)
traverse = lambda path, retval : traverse(path[1:], retval[toType(path[0])]) if len(path) > 0 else retval

@app.get("/pc/<path>") 
def playerCharacterShortcut(path) :
    return processRequest(lambda pf : traverse(path.split('/'), pf['player']['character']))

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
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

@app.get("/currencies")
def currencies() :
    def getCurrencies(pf) :
        p = pf['player']
        pc = p['character']
        return {
            "chronitons": pc['replay_energy_max'] + pc['replay_energy_overflow'],
            "credits": p['money'],
            "dilithium": p['premium_purchasable'],
            "honor": p['honor'],
            "quantum": pf['crew_crafting_root']['energy']['quantity'],
        }
    
    return processRequest(getCurrencies)

@app.get("/tickets")
def tickets() :
    def getTickets(pf) :
        p = pf['player']
        pc = p['character']

        return {
            "cadets": pc['cadet_tickets']['current'],
            "ship_battles": pc['pvp_tickets']['current'],
            "replicator": p['replicator_limit'] - p['replicator_uses_today'],
            "boss_battles": pf['fleet_boss_battles_root']['fleet_boss_battles_energy']['quantity']
        }
    
    return processRequest(getTickets)