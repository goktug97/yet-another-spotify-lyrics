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
atexit.register(show_cursor)

def move_cursor(x, y):
    sys.stdout.write(f"\033[{y};{x}H")

def delete_line():
    sys.stdout.write('\x1b[2K')

def boldify(string):
    return f'\033[1m{string}\033[0m'

def fetch_lyrics(artist, title):
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

def terminal_size():
    rows, columns = map(int, os.popen('stty size', 'r').read().split())
    return rows, columns

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


class Spotify(object):
    def __init__(self):
        session_bus = dbus.SessionBus()
        try:
            self.spotify_bus = session_bus.get_object(
                "org.mpris.MediaPlayer2.spotify",
                "/org/mpris/MediaPlayer2")
        except dbus.exceptions.DBusException:
            sys.exit("Can't access to Spotify DBUS")
        self.player_interface = dbus.Interface(
            self.spotify_bus, dbus_interface='org.mpris.MediaPlayer2.Player')
        self.properties_interface = dbus.Interface(
            self.spotify_bus, "org.freedesktop.DBus.Properties")

    def metadata(self):
        metadata = self.properties_interface.Get(
            "org.mpris.MediaPlayer2.Player", "Metadata")
        title = metadata['xesam:title'].replace("&", "&amp;")
        artist = metadata['xesam:artist'][0].replace("&", "&amp;")
        album = metadata['xesam:album'].replace("&", "&amp;")
        art_url = metadata['mpris:artUrl'].replace("&", "&amp;")
        return title, artist, album, art_url

    def next(self):
        self.player_interface.Next()

    def prev(self):
        self.player_interface.Previous()

    def toggle(self):
        self.player_interface.PlayPause()

class Lyrics(object):
    def __init__(self):
        self.spotify = Spotify()
        self.home = str(Path.home())

    def update_directories(self):
        self.lyrics_directory = os.path.join(self.home, '.cache', 'spotify-lyrics')
        self.artist_directory = os.path.join(
            self.lyrics_directory, self.artist.replace('/', ''))
        self.album_directory = os.path.join(
            self.artist_directory, self.album.replace('/', ''))
        self.image_directory = os.path.join(self.artist_directory, 'album_arts')
        self.lyrics_file = os.path.join(
            self.album_directory, self.song.replace('/', ''))
        self.image_file = f'{os.path.join(self.image_directory, self.album)}.png'

        if not os.path.isdir(self.lyrics_directory): os.mkdir(self.lyrics_directory)
        if not os.path.isdir(self.artist_directory): os.mkdir(self.artist_directory)
        if not os.path.isdir(self.album_directory): os.mkdir(self.album_directory)
        if not os.path.isdir(self.image_directory): os.mkdir(self.image_directory)

        try:
            if not os.path.exists(self.image_file):
                urlretrieve(self.art_url, self.image_file)
        except FileNotFoundError:
            pass
        except urllib.error.URLError:
            pass

    def print_metadata(self):
        print(f'\033[95mArtist: {self.artist}\033[0m')
        print(f'\033[95mAlbum: {self.album}\033[0m')
        print(f'\033[95mSong: {self.song}\033[0m')

    def read_lyrics(self):
        with open(self.lyrics_file, 'r') as f:
            lyrics = ''.join(f.readlines())
        return lyrics

    def save_lyrics(self):
        with open(self.lyrics_file, 'w') as f:
            f.write(self.lyrics)

    def update_lyrics(self):
        if not os.path.exists(self.lyrics_file):
            self.lyrics = fetch_lyrics(self.artist, self.song)
            self.save_lyrics()
        else:
            self.lyrics = self.read_lyrics()

    @ueberzug.Canvas()
    def main(self, canvas):
        self.rows, self.columns = terminal_size()
        self.song, self.artist, self.album, self.art_url = self.spotify.metadata()

        self.update_directories()

        self.update_lyrics()

        album_cover = canvas.create_placement(
            'album_cover',
            x=self.columns//2, y=4,
            scaler=ueberzug.ScalerOption.COVER.value)
        album_cover.path = self.image_file
        album_cover.visibility = ueberzug.Visibility.VISIBLE

        hide_cursor()

        os.system('clear')
        move_cursor(0, 0)
        self.print_metadata()

        current_line = 0
        start_row = 5

        with KeyPoller() as key_poller:
            while True:
                song, artist, album, art_url = self.spotify.metadata()
                if self.song != song or self.artist != artist:
                    self.song = song
                    self.artist = artist
                    self.album = album
                    self.art_url = art_url
                    self.update_directories()
                    self.update_lyrics()

                    album_cover.path = self.image_file

                    os.system('clear')
                    move_cursor(0, 0)
                    self.print_metadata()

                rows, columns = terminal_size()
                if self.rows != rows or self.columns != columns:
                    difference = rows - self.rows
                    self.rows, self.columns = rows, columns
                    if difference > 0:
                        current_line -= difference
                        current_line = max(0, current_line)
                        current_line = min(current_line, len(wrapped_lines)-1)
                    album_cover.x = self.columns//2

                    os.system('clear')
                    move_cursor(0, 0)
                    self.print_metadata()

                lines = self.lyrics.split('\n')
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

                key = key_poller.poll()
                if key == 'q':
                    os.system('clear')
                    break
                elif key == 'j':
                    if rows - start_row == n_entries:
                        current_line += 1
                        current_line = min(current_line, len(wrapped_lines)-1)
                elif key == 'k':
                    current_line += -1
                    current_line = max(current_line, 0)
                elif key == 'e':
                    try:
                        EDITOR = os.environ.get('EDITOR')
                        call([EDITOR, self.lyrics_file])
                        self.update_lyrics()
                        hide_cursor()
                    except TypeError:
                        os.system('clear')
                        print('$EDITOR is not set')
                        time.sleep(1)
                elif key == 'r':
                    os.system('clear')
                    move_cursor(0, 0)
                    self.print_metadata()
                elif key == 'd':
                    os.remove(self.lyrics_file)
                    self.update_lyrics()
                elif key == 'n':
                    self.spotify.next()
                elif key == 'p':
                    self.spotify.prev()
                elif key == 't':
                    self.spotify.toggle()

def main():
    Lyrics().main()

if __name__ == '__main__':
    main()
