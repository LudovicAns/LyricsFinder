# This is just a training program.
# It's probably bad, be cool with me ! :)
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import requests

# Default dir where store all data of LyricsFinder.
LYRICS_DIR = Path().home() / "LyricsFinder" / "Lyrics"


def write_all_songs(artist_info: tuple, urls: list[str]) -> None:
    """Write all lyrics present in given urls in a directory.

    :param artist_info: information about the artist. Use this format : (artist_name, artist_id)
    :param urls: list of lyrics urls.
    """
    # Create artist directory.
    artist_dir = LYRICS_DIR / artist_info[0]
    artist_dir.mkdir(parents=True, exist_ok=True)

    # For each url we're getting lyrics in all div with class "Lyrics__Container-sc-1ynbvzw-6 jYfhrf".
    # Write the content in file_path.
    for url in urls:
        file_path = artist_dir / (url.split("/")[3].replace("-lyrics", "") + ".txt")
        if file_path.exists():
            print(f"Le chemin {file_path.name} existe déjà.")
            continue
        else:
            print(f"Ecriture de {file_path.name}")

        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        lyrics_containers = soup.findAll("div", class_="Lyrics__Container-sc-1ynbvzw-6 jYfhrf")

        with open(file_path, "x", encoding="utf-8") as file:
            file.write(f"Link to this lyrics on https://genius.com/ :\n  • {url}\n\n")
            for lyrics in lyrics_containers:
                for line in lyrics.stripped_strings:
                    file.write(line + "\n")


def get_all_urls(artist_info: tuple) -> list[str]:
    """Get all lyrics url of an artist.

    :param artist_info: the info of the artist.
    :return: list of url to all his songs.
    """
    urls = []
    page = 1
    # Run this while the "response/next_page" is not null.
    while page is not None:
        # Getting page by requesting Genius API.
        print(f"Récupération des urls sur la page {page}.")
        song_page = requests.get(f"https://genius.com/api/artists/{artist_info[1]}/songs?page={page}&sort=popularity")

        # Exit if error when loading page.
        if song_page.status_code != 200:
            print("Une erreur de chargement est survenue. Le programme va s'arrêter.")
            sys.exit()

        r_json = song_page.json()
        # Getting all songs in the response (max in a page : 20?) for the actual page.
        songs = [song if "url" in song else {} for song in r_json["response"]["songs"]]

        urls.extend([song.get("url") for song in songs])

        # Actualize page (basically an incrementation).
        page = r_json["response"]["next_page"]
    return urls


def ask_for_artist() -> tuple:
    """Ask for an artist to the user.

    :return: artist information (name, id)
    """
    artist_name = None
    artist_id = None
    while True:
        entry = input("Entrez le nom d'un artiste : ")

        # Search user entry in Genius API.
        r = requests.get(f"https://genius.com/api/search/artist?q={entry}")

        # In case where API found 0 potential result we ask again.
        if not r.json()["response"]["sections"][0]["hits"]:
            print("La saisie n'est pas assez précise.")
            continue

        # Getting the first suggestion of Genius API.
        artist_name = r.json()["response"]["sections"][0]["hits"][0]["result"]["name"]
        response = None

        # Ask for the user if the result is his searched artist.
        while response not in ['1', '2']:
            response = input(f"""{artist_name} est bien l'artiste que vous voulez ?
            1. Oui
            2. Non
            >>> """)
        if response == '2':
            continue
        artist_id = r.json()["response"]["sections"][0]["hits"][0]["result"]["id"]
        break
    return tuple([artist_name, artist_id])


artist_infos = ask_for_artist()
write_all_songs(artist_infos, get_all_urls(artist_infos))
