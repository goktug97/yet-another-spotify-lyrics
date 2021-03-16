#!/usr/bin/env python3

import os
import re
import select
import sys
import textwrap
import urllib.parse
from pathlib import Path
from urllib.request import urlretrieve

import dbus
import requests
from bs4 import BeautifulSoup

import utils

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

        if not os.path.isdir(self.lyrics_directory): os.mkdir(self.lyrics_directory)
        if not os.path.isdir(self.artist_directory): os.mkdir(self.artist_directory)
        if not os.path.isdir(self.album_directory): os.mkdir(self.album_directory)

    def print_metadata(self):
        print(f'Artist: {self.artist}')
        print(f'Album: {self.album}')
        print(f'Song: {self.song}\n')

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

    def main(self):
        self.song, self.artist, self.album, self.art_url = self.spotify.metadata()
        self.update_directories()
        self.update_lyrics()
        self.print_metadata()
        lines = self.lyrics.split('\n')
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(
                textwrap.fill(line, 50).split('\n'))

        for i in range(len(wrapped_lines)):
            print(wrapped_lines[i])

def main():
    Lyrics().main()

if __name__ == '__main__':
    main()
