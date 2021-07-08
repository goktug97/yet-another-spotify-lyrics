import os
import re
import select
import sys
import termios
import urllib.parse

import dbus
import requests
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

def fetch_lyrics(artist, title):
    title = re.sub(r'[-\*"]', ' ', title)
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

    def poll(self, timeout=0.0):
        dr,dw,de = select.select([sys.stdin], [], [], timeout)
        return sys.stdin.read(1) if not dr == [] else None

    def flush(self):
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

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
        art_url = f"https://i.scdn.co/image/{metadata['mpris:artUrl'].replace('&', '&amp;').split('/')[-1]}"
        return title, artist, album, art_url

    def next(self):
        self.player_interface.Next()

    def prev(self):
        self.player_interface.Previous()

    def toggle(self):
        self.player_interface.PlayPause()

def print_help():
    print(boldify('''
| Action              | Keybinding    |
|:-------------------:|:-------------:|
| Scroll Up           |      k        |
| Scroll Down         |      j        |
| Beginning of Lyrics |      gg       |
| End of Lyrics       |      G        |
| Edit Lyrics         |      e        |
| Refresh             |      r        |
| Toggle              |      t        |
| Next                |      n        |
| Prev                |      p        |
| Update Lyrics       |      d        |
| Toggle Album Cover  |      i        |
| Help                |      h        |
| Quit Program        |      q        |

- Edit Lyrics: Open lyrics in `$EDITOR`.
- Refresh: Refresh lyrics and song metadata.
- Toggle: Play or Pause currently playing song.
- Next: Play next song.
- Prev: Play previous song.
- Update Lyrics: Deletes cached lyrics and fetches lyrics from the internet.
- Help: Show keybindings 5 seconds.'''))
