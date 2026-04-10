import json
import lyricsgenius
from dotenv import load_dotenv
import os
from typing import Final
import spotipy
import time
import requests
from colorthief import ColorThief
from io import BytesIO
import re

load_dotenv()

GENIUS_API_TOKEN: Final[str] = os.getenv('GENIUS_TOKEN')
SPOTIFY_CLIENT_ID: Final[str] = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET: Final[str] = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI: Final[str] = os.getenv('SPOTIFY_REDIRECT_URI')

genius = lyricsgenius.Genius(GENIUS_API_TOKEN)

scope = "user-read-currently-playing"

oauth_object = spotipy.SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=scope
)

token_dict = oauth_object.get_access_token()
token = token_dict['access_token']
spotify_object = spotipy.Spotify(auth=token)

songInfo = {
    "songArtImagePath": "",
    "title": "",
    "artist": "",
    "lyrics": "",
    "dominantColor": ""
}

def get_spotify_token():
    global token, spotify_object
    token_dict = oauth_object.get_access_token(as_dict=True)
    token = token_dict['access_token']
    spotify_object = spotipy.Spotify(auth=token)

def get_dominant_color_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_file = BytesIO(response.content)
        color_thief = ColorThief(image_file)
        return color_thief.get_color(quality=1)
    else:
        raise Exception("Failed to download image")

def check_song_change():
    previous_song_name = None

    while True:
        try:
            if oauth_object.is_token_expired(oauth_object.cache_handler.get_cached_token()):
                print("Token abgelaufen, erneuere Token...")
                get_spotify_token()

            current = spotify_object.currently_playing()

            if current and current["item"]:
                current_song_name = current["item"]["name"]
                current_artist_name = ", ".join(
                    artist["name"] for artist in current["item"]["artists"]
                )
                current_primary_artist = current["item"]["artists"][0]["name"]
                track_id = current["item"]["id"]

                if current_song_name != previous_song_name:
                    print(f"Song changed to: {current_song_name} by {current_artist_name}")
                    previous_song_name = current_song_name

                    search_query = f"{current_song_name} by {current_primary_artist}"
                    song = genius.search_song(search_query)

                    if not song and "(" in current_song_name and ")" in current_song_name:
                        cleaned = re.sub(r"\s*\(.*?\)\s*", " ", current_song_name).strip()
                        search_query = f"{cleaned} by {current_primary_artist}"
                        song = genius.search_song(search_query)

                    if song:
                        songInfo["title"] = song.title
                        songInfo["artist"] = song.artist
                        songInfo["songArtImagePath"] = song.song_art_image_url
                        songInfo["lyrics"] = song.lyrics
                        songInfo["dominantColor"] = get_dominant_color_from_url(song.song_art_image_url)

                    else:
                        search_query_without_artist = current_song_name
                        song = genius.search_song(search_query_without_artist)

                        if song:
                            songInfo["title"] = song.title
                            songInfo["artist"] = song.artist
                            songInfo["songArtImagePath"] = song.song_art_image_url
                            songInfo["lyrics"] = song.lyrics
                            songInfo["dominantColor"] = get_dominant_color_from_url(song.song_art_image_url)
                        else:
                            songInfo["title"] = current_song_name
                            songInfo["artist"] = current_artist_name
                            songInfo["songArtImagePath"] = (
                                "https://clipartcraft.com/images/spotify-logo-transparent-icon-2.png"
                            )
                            songInfo["lyrics"] = "No lyrics found..."
                            songInfo["dominantColor"] = (0, 0, 0)

                    with open("website/songJSON.json", "w") as outfile:
                        json.dump(songInfo, outfile, indent=5)

            time.sleep(5)

        except Exception as e:
            print(f"Fehler: {e}")
            time.sleep(5)

# Start
get_spotify_token()
check_song_change()
