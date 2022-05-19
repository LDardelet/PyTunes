import datetime
import time
from enum import Enum, auto

from . import browsers
from .tools import AutoConfig

class State(Enum):
    RUNNING = auto()
    WAITING = auto()
    SENT = auto()
    IGNORE = auto()

class SelectorC(AutoConfig):
    ConfigKey = 'selector'
    Params = [('minimum_duration_seconds', 7),
              ('scrap_period_seconds', 2),]
    def __init__(self, config, new_selection_callback):
        self.UpdateParams(config)
        self.minimum_duration = datetime.timedelta(seconds=self.MINIMUM_DURATION_SECONDS)

        self.Scrappers = {browsers.FirefoxScrapperC(config)}
        self.Videos = {Scrapper:{} for Scrapper in self.Scrappers}
        self.SelectionCallback = new_selection_callback
        
        self.Running = False

    def Run(self):
        self.Running = True
        while self.Running:
            self.Scrap()
            time.sleep(self.SCRAP_PERIOD_SECONDS)

    def Scrap(self):
        Selection = set()
        now = datetime.datetime.now()
        for Scrapper in self.Scrappers:
            Videos = self.Videos[Scrapper]
            LiveVideos = Scrapper.get_videos()
            for LiveID, title in LiveVideos.items():
                if LiveID in Videos:
                    if Videos[LiveID]['state'] == State.RUNNING and now > Videos[LiveID]['start'] + self.minimum_duration:
                        Videos[LiveID]['state'] = State.SENT
                        Selection.add((LiveID, Videos[LiveID]['title']))
                else:
                    Videos[LiveID] = {'state':State.RUNNING,
                                      'start':now,
                                      'title':title}
            for ID, values in Videos.items():
                if values['state'] != State.RUNNING:
                    continue
                if ID in LiveVideos:
                    continue
                print(f"Ignoring {ID}")
                values['state'] = State.IGNORE
        for yt_id, title in Selection:
            self.SelectionCallback(yt_id, title)
