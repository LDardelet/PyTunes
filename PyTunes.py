import json
from gi.repository import Notify

from src.selector import SelectorC
from src.client import DjangoClientC
from src.tools import AutoConfig

class PyTunesC:
    def __init__(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {}
        
        self.Selector = SelectorC(self.config, self.OnSelection)
        self.Client = DjangoClientC(self.config)
        self.Command = CommandC(self.config, self.OnDownload, self.OnIgnore)

        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent = 4)

        self.Selector.Run()

    def OnDownload(self, yt_id):
        print(f"Downloaded {yt_id}")
    def OnIgnore(self, yt_id):
        print(f"Ignored {yt_id}")

    def OnSelection(self, yt_id, title = '', downloaded = False):
        ans = self.Client.post('/data/refs/', payload = {'yt_id':yt_id, 
                                                         'downloaded':downloaded}).json()
        print(f"Sent {title} to the library")
        if not ans.get('downloaded'):
            self.Command(yt_id, title, ans.get('remind'))

class CommandC(AutoConfig):
    ConfigKey = 'command'
    Params = [('auto_download_after', 20),
              ('ask_download_every', 4),
              ('ask_at_first_encounter', True),]

    def __init__(self, config, new_download_callback, new_ignore_callback):
        self.UpdateParams(config)
        self.DownloadCallback = new_download_callback
        self.IgnoreCallback = new_ignore_callback

        self.current_id = None

        Notify.init("PyTunes")
        self.notification = Notify.Notification.new("")
        self.notification_template = "Download this song ({0} occurences) ?\n{1}"
        self.notification_template_first = "Download this song ?\n{0}"
        self.notification.add_action("download_click", "Download", self.DownloadCallback)
        self.notification.add_action("ignore_click", "Ignore", self.IgnoreCallback)

    def __call__(self, yt_id, title, remind):
        self.current_id = yt_id
        if (remind == 1 and self.ASK_AT_FIRST_ENCOUNTER):
            self.notification.update("New song", self.notification_template_first.format(title))
            self.notification.show()
            return
        if (remind % self.ASK_DOWNLOAD_EVERY == 0) or (remind >= self.AUTO_DOWNLOAD_AFTER):
            self.notification.update("Recurring song", self.notification_template.format(remind, title))
            self.notification.show()
            return

P = PyTunesC()
