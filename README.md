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
| scrool-up     | <kbd>k</kbd> |
| scrool-down   | <kbd>j</kbd> |
| edit-lyrics   | <kbd>e</kbd> |
| refresh       | <kbd>r</kbd> |
| delete-cached | <kbd>d</kbd> |
| quit-program  | <kbd>q</kbd> |

- edit-lyrics: Open lyrics in `$EDITOR`
- refresh: Re-prints lyrics and song info.
- delete-cached: Deletes cached lyrics and gets lyrics from the internet. 

### Example Use Case (i3wm)
```i3
bindsym $mod+Shift+Home exec st -n Lyrics -e spotify-lyrics
for_window [instance="Lyrics"] floating enable; [instance="Lyrics"] move position center
for_window [instance="Lyrics"] resize set 644 388
```

## License
yet-another-spotify-lyrics is licensed under the MIT License.

