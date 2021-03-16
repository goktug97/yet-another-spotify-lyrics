#!/usr/bin/env python3

import atexit
import os
import textwrap
import threading
import time
import urllib.parse
from pathlib import Path
from subprocess import call
from urllib.request import urlretrieve

import dbus.mainloop.glib
import dbus.service
import ueberzug.lib.v0 as ueberzug
from gi.repository import GLib

import utils


atexit.register(utils.show_cursor)


class Lyrics(dbus.service.Object):
    def __init__(self):
        self.spotify = utils.Spotify()
        self.home = str(Path.home())
        self._current_line = 0
        self.changed = True
        self.album_hidden = False

        self.bus = dbus.SessionBus()
        name = dbus.service.BusName('com.spotify_lyrics.line', bus=self.bus)
        super().__init__(name, '/com/spotify_lyrics')

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

    @property
    def current_line(self):
        return self._current_line

    @current_line.setter
    def current_line(self, value):
        self._current_line = value
        self._current_line = min(self._current_line, self.total_lines-self.n_entries)
        self._current_line = max(self._current_line, 0)
        self.changed = True

    @dbus.service.method('com.spotify_lyrics.line', signature='v')
    def move(self, val):
        self.current_line += max(min(val, 1), -1)

    def print_metadata(self):
        self.changed = True
        os.system('clear')
        utils.move_cursor(0, 0)
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
        self._current_line = 0

    @ueberzug.Canvas()
    def main(self, loop, event, canvas):
        self.rows, self.columns = utils.terminal_size()
        self.song, self.artist, self.album, self.art_url = self.spotify.metadata()

        self.update_directories()

        self.update_lyrics()

        album_cover = canvas.create_placement(
            'album_cover',
            x=self.columns//2, y=4,
            scaler=ueberzug.ScalerOption.COVER.value)
        album_cover.path = self.image_file
        if self.album_hidden:
            album_cover.visibility = ueberzug.Visibility.INVISIBLE
        else:
            album_cover.visibility = ueberzug.Visibility.VISIBLE

        utils.hide_cursor()

        self.print_metadata()

        start_row = 5

        with utils.KeyPoller() as key_poller:
            while event.is_set():
                song, artist, album, art_url = self.spotify.metadata()
                if self.song != song or self.artist != artist:
                    self.song = song
                    self.artist = artist
                    self.album = album
                    self.art_url = art_url
                    self.update_directories()
                    self.update_lyrics()
                    album_cover.path = self.image_file
                    self.print_metadata()

                rows, columns = utils.terminal_size()
                if self.rows != rows or self.columns != columns:
                    difference = rows - self.rows
                    self.rows, self.columns = rows, columns
                    if difference > 0:
                        self.current_line -= difference
                        self.current_line = max(0, self.current_line)
                        self.current_line = min(self.current_line,
                                self.total_lines-self.n_entries)
                    album_cover.x = self.columns//2
                    self.print_metadata()

                if self.changed:
                    lines = self.lyrics.split('\n')
                    wrapped_lines = []
                    for line in lines:
                        wrapped_lines.extend(
                            textwrap.fill(
                                line, (columns if self.album_hidden
                                               else columns//2-2)).split('\n'))
                    self.total_lines = len(wrapped_lines)

                    utils.move_cursor(0, start_row)
                    self.n_entries = min(rows+self.current_line-start_row,
                                    self.total_lines) - self.current_line
                    for i in range(self.current_line,
                                   self.current_line + self.n_entries):
                        utils.delete_line()
                        print(utils.boldify(wrapped_lines[i]))
                    utils.move_cursor(0, self.n_entries+start_row)
                    utils.delete_line()
                    self.changed = False

                key = key_poller.poll(timeout=0.1)
                if key is not None:
                    if key == 'q':
                        os.system('clear')
                        loop.quit()
                        event.clear()
                        break
                    elif key == 'j' or ord(key) == 5:
                        self.current_line += 1
                    elif key == 'k' or ord(key) == 25:
                        self.current_line += -1
                    elif key == 'e':
                        try:
                            EDITOR = os.environ.get('EDITOR')
                            album_cover.visibility = ueberzug.Visibility.INVISIBLE
                            call([EDITOR, self.lyrics_file])
                            self.update_lyrics()
                            self.print_metadata()
                            utils.hide_cursor()
                            if self.album_hidden:
                                album_cover.visibility = ueberzug.Visibility.INVISIBLE
                            else:
                                album_cover.visibility = ueberzug.Visibility.VISIBLE
                        except TypeError:
                            os.system('clear')
                            print('$EDITOR is not set')
                            time.sleep(1)
                    elif key == 'r':
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
                    elif key == 'i':
                        self.album_hidden = not self.album_hidden
                        self.changed = True
                        if self.album_hidden:
                            album_cover.visibility = ueberzug.Visibility.INVISIBLE
                        else:
                            album_cover.visibility = ueberzug.Visibility.VISIBLE
                    elif key == 'h':
                        os.system('clear')
                        album_cover.visibility = ueberzug.Visibility.INVISIBLE
                        utils.move_cursor(0, 0)
                        utils.print_help()
                        time.sleep(5)
                        self.print_metadata()
                        if self.album_hidden:
                            album_cover.visibility = ueberzug.Visibility.INVISIBLE
                        else:
                            album_cover.visibility = ueberzug.Visibility.VISIBLE
                        key_poller.flush()
                    elif key == 'g':
                        modified_key = key_poller.poll(timeout=1.0)
                        if modified_key == 'g':
                            self.current_line = 0
                    elif key == 'G':
                        self.current_line = self.total_lines-self.n_entries


def main():
    run_event = threading.Event()
    run_event.set()
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()

    try:
        lyrics_thread = threading.Thread(target=Lyrics().main, args=(loop, run_event))
        lyrics_thread.start()
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
    finally:
        run_event.clear()
        lyrics_thread.join()

if __name__ == '__main__':
    main()
