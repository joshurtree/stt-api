# STTApi

This is a Docker container that provides provides api endpoints to the latest version of your Star Trek Timelines player file.

## Prerequsites
* [Docker](https://docker.com) or [Podman](https://podman.io)
* [Curl](https://curl.se) (aready installed on all Linux, Mac and Windows 10 or later)

## Retriveing an access for you account  
Run the command
```
curl -X POST \
    -d 'username=<email>' -d 'password=<password>' -d 'grant_type=password'  \
    https://thorium.disruptorbeam.com/oauth2/token 
```
where "<email>" and "<password>" are your login credentials for your Star Trek Timelines account. This a
For any addional accounts replace "default" with a custom name. This produces the output along t
```
{"access_token":"<access_token>","expires_in":864000000,"refresh_token":"<refresh_token>","token_type":"Bearer"}
```
Copy <access_token> for future use. 

## Installation
### Using Docker
To run the container as a standalone container run
```
docker build https://github.com/joshurtree/stt-api.git -t stt-api
```
Then
```
docker run -e STT_API_VERSION=<client_api> -p 80:8080 -d stt-api
```
Where "<client_api>" is passed to "https://app.startrektimelines.com?client_api=<client_api>".

### Using Docker Compose
To use the image within docker compose add 

services:
    stt-tracker:
        build: https://github.com/joshurtree/stt-api.git
        ports:
            - 80:8080
        environment:
            STT_API_VERSION: <client_api>
```

## Usage
Calling the api without any arguments will return results based on your main account at "stt-tokens/default". To specify another accout add "?access_token=<access_token>" to the url. The following api endpoints are provided

### /
The root simply returns the entire player file

### /\<path\>
This fetches the section of the player file specified by the <path> element. Some examples are 
`/player/character/player_name` which returns `player.character.player_name` and `/player/character/shuttle_adventures/0`
which returns `player.character.shuttle_adventures[0]`

### /pc/\<path\>
As above but this is a shortcut to `player.character.<path>`

### /voyage
Shortcut to `player.character.voyage[0]`

### /shuttles
Shortcut to `player.character.shuttle_adventures`

### /currencies
Returns quantities of each of chronitons, credits, honor, quantum and dilithium.

### /tickets
Returns the number of tickets you have for cadet missions, ship battles, replications and boss battles.

### /containers
Returns the current state of the continuum containers.