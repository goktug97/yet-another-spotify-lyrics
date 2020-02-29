Yet Another Spotify Command Line Lyrics
==========================================

![Lyrics-Screenshot](https://raw.githubusercontent.com/goktug97/yet-another-spotify-lyrics/master/screenshot.jpg)

## Requirements
* Linux
* Python >= 3.6
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
![Usage Gif](https://raw.githubusercontent.com/goktug97/yet-another-spotify-lyrics/master/usage.gif)

``` bash
spotify-lyrics
```

### Keybindings

| Action              | Keybinding    |
|:-------------------:|:-------------:|
| Scroll Up           | <kbd>k</kbd>  |
| Scroll Down         | <kbd>j</kbd>  |
| Beginning of Lyrics | <kbd>gg</kbd> |
| End of Lyrics       | <kbd>G</kbd>  |
| Edit Lyrics         | <kbd>e</kbd>  |
| Refresh             | <kbd>r</kbd>  |
| Toggle              | <kbd>t</kbd>  |
| Next                | <kbd>n</kbd>  |
| Prev                | <kbd>p</kbd>  |
| Update Lyrics       | <kbd>d</kbd>  |
| Toggle Album Cover  | <kbd>i</kbd>  |
| Help                | <kbd>h</kbd>  |
| Quit Program        | <kbd>q</kbd>  |

- Edit Lyrics: Open lyrics in `$EDITOR`.
- Refresh: Refresh lyrics and song metadata.
- Toggle: Play or Pause currently playing song.
- Next: Play next song.
- Prev: Play previous song.
- Update Lyrics: Deletes cached lyrics and fetches lyrics from the internet. 
- Help: Show keybindings 5 seconds.

### DBUS
The lyrics can be scrolled via dbus.
Scroll the lyrics without changing the focus.

#### Python Example

``` python
import dbus

bus = dbus.SessionBus()
lyrics = bus.get_object('com.spotify_lyrics.line', '/com/spotify_lyrics')
lyrics.move(1) # Scroll Down
lyrics.move(-1) # Scroll Up
```

#### Bash Example

``` bash
#!/usr/bin/env bash
dbus-send --print-reply --dest="com.spotify_lyrics.line"\
    "/com/spotify_lyrics"\
    "com.spotify_lyrics.line.move"\
    int32:$1 > /dev/null
```

I call this bash script from my i3 config. See below.

### Example Use Case (i3wm)
```i3
bindsym $mod+Shift+Home exec st -n Lyrics -e spotify-lyrics
for_window [instance="Lyrics"] floating enable; [instance="Lyrics"] move position center
for_window [instance="Lyrics"] resize set 644 388
bindsym $mod+Control+k exec lyrics-move -1
bindsym $mod+Control+j exec lyrics-move 1
```

### Example Use Case (Emacs)
Open the lyrics in a buffer.

``` emacs-lisp
(defun spotify-lyrics ()
  (interactive)
  (let ((string (shell-command-to-string "spotify-lyrics-once")))
    (get-buffer-create "lyrics-buffer")
    (switch-to-buffer-other-window "lyrics-buffer")
    (with-current-buffer "lyrics-buffer"
      (goto-char (point-max))
      (erase-buffer)
      (insert string)
      (goto-line 1))))
```

### Example Use Case (Conky)
You can use spotify-lyrics-once to output the lyrics to the stdout and exit.
If you have program that utilizes stdin, you can use this version.
An example for such program is Conky.

``` lua
#!/usr/bin/lua
conky.config = {
	alignment = 'tl',
	background = true,
	color2 = '2ECC71',
	cpu_avg_samples = 2,
	default_color = 'FFFFFF',
	double_buffer = true,
	font = 'Bitstream Vera Sans:size=10',
	gap_x = 30,
	gap_y = 50,
	minimum_width = 200,
	no_buffers = true,
	own_window = true,
	own_window_type = 'override',
	own_window_transparent = true,
	own_window_argb_visual = true,
	-- own_window_type = 'desktop',
	update_interval = 3,
	use_xft = true,
}
conky.text = [[
${voffset 8}$color2${font Bitstream Vera Sans:size=16}${time %A}$font\
${voffset -8}$alignr$color${font Bitstream Vera Sans:size=38}${time %e}$font
$color${voffset -30}$color${font Bitstream Vera Sans:size=18}${time %b}$font\
${voffset -3} $color${font Bitstream Vera Sans:size=20}${time %Y}$font$color2$hr
${execi 5 spotify-lyrics-once}
]]
```

## License
yet-another-spotify-lyrics is licensed under the MIT License.

