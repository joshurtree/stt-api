import requests
from flask import Flask, request
from bs4 import BeautifulSoup
import json

app = Flask(__name__)

def responseToJson(response) :
    return {
        "status_code": response.status_code, 
        "message": response.text  
    }

PLAYERFILE_URL = "https://app.startrektimelines.com/player?client_api=20&only_read_state=true"
LOGIN_PAGE = 'https://app.startrektimelines.com/users/auth'
LOGIN_URL = 'https://games.disruptorbeam.com/auth/authenticate/userpass'
def login(session) :

    login_page = session.get(PLAYERFILE_URL)
    #soup = BeautifulSoup(login_page.content, 'html.parser')
    login_payload = {
        'username': request.authorization['username'],
        'password': request.authorization['password'],
        'client_id': '1425f8c5-b07f-45ba-b490-3dfd4561d5cf',
        'grant_type': 'password'  
    }
 
    # Send a POST request to login
    login_response = session.post('https://thorium.disruptorbeam.com/oauth2/token', data=login_payload)
    return login_response

def processRequest(callback) :
    session = requests.Session()
    loginRes = login(session)
    print(loginRes.json())

    if (loginRes.ok) :
        response = session.get(PLAYERFILE_URL + '&access_token=' + loginRes.json()['access_token'])
        return json.dumps(callback(response.json())) if response.ok else responseToJson(response)
        
    return responseToJson(loginRes)

@app.route("/")
def index() :
    return "<html><head><title>Hi there.</title></head><body><h1>Hello World</h1></body></html>"


@app.route("/playername") 
def playerName() :
    return processRequest(lambda pf : pf.player.character.display_name)

@app.route("/playerfile")
def playerFile() :
    return processRequest(lambda pf : pf)

@app.route("/voyage")
def voyage() :
    return processRequest(lambda pf : pf['player']['character']['voyage'][0])

@app.route("/shuttles") 
def shuttles() :
    return processRequest(lambda pf : pf['player']['character']['shuttle_adventures'])

@app.route("/quantum")
def quantum() :
    return processRequest(lambda pf : pf['crew_crafting_root']['energy'])

if __name__ == "__main__" :
    app.run(host="0.0.0.0")