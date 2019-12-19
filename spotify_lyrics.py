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

import utils

atexit.register(utils.show_cursor)

class Lyrics(object):
    def __init__(self):
        self.spotify = utils.Spotify()
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
            self.lyrics = utils.fetch_lyrics(self.artist, self.song)
            self.save_lyrics()
        else:
            self.lyrics = self.read_lyrics()

    @ueberzug.Canvas()
    def main(self, canvas):
        self.rows, self.columns = utils.terminal_size()
        self.song, self.artist, self.album, self.art_url = self.spotify.metadata()

        self.update_directories()

        self.update_lyrics()

        album_cover = canvas.create_placement(
            'album_cover',
            x=self.columns//2, y=4,
            scaler=ueberzug.ScalerOption.COVER.value)
        album_cover.path = self.image_file
        album_cover.visibility = ueberzug.Visibility.VISIBLE

        utils.hide_cursor()

        os.system('clear')
        utils.move_cursor(0, 0)
        self.print_metadata()

        current_line = 0
        start_row = 5

        with utils.KeyPoller() as key_poller:
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
                    utils.move_cursor(0, 0)
                    self.print_metadata()

                rows, columns = utils.terminal_size()
                if self.rows != rows or self.columns != columns:
                    difference = rows - self.rows
                    self.rows, self.columns = rows, columns
                    if difference > 0:
                        current_line -= difference
                        current_line = max(0, current_line)
                        current_line = min(current_line, len(wrapped_lines)-1)
                    album_cover.x = self.columns//2

                    os.system('clear')
                    utils.move_cursor(0, 0)
                    self.print_metadata()

                lines = self.lyrics.split('\n')
                wrapped_lines = []
                for line in lines:
                    wrapped_lines.extend(
                        textwrap.fill(line, columns//2-2).split('\n'))

                utils.move_cursor(0, start_row)
                n_entries = min(rows+current_line-start_row,
                                len(wrapped_lines)) - current_line
                for i in range(current_line, current_line + n_entries):
                    utils.delete_line()
                    print(utils.boldify(wrapped_lines[i]))
                utils.move_cursor(0, n_entries+start_row)
                utils.delete_line()

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
                        utils.hide_cursor()
                    except TypeError:
                        os.system('clear')
                        print('$EDITOR is not set')
                        time.sleep(1)
                elif key == 'r':
                    os.system('clear')
                    utils.move_cursor(0, 0)
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
