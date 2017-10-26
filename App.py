from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
import time
import webbrowser
import requests
import requests
import base64
import json

playingMusic = False
settings = {}
defaultSettings = {
    "winMusic": {
        "enabled": True,
        "track": "spotify:track:0TtD91m3UCmluyHjbm5k5w",
        "startTime": 93000
    },
    "refreshToken": {
        "enabled": True
    }
}

def MakeGetAuthorizationCodeHandler(OAuth2Class):
    class GetAuthorizationCodeHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return
 
        def do_GET(self):
            parsedPath = urlparse.urlparse(self.path)
           
            for q in parsedPath.query.split("&"):
                kv = q.split("=")
 
                if kv[0] == "code":
                    OAuth2Class.authorizationCode = kv[1]
 
            self.send_response(200)
            self.end_headers()
            self.wfile.write("<script>window.close();</script>")
 
            return
 
    return GetAuthorizationCodeHandler

def MakeGameStateIntegrationHandler(OAuth2Class, deviceId):
    class GetAuthorizationCodeHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            return
 
        def do_POST(self):
            global playingMusic

            parsedPath = urlparse.urlparse(self.path)
           
            contentLength = int(self.headers.getheader("content-length", 0))
            body = json.loads(self.rfile.read(contentLength))
 
            shouldBePlay = shouldPlay(body)

            if shouldBePlay == True and not playingMusic:
                resumeMusic(auth, deviceId)
            elif shouldBePlay == False and playingMusic:
                pauseMusic(auth, deviceId)
            elif shouldBePlay == "win" and not playingMusic == "win":
                playWinMusic(auth, deviceId)

            playingMusic = shouldBePlay

            self.send_response(200)
            self.end_headers()

            return
 
    return GetAuthorizationCodeHandler
 
class OAuth2:
    def __init__(self, clientId, clientSecret, authorizationURL, tokenURL):
        self.clientId = clientId
        self.clientSecret = clientSecret
 
        self.authorizationURL = authorizationURL
        self.tokenURL = tokenURL
 
        self.authorizationCode = ""
 
    def openAuthorizationURL(self, scopes):
        url = self.getAuthorizationURL(scopes)
        webbrowser.open(url)
 
        return self.getAuthorizationCode()
 
    def getAuthorizationURL(self, scopes):
        return authorizationURL + "?" + "scope=" + " ".join(scopes) + "&response_type=code&client_id=" + self.clientId + "&redirect_uri=http://localhost:4074/"
 
    def getAuthorizationCode(self):
        self.authorizationCode = ""
 
        server = HTTPServer(("", 4074), MakeGetAuthorizationCodeHandler(self))
       
        print "Waiting for authorization code"
        while self.authorizationCode == "":
            server.handle_request()
 
        return self.authorizationCode
 
    def getTokens(self):
        data = {"grant_type": "authorization_code", "code": self.authorizationCode, "redirect_uri": "http://localhost:4074/"}
        
        r = requests.post(self.tokenURL, data=data, headers={"Authorization": "Basic " + base64.b64encode(self.clientId + ":" + self.clientSecret)})

        return json.loads(r.text)
 
    def getAccessToken(self, secondTry = False):
        if time.time() >= self.expires and not secondTry:
            print "Access token expired"
            self.refreshAcessToken()
            return self.getAccessToken(secondTry = True)

        return self.accessToken
 
    def refreshAcessToken(self):
        data = {"grant_type": "refresh_token", "refresh_token": self.refreshToken}
        
        r = requests.post(self.tokenURL, data=data, headers={"Authorization": "Basic " + base64.b64encode(self.clientId + ":" + self.clientSecret)})

        tokens = json.loads(r.text)
        
        self.accessToken = tokens["access_token"]
        self.expires = time.time() + tokens["expires_in"]

        print "Refreshed acceses token"

    def authorize(self, scopes, refreshToken = None):
        if not refreshToken == None:
            
            self.refreshToken = refreshToken
            self.refreshAcessToken()
        else:
            self.openAuthorizationURL(scopes)
            tokens = self.getTokens()

            self.accessToken = tokens["access_token"]
            self.refreshToken = tokens["refresh_token"]
            self.expires = time.time() + tokens["expires_in"]
        
        return self.refreshToken

def choseDevice():
    devices = getDevices(auth)
     
    if not "devices" in devices:
        print "No active devices"
        exit()

    for d in devices["devices"]:
        if d["is_active"]:
            return d["id"]

def startGSIServer(oauth, deviceId):
    print "Starting GSI server"
    server = HTTPServer(("", 27375), MakeGameStateIntegrationHandler(oauth, deviceId))
    
    server.serve_forever()

def getDevices(oauth2):
    r = requests.get("https://api.spotify.com/v1/me/player/devices", headers={"Accept": "application/json", "Authorization": "Bearer " + oauth2.getAccessToken()})

    return json.loads(r.text)

def readSettings():
    global settings
    try:
        file = open("settings.json", "r")
        settings = json.load(file)
        
        return True
    except IOError:
        return False

def writeSettings():
    file = open("settings.json", "w")
    json.dump(settings, file, indent=4)
    file.close()

def getSetting(path, s = None):
    if s == None:
        s = settings

    path = path.split("/", 1)

    if len(path) == 1 and path[0] in s:
        return s[path[0]]
    elif path[0] in s:
        return getSetting(path[1], s[path[0]])
    elif path[0] in defaultSettings:
        return getSetting(path[1], defaultSettings[path[0]])
    else:
        return None

def _setSettingRecursive(path, value, s):
    path = path.split("/", 1)

    if not path[0] in s and len(path) > 1:
        s[path[0]] = {}

    if len(path) == 1:
        s[path[0]] = value
    else:
        s[path[0]] = _setSettingRecursive(path[1], value, s[path[0]])

    return s

def setSetting(path, value):
    global settings
    settings = _setSettingRecursive(path, value, settings)
    
    writeSettings()

def playWinMusic(oauth, device):
    # Play track
    r = requests.put("https://api.spotify.com/v1/me/player/play?device_id=" + device, json={"uris": [getSetting("winMusic/track")]}, headers={"Accept": "application/json", "Authorization": "Bearer " + oauth.getAccessToken()})
    
    # Go to chorus
    r = requests.put("https://api.spotify.com/v1/me/player/seek?device_id=" + device + "&position_ms=" + getSetting("winMusic/startTime"), headers={"Accept": "application/json", "Authorization": "Bearer " + oauth.getAccessToken()})

    # Try to find and API to resume the old music

def pauseMusic(oauth, device):
    print "Pausing music"
    r = requests.put("https://api.spotify.com/v1/me/player/pause?device_id=" + device, headers={"Accept": "application/json", "Authorization": "Bearer " + oauth.getAccessToken()})

def resumeMusic(oauth, device):
    print "Resuming music"
    r = requests.put("https://api.spotify.com/v1/me/player/play?device_id=" + device, headers={"Accept": "application/json", "Authorization": "Bearer " + oauth.getAccessToken()})
 
def shouldPlay(body):
    if not "map" in body: # Not in game, prevents errors from trying to access non existing keys in body
        return

    health = body["player"]["state"]["health"]
    roundPhase = body["round"]["phase"]

    if body["map"]["phase"] == "gameover":
        if body["map"]["team_ct"]["score"] == body["map"]["team_t"]["score"]:
            return True

        winner = "CT" if body["map"]["team_ct"]["score"] > body["map"]["team_t"]["score"] else "T"

        if winner == body["player"]["team"]:
            return "win"
        else:
            return True

    if not body["map"]["mode"] == "competitive":
        return True

    if not body["player"]["steamid"] == body["provider"]["steamid"]:
        return True

    if health > 0 and roundPhase == "live":
        return False

    return True

if __name__ == "__main__":
    readSettings()
    
    authorizationURL = "https://accounts.spotify.com/authorize"
    tokenURL = "https://accounts.spotify.com/api/token"
 
    auth = OAuth2(getSetting("spotifyAPI/clientId"), getSetting("spotifyAPI/clientSecret"), authorizationURL, tokenURL)

    refreshToken = None
    
    if getSetting("refreshToken/enabled"):
        refreshToken = getSetting("refreshToken/token")
    
    print "Authorizing Spotify..."
    refreshToken = auth.authorize(["user-modify-playback-state", "user-read-playback-state", "user-modify-playback-state"], refreshToken)
    
    if getSetting("refreshToken/enabled"):
        setSetting("refreshToken/token", refreshToken)    
    
    startGSIServer(auth, choseDevice())
