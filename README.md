# Yet Another Spotify Command Line Lyrics

## Requirements
* ueberzug
* python-dbus
* request
* beautifulsoup4
* lxml

## Screenshot

![Lyrics-Screenshot](https://github.com/goktug97/yet-another-spotify-lyrics/blob/master/lyrics-screenshot.jpg)

## Install

```bash
git clone https://github.com/goktug97/yet-another-spotify-lyrics
cd yet-another-spotify-lyrics
python setup.py install
```

## Usage

``` bash
spotify-lyrics
```

## example i3 settings for the script
```i3
bindsym $mod+Shift+Home exec st -n Lyrics -e lyrics
for_window [instance="Lyrics"] floating enable; [instance="Lyrics"] move position center
for_window [instance="Lyrics"] resize set 644 388
```

