import json
import lyricsgenius
from dotenv import load_dotenv
import os
from typing import Final
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import requests
from colorthief import ColorThief
from io import BytesIO
import re  # Import the regex module for handling parentheses

load_dotenv()
GENIUS_API_TOKEN: Final[str] = os.getenv('GENIUS_TOKEN')
SPOTIFY_CLIENT_ID: Final[str] = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET: Final[str] = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI: Final[str] = os.getenv('SPOTIFY_REDIRECT_URI')

genius = lyricsgenius.Genius(GENIUS_API_TOKEN)
spotify_client_id = SPOTIFY_CLIENT_ID
spotify_client_secret = SPOTIFY_CLIENT_SECRET
spotify_redirect_uri = SPOTIFY_REDIRECT_URI

scope = "user-read-currently-playing"

oauth_object = spotipy.SpotifyOAuth(client_id=spotify_client_id,  
                             client_secret=spotify_client_secret,
                             redirect_uri=spotify_redirect_uri,
                             scope=scope)

token_dict = oauth_object.get_access_token()
token = token_dict['access_token']

spotify_object = spotipy.Spotify(auth=token)


songInfo = {
    "songArtImagePath": "",
    "title": "",
    "artist": "",
    "lyrics": "",
    "dominantColor": "",
    "embed": "",
    "latestSongs": []  # Add a list to store the latest 5 songs
}

def get_spotify_token():
    global token, spotify_object
    token_dict = oauth_object.get_access_token(as_dict=True)
    token = token_dict['access_token']
    spotify_object = spotipy.Spotify(auth=token)

def check_song_change():
    previous_song_name = None

    while True:
        try:
            # Aktualisiere den Token, falls er abgelaufen ist
            if oauth_object.is_token_expired(oauth_object.cache_handler.get_cached_token()):
                print("Token abgelaufen, erneuere Token...")
                get_spotify_token()

            current = spotify_object.currently_playing()
            if current and current["item"]:
                current_song_name = current["item"]["name"]
                current_artist_name = ", ".join([artist["name"] for artist in current["item"]["artists"]])
                current_primary_artist = current["item"]["artists"][0]["name"]
                track_id = current["item"]["id"]

                if current_song_name != previous_song_name:
                    print(f"Song changed to: {current_song_name} by {current_artist_name}")
                    previous_song_name = current_song_name

                    # Update song info
                    search_query = f"{current_song_name} by {current_primary_artist}"
                    song = genius.search_song(search_query)

                    # If no song is found, check for parentheses and retry
                    if not song and "(" in current_song_name and ")" in current_song_name:
                        # Remove content inside parentheses
                        current_song_name_no_parentheses = re.sub(r"\s*\(.*?\)\s*", " ", current_song_name).strip()
                        print(f"Retrying search without parentheses: {current_song_name_no_parentheses}")
                        search_query = f"{current_song_name_no_parentheses} by {current_primary_artist}"
                        song = genius.search_song(search_query)

                    if song:
                        songInfo["title"] = song.title
                        songInfo["artist"] = song.artist
                        songInfo["songArtImagePath"] = song.song_art_image_url
                        songInfo["embed"] = f"https://open.spotify.com/embed/track/{track_id}"
                        songInfo["lyrics"] = song.lyrics
                        dominant_color = get_dominant_color_from_url(song.song_art_image_url)
                        songInfo["dominantColor"] = dominant_color

                        with open("website/songJSON.json", "w") as outfile:
                            json.dump(songInfo, outfile, indent=5)

                        with open("website/songJSON.json", "r") as json_file:
                            saved_song_data = json.load(json_file)
                        if "Genius" in saved_song_data["artist"] or "Translations" in saved_song_data["artist"]:
                            language_suffixes = ["- english", "- german", "- japanese", "- spanish", "- french"]
                            for suffix in language_suffixes:
                                search_query_with_suffix = f"{current_song_name} by {current_artist_name} {suffix}"
                                print(f"Trying search query: {search_query_with_suffix}")
                                song = genius.search_song(search_query_with_suffix)
                                if song:
                                    songInfo["title"] = song.title
                                    songInfo["artist"] = song.artist
                                    songInfo["songArtImagePath"] = song.song_art_image_url
                                    songInfo["embed"] = f"https://open.spotify.com/embed/track/{track_id}"
                                    songInfo["lyrics"] = song.lyrics
                                    dominant_color = get_dominant_color_from_url(song.song_art_image_url)
                                    songInfo["dominantColor"] = dominant_color
                                    break
                    else:
                        # Try searching without the artist's name
                        search_query_without_artist = current_song_name
                        print(f"Trying search query without artist: {search_query_without_artist}")
                        song = genius.search_song(search_query_without_artist)
                        if song:
                            songInfo["title"] = song.title
                            songInfo["artist"] = song.artist
                            songInfo["songArtImagePath"] = song.song_art_image_url
                            songInfo["embed"] = f"https://open.spotify.com/embed/track/{track_id}"
                            songInfo["lyrics"] = song.lyrics
                            dominant_color = get_dominant_color_from_url(song.song_art_image_url)
                            songInfo["dominantColor"] = dominant_color
                        else:
                            # No song found
                            songInfo["title"] = current_song_name
                            songInfo["artist"] = current_artist_name
                            songInfo["songArtImagePath"] = "https://clipartcraft.com/images/spotify-logo-transparent-icon-2.png"
                            songInfo["embed"] = f"https://open.spotify.com/embed/track/{track_id}"
                            songInfo["lyrics"] = "No lyrics found..."
                            songInfo["dominantColor"] = dominant_color
                    # Add the current song's embed link to the latestSongs list
                    embed_link = songInfo["embed"]
                    if embed_link not in songInfo["latestSongs"]:
                        songInfo["latestSongs"].insert(0, embed_link)  # Add to the beginning of the list
                        if len(songInfo["latestSongs"]) > 5:  # Keep only the latest 5 songs
                            songInfo["latestSongs"].pop()

                    # Save to JSON
                    with open("website/songJSON.json", "w") as outfile:
                        json.dump(songInfo, outfile, indent=5)

            time.sleep(5)

        except Exception as e:
            print(f"Fehler: {e}")
            time.sleep(5)


def get_dominant_color_from_url(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_file = BytesIO(response.content)
        color_thief = ColorThief(image_file)
        dominant_color = color_thief.get_color(quality=1)
        return dominant_color
    else:
        raise Exception("Failed to download image")


# Initialisiere den Token
get_spotify_token()

# Call the function to start monitoring
check_song_change()

