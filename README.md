# CS:GO Spotify controller

A program that pauses your Spotify music when you're alive in a round. But plays it when you're dead or in a freezetime

## Get up and running

- Create an OAuth2 app on [developers.spotify.com](https://developers.spotify.com). Put the secret and id in [`settings.json`](#settingsjson).
- Put `gamestate_integration_music.cfg` in your `cfg` folder (usally `/Steam/steamapps/common/Counter-Strike Global Offensive/csgo/cfg`) folder. Restart the game if it was running.
- Start the script `App.py` and allow it to access Spotify in the browser window that should have popped up.

## `Settings.json`
`settings.json` is used to configure your application. Hera are the `settings.json` properties.

### spotifyAPI

- `clientId` your Spotify OAuth2 client id
- `clientSecret` your Spotify OAuth2 client secret

### refreshToken

- `enabled` dicides wheter you want to save the refresh token or re-authenticate on each launch
- `token` where the application saves your refresh token

### winMusic

- `enabled` diced wheter you want a special track to play when you win a game
- `track` the Spotify URI of the track that should be played
- `startTime` the timestamp of where the track should start playing from

### playbackDevice
- `mode` either `"active"` which will choose the active spotify device, `"choose"` which will let you choose from all of your spotify devices, or `"given"` which will play from the given `deviceId` or let you choose one if none is set.
- `deviceId` where the application saves your device id
