import queue
from pathlib import Path
from .helpers.lunahost import LunaHost

BIN_DIR = Path(__file__).parent / "bin"

class LunaHook:
    def __init__(self):
        self._queue = queue.Queue()
        self.host = LunaHost(BIN_DIR, on_output=self.on_output)

    def attach(self, pid:int):
        err = self.host.attach(pid)
        if self.host.injection_needed(pid):
            self.host.inject(pid)
    
    def detach(self, pid:int):
        self.host.detach(pid=pid)
    

    def on_output(self, hookcode, hookname, threadparam, text):
        self._queue.put((threadparam.processId, hookcode, text))

    def listen(self, pid: int = 0, hook: str = None):
        while True:
            out_pid, out_hook, text = self._queue.get()
            if pid != 0 and out_pid != pid:
                continue
            if hook is not None and out_hook != hook:
                continue
            yield (out_pid, out_hook, text)