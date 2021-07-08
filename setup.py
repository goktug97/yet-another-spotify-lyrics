#!/usr/bin/env python

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='yet-another-spotify-lyrics',
      version='2.4.5',
      description='Command Line Spotify Lyrics with Album Cover',
      author='Göktuğ Karakaşlı',
      author_email='karakasligk@gmail.com',
      license='MIT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/goktug97/yet-another-spotify-lyrics',
      packages = ['spotify_lyrics'],
      entry_points={
          'console_scripts': [
              'spotify-lyrics = spotify_lyrics:main',
              'spotify-lyrics-once = spotify_lyrics_once:main'
          ]
      },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
      ],
      install_requires=[
          'ueberzug',
          'lxml',
          'requests',
          'dbus-python',
          'beautifulsoup4'
      ],
      python_requires='>=3.6',
      include_package_data=True)
