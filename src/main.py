from threading import Thread
from gi.repository import Notify, Gtk

from .selector import SelectorC
from .client import DjangoClientC
from .tools import AutoConfig

class PyTunesC:
    def __init__(self, config, argv):
        self.config = config
        
        self.Selector = SelectorC(self.config, self.OnSelection)
        self.Client = DjangoClientC(self.config)
        self.Command = CommandC(self.config, self.OnDownload, self.OnIgnore)

        argv.pop(0)
        if argv:
            key, value = argv[0].split('=')
            command_data = {key:value for key, value in [arg.split('=') for arg in argv]}
            self.TestCommand(command_data)
            return
        
        Thread(target=self.Selector.Run).start()
        try:
            Gtk.main()
        except KeyboardInterrupt:
            self.Selector.Running = False

    def TestCommand(self, data):
        test_type = data.get('test')
        yt_id = data.get('yt_id', 'test')
        print("Current YtRefs:")
        print(self.GetRefs(), '\n')
        if test_type == 'download':
            self.Client.delete(f'/data/refs/{yt_id}/')
            self.OnDownload(yt_id)

    def GetRefs(self):
        return self.Client.get('/data/refs/').json()

    def OnDownload(self, yt_id):
        ans = self.Client.post('/data/refs/', payload = self.YtRefPayload(yt_id, downloaded=True)).json()
        print(f"Downloaded {yt_id}")
        print(ans)
    def OnIgnore(self, yt_id):
        self.Client.post('/data/refs/', payload = self.YtRefPayload(yt_id, ignore=True))
        print(f"Ignored {yt_id}")

    def OnSelection(self, yt_id, title = '', downloaded = False):
        ans = self.Client.post('/data/refs/', payload = self.YtRefPayload(yt_id)).json()
        print(f"Sent {title} to the library")
        if not ans.get('downloaded') and not ans.get('ignored'):
            self.Command(yt_id, title, ans.get('remind'))

    @staticmethod
    def YtRefPayload(yt_id, **kwargs):
        payload = {'yt_id':yt_id,
                   'downloaded':False,
                   'ignored':False}
        for key, value in kwargs.items():
            payload[key]=value
        return payload

class CommandC(AutoConfig):
    ConfigKey = 'command'
    Params = [('auto_download_after', 20),
              ('ask_download_every', 4),
              ('ask_at_first_encounter', True),]

    def __init__(self, config, download_callback, ignore_callback):
        self.UpdateParams(config)
        self.DownloadCallback = lambda *args, self=self, **kwargs: download_callback(self.current_id)
        self.IgnoreCallback = lambda *args, self=self, **kwargs: ignore_callback(self.current_id)

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
