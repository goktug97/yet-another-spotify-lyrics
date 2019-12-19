#!/usr/bin/env python

import os
from setuptools import setup

directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='yet-another-spotify-lyrics',
      version='1.0.3',
      description='Command Line Spotify Lyrics with Album Cover',
      author='Göktuğ Karakaşlı',
      author_email='karakasligk@gmail.com',
      license='MIT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/goktug97/yet-another-spotify-lyrics',
      download_url=(
          'https://github.com/goktug97/yet-another-spotify-lyrics/archive/v1.0.3.tar.gz'),
      py_modules=[os.path.splitext(os.path.basename(path))[0]
                  for path in ['spotify_lyrics']],
      entry_points={
              'console_scripts': [
                  'spotify-lyrics = spotify_lyrics:main',
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
