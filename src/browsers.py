#! /usr/bin/env python3

import importlib
import sys
import pathlib
import json

from .tools import AutoConfig

"""
Credits: 
Firefox scrapper: https://gist.github.com/tmonjalo
"""

class BrowserScrapperC(AutoConfig):
    ConfigKey = 'scrapper'
    Params = [('youtube_url', 'youtube.com'),]
    def get_youtube_pages(self):
        return {(url, title) for (url, title) in self.get_pages() if self.YOUTUBE_URL in url}
    def get_videos(self):
        IDs = {}
        pages = self.get_youtube_pages()
        for url, title in pages:
            fields = url.split('?')[-1].split('&')
            for field in fields:
                try:
                    key, value = field.split('=')
                except ValueError:
                    continue
                if key == 'v':
                    IDs[value] = title
        return IDs
    
class FirefoxScrapperC(BrowserScrapperC):
    ConfigKey = 'firefox'
    Params = [('mozilla_path', '.mozilla/firefox'),]
    def __init__(self, config):
        self.UpdateParams(config)
        self.path = pathlib.Path.home().joinpath(self.MOZILLA_PATH)
        self.lz = importlib.import_module('lz4.block')

    def get_pages(self):
        files = self.path.glob('*default*/sessionstore-backups/recovery.js*')
        pages = set()
        for f in files:
            b = f.read_bytes()
            if b[:8] == b'mozLz40\0':
                try:
                    b = self.lz.decompress(b[8:])
                    print("Decompress success")
                except self.lz.LZ4BlockError as e:
                    print("Unable to decompress file")
                    print(e)
                    continue
            try:
                j = json.loads(b)
            except UnicodeDecodeError as e:
                print("Unable to load JSON data")
                print(e)
                continue
            for w in j['windows']:
                for t in w['tabs']:
                    i = t['index'] - 1
                    pages.add((t['entries'][i]['url'], t['entries'][i]['title']))
        return pages

    def get_tabs(self):
        files = self.path.glob('*default*/sessionstore-backups/recovery.js*')
        tabs = {}
        for f in files:
            b = f.read_bytes()
            if b[:8] == b'mozLz40\0':
                b = self.lz.decompress(b[8:])
            j = json.loads(b)
            for w in j['windows']:
                for t in w['tabs']:
                    tabs[t['entries'][t['index'] - 1]['url']] = t
        return tabs
