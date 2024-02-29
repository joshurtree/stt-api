import requests
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import json
import subprocess
import os
import traceback
from dataclasses import asdict, dataclass 
from datetime import datetime, timedelta, timezone

app = Flask('stt-api')
voyage_ids = dict()

class ClientException(Exception) :
    def __init__(self, message) :
        self.message = message

BASE_URL = 'https://app.startrektimelines.com/'
PLAYERFILE_URL = BASE_URL + 'player'
VOYAGE_URL = BASE_URL + 'voyage/refresh'
LOGIN_PAGE = BASE_URL + 'users/auth'
#LOGIN_URL = 'https://thorium.disruptorbeam.com/oauth2/token'

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
        
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
    return jsonify({
        "status_code": response.status_code, 
        "message": response.text  
    })

def fetchDefaultParams() :
    if not 'access_token' in request.args :
        raise ClientException("Access token is required.")
    
    if not 'STT_API_VERSION' in os.environ and not 'stt_api_version' in request.args :
        raise ClientException('Parameter stt_api_version is required')
    client_api = request.args['stt_api_version']  if 'stt_api_version' in request.args else os.environ['STT_API_VERSION']
 
    return {
        'access_token': request.args['access_token'],
        'client_api': client_api
    }

def processRequest(callback) :
    def request() :
        params = fetchDefaultParams()
        params['only_read_state'] = True
        return requests.get(PLAYERFILE_URL, params)
    
    def storeVoyageIdAndDoCallback(pf) :
        params = fetchDefaultParams()
        voyage = pf['player']['character']['voyage']
        if len(voyage) > 0 :
            voyage_ids[params['access_token'][:-10]] = voyage[0]['id']
        return callback(pf)
    
    return processCustomRequest(request, storeVoyageIdAndDoCallback)

def processCustomRequest(request, callback) :
    try :
        response = request() 
        return callback(response.json()) if response.ok else responseToJson(response)
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
    def request() :
        payload = fetchDefaultParams()
        user_key = payload['access_token'][:-10]
        if user_key not in voyage_ids :
            processRequest(lambda pf : pf)
            if user_key not in voyage_ids :
                raise ClientException('No voyage running')
        payload['voyage_status_id'] = voyage_ids[user_key]
        return  requests.post(VOYAGE_URL, payload)
    
    return processCustomRequest(request, lambda pf : pf[0]['character']['voyage'][0])

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

CONTAINER_FILL_SECONDS = timedelta(hours=10).seconds
FILL_RATE = CONTAINER_FILL_SECONDS/100
@app.get("/containers")
def containers() :
    fill_states = [ "Cooldown", "Filling", "Full"]
    request = lambda : requests.get(BASE_URL + 'continuum/containers', fetchDefaultParams())
    def processResult(res) :
        containers = res['character']['continuum_containers']
        output = []
        for i in range(len(containers['auto_fill_starts'])) :
            fill_duration = datetime.now(timezone.utc) - datetime.fromisoformat(containers['auto_fill_starts'][i])
            output.append({
                "time_util_full": CONTAINER_FILL_SECONDS - fill_duration.seconds - containers['manual_fill_counts'][i]*FILL_RATE, 
                "fill_count": max([fill_duration.seconds//FILL_RATE + containers['manual_fill_counts'][i], 0]),
                "fill_state":fill_states[(fill_duration.seconds//CONTAINER_FILL_SECONDS) + 1]
            })

        return output 

    return processCustomRequest(request, processResult)