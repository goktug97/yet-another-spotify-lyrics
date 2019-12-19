Yet Another Spotify Command Line Lyrics
==========================================

![Lyrics-Screenshot](https://raw.githubusercontent.com/goktug97/yet-another-spotify-lyrics/master/screenshot.jpg)

## Requirements
* ueberzug
* dbus-python
* requests
* beautifulsoup4
* lxml

## Install

### From PyPI
```bash
pip3 install yet-another-spotify-lyrics --user
```

### From Source
```bash
git clone https://github.com/goktug97/yet-another-spotify-lyrics
cd yet-another-spotify-lyrics
python setup.py install --user
```

## Usage

``` bash
spotify-lyrics
```

### Keybindings

| Action        | Keybinding   |
|:-------------:|:------------:|
| Scrool Up     | <kbd>k</kbd> |
| Scrool Down   | <kbd>j</kbd> |
| Edit Lyrics   | <kbd>e</kbd> |
| Refresh       | <kbd>r</kbd> |
| Toggle        | <kbd>t</kbd> |
| Next          | <kbd>n</kbd> |
| Prev          | <kbd>p</kbd> |
| Update Lyrics | <kbd>d</kbd> |
| Quit Program  | <kbd>q</kbd> |

- Edit Lyrics: Open lyrics in `$EDITOR`.
- Refresh: Refresh lyrics and song metadata.
- Toggle: Play or Pause currently playing song.
- Next: Play next song.
- Prev: Play previous song.
- Update Lyrics: Deletes cached lyrics and fetches lyrics from the internet. 

### Example Use Case (i3wm)
```i3
bindsym $mod+Shift+Home exec st -n Lyrics -e spotify-lyrics
for_window [instance="Lyrics"] floating enable; [instance="Lyrics"] move position center
for_window [instance="Lyrics"] resize set 644 388
```

## License
yet-another-spotify-lyrics is licensed under the MIT License.

