import json
import sys

from src.main import PyTunesC

try:
    with open('config.json', 'r') as f:
        try:
            config = json.load(f)
        except json.decoder.JSONDecodeError:
            config = {}
except FileNotFoundError:
    config = {}

P = PyTunesC(config, sys.argv)

with open('config.json', 'w') as f:
    json.dump(P.config, f, indent = 4)

