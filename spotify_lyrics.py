#!/usr/bin/env python3

import atexit
import os
import re
import select
import sys
import termios
import textwrap
import time
import urllib.parse
from pathlib import Path
from subprocess import call
from urllib.request import urlretrieve

import dbus
import requests
import ueberzug.lib.v0 as ueberzug
from bs4 import BeautifulSoup

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def move_cursor(x, y):
    sys.stdout.write(f"\033[{y};{x}H")

def delete_line():
    sys.stdout.write('\x1b[2K')

def boldify(string):
    return f'\033[1m{string}\033[0m'

class KeyPoller():
    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)
        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def poll(self):
        dr,dw,de = select.select([sys.stdin], [], [], 0.0)
        return sys.stdin.read(1) if not dr == [] else None

def get_lyrics(artist, title):
    title = re.sub(r'(-.*)', '', title)
    search_string = f'{artist} {title} lyrics'
    search_string = urllib.parse.quote_plus(search_string)
    url = 'https://google.com/search?q=' + search_string
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "lxml", from_encoding='UTF-8')
    raw_lyrics = (soup.findAll('div', attrs={'class': 'hwc'}))
    final_lyrics = str.join(u'\n', map(str, raw_lyrics))
    final_lyrics = re.sub(r'<(.*)>', '', string=final_lyrics)
    final_lyrics = '\n'.join(final_lyrics.split('\n')[:-2])
    return final_lyrics

def get_spotify_song_data():
    session_bus = dbus.SessionBus()
    try:
        spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify",
                                             "/org/mpris/MediaPlayer2")
    except dbus.exceptions.DBusException:
        sys.exit("Can't access to Spotify DBUS")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")
    title = metadata['xesam:title'].replace("&", "&amp;")
    artist = metadata['xesam:artist'][0].replace("&", "&amp;")
    album = metadata['xesam:album'].replace("&", "&amp;")
    art_url = metadata['mpris:artUrl'].replace("&", "&amp;")
    return title, artist, album, art_url

def terminal_size():
    rows, columns = map(int, os.popen('stty size', 'r').read().split())
    return rows, columns

def print_metadata(artist, album, song):
    print(f'\033[95mArtist: {artist}\033[0m')
    print(f'\033[95mAlbum: {album}\033[0m')
    print(f'\033[95mSong: {song}\033[0m')

def read_lyrics(lyrics_file):
    with open(lyrics_file, 'r') as f:
        lyrics = ''.join(f.readlines())
    return lyrics

def save_lyrics(lyrics, lyrics_file):
    with open(lyrics_file, 'w') as f:
        f.write(lyrics)

atexit.register(show_cursor)

@ueberzug.Canvas()
def main(canvas):
    rows, columns = terminal_size()
    song, artist, album, art_url = get_spotify_song_data()

    home = str(Path.home())
    lyrics_directory = os.path.join(home, '.cache', 'spotify-lyrics')
    artist_directory = os.path.join(lyrics_directory, artist.replace('/', ''))
    image_directory = os.path.join(artist_directory, 'album_arts')
    lyrics_file = os.path.join(artist_directory, song.replace('/', ''))
    image_file = '{}.png'.format(os.path.join(image_directory, album))

    if not os.path.isdir(lyrics_directory): os.mkdir(lyrics_directory)
    if not os.path.isdir(artist_directory): os.mkdir(artist_directory)
    if not os.path.isdir(image_directory): os.mkdir(image_directory)

    if not os.path.exists(lyrics_file):
        lyrics = get_lyrics(artist, song)
        save_lyrics(lyrics, lyrics_file)
    else:
        lyrics = read_lyrics(lyrics_file)

    try:
        if not os.path.exists(image_file):
            urlretrieve(art_url, image_file)
    except FileNotFoundError:
        pass

    album_cover = canvas.create_placement('album_cover',
                                          x=columns//2, y=4,
                                          scaler=ueberzug.ScalerOption.COVER.value)
    album_cover.path = image_file
    album_cover.visibility = ueberzug.Visibility.VISIBLE

    os.system('clear')
    hide_cursor()
    print_metadata(artist, album, song)

    current_line = 0
    start_row = 5

    old_rows, old_columns = rows, columns
    with KeyPoller() as key_poller:
        while True:
            rows, columns = terminal_size()
            if old_rows != rows or old_columns != columns:
                difference = rows - old_rows
                if difference > 0:
                    current_line -= difference
                    current_line = max(0, current_line)
                    current_line = min(current_line, len(wrapped_lines)-1)
                album_cover.x = columns//2

                os.system('clear')
                move_cursor(0, 0)
                print_metadata(artist, album, song)

                old_rows, old_columns = rows, columns

            lines = lyrics.split('\n')
            wrapped_lines = []
            for line in lines:
                wrapped_lines.extend(
                    textwrap.fill(line, columns//2-2).split('\n'))

            move_cursor(0, start_row)
            n_entries = min(rows+current_line-start_row,
                            len(wrapped_lines)) - current_line
            for i in range(current_line, current_line + n_entries):
                delete_line()
                print(boldify(wrapped_lines[i]))
            move_cursor(0, n_entries+start_row)
            delete_line()

            c = key_poller.poll()
            if c == 'q':
                os.system('clear')
                break
            if c == 'j':
                if rows - start_row == n_entries:
                    current_line += 1
                    current_line = min(current_line, len(wrapped_lines)-1)
            if c == 'k':
                current_line += -1
                current_line = max(current_line, 0)
            if c == 'e':
                try:
                    EDITOR = os.environ.get('EDITOR')
                    call([EDITOR, lyrics_file])
                    lyrics = read_lyrics(lyrics_file)
                    hide_cursor()
                except TypeError:
                    os.system('clear')
                    print('$EDITOR is not set')
                    time.sleep(1)
            if c == 'r':
                os.system('clear')
                move_cursor(0, 0)
                print_metadata(artist, album, song)
            if c == 'd':
                os.remove(lyrics_file)
                lyrics = get_lyrics(artist, song)
                save_lyrics(lyrics, lyrics_file)

if __name__ == '__main__':
    main()
