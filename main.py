import spotipy
import math
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id='bfa5db923dc040808cb9f2364bba9957',
    client_secret='0e1e4504bbf443b1b82dae2e792a91fe',
    redirect_uri='http://127.0.0.1:8888/callback',
    scope='playlist-modify-public',
    cache_path='./cache.txt',
    requests_timeout=10,
))

print("This script will create a new playlist based on the genres of tracks in an existing playlist.")
print("Enter the playlist link:")
print("Please wait")
playlist_link = input()  # e.g., "https://open.spotify.com/playlist/0xVAAltZaAzHBMJE7t3sRU"

playlist_URI = playlist_link.split("/")[-1].split("?")[0]

playlist = sp.playlist(playlist_URI)
playlist_length = playlist['tracks']['total']
print(f"Playlist length: {playlist_length} tracks")
print("Fetching tracks and genres... (This may take a while for large playlists)")

lim = 100

tracks = []

off = 0

iterations = math.ceil(playlist_length / lim)
for i in range(iterations): # len(liked2)/100
    tracks += [x["track"] for x in sp.playlist_tracks(playlist_id=playlist_URI, limit=lim, offset=off)["items"]]
    off+=100



un_genres = set()
tracks_with_genres = {} # important for later, to not call spotify api twice for the same track

for track in tracks:

        track_uri = track["uri"]


        artist_uri = track["artists"][0]["uri"]
        artist_genres = sp.artist(artist_uri)["genres"]

        tracks_with_genres[track_uri] = artist_genres

        for genre in artist_genres:
            genre = genre.lower()
            un_genres.add(genre)
            
print(f"Unique genres found: {len(un_genres)}")
for i, genre in enumerate(un_genres):
    print(f"{i+1}. {genre}")

uris = []
print("Do you want to include or exclude genres from the original playlist? (Type 'include' or 'exclude')")

choice = input().lower()
if choice == 'include':
    print("Enter the genres you want to include (comma-separated names of genres):")
    selected_genres = input().lower().split(",")

    for track_uri, genres in tracks_with_genres.items():
        for genre in genres:
            genre = genre.lower()
            if genre in selected_genres:
                uris.append(track_uri)
                break
elif choice == 'exclude':
    print("Enter the genres you want to exclude (comma-separated names of genres):")
    selected_genres = input().lower().split(",")

    for track_uri, genres in tracks_with_genres.items():
        exclude = False
        for genre in genres:
            genre = genre.lower()
            if genre in selected_genres:
                exclude = True
                break
        if not exclude:
            uris.append(track_uri)

print(f"Total tracks matching selected genres: {len(uris)}")
print("What is the name of the new playlist?")
new_playlist_name = input()

iterations = math.ceil(len(uris) / lim)
try:
    new_playlist = sp.user_playlist_create(user=sp.current_user()["id"], name=new_playlist_name, public=True)
    for i in range(iterations):
        batch_uris = uris[i*lim:(i+1)*lim]
        sp.playlist_add_items(new_playlist['id'], batch_uris)
        print(f"Playlist '{new_playlist_name}' created successfully.")


except Exception as e:
    print(f"Error creating playlist: {e}")

