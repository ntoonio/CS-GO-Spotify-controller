# CS:GO Spotify controller

A program that pauses your Spotify music when you're alive in a round. But plays it when you're dead or in a freezetime

## Get up and running

- Create an OAuth2 app on [developers.spotify.com](https://developers.spotify.com). Put the secret and id in `Keys.py`.
- Put `gamestate_integration_music.cfg` in your `cfg` folder (usally `/Steam/steamapps/common/Counter-Strike Global Offensive/csgo/cfg`) folder. Restart the game if it was running.
- Start the script `App.py` and allow it to access Spotify in the browser window that should have popped up.
