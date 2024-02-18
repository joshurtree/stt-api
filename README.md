# STTApi

This is a Docker container that provides provides api endpoints to the latest version of your Star Trek Timelines player file.

## Prerequsites
* git
* [Docker](https://docker.com) or [Podman](https://podman.io)
* [Curl](https://curl.se) (aready installed on all Linux, Mac and Windows 10 or later)

## Installation
Make a directory where your access tokens will be stored. This documentation assumes you have used the directory "stt-tokens".
For each account you want access through the api run the command

```
curl -X POST \
    -d 'username=<email>' -d 'password=<password>' -d 'grant_type=password'  \
    https://thorium.disruptorbeam.com/oauth2/token > stt-tokens/<username>
```

where "<email>" and "<password>" are your login credentials for your Star Trek Timelines account. The value of "<username>" can be anything but this documentation assumes you use the username of the account.

## Standalone
To run the container as a standalone container run
```
docker build https://github.com/joshurtree/stt-tracker -t stt-tracker
```
Then
```
docker run -e STT_API=<client_api> -v ./api-tokens:/run/secrets/stt-tracker -p 80:8080 stt-tracker
```
Where "<client_api>" is passed to "https://app.startrektimelines.com?client_api=<client_api>".

## In docker compose
To use the image within docker compose add 

```
secrets:
    <username1>:
        file: stt-tokens/<username1>
    <username2>:
        file: stt-tokens/<username2>

services:
    stt-tracker:
        build: https://github.com/joshurtree/stt-tracker
        ports:
            - 80:8080
        environment:
            STT_API: <client_api>
        secrets:
            - <username1>
            - <username2>
```

## Usage
The following api endpoints are provided

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

### /quantum
Shortcut to `crew_crafting_root.energy`