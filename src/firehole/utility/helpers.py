from multiprocessing import Process


class ProxyProcess:
    def __init__(self, proxy):
        self.proxy = proxy
        self._process: Process | None = None

    def start(self):
        self._process = Process(target=self.proxy.start)
        self._process.start()

    def stop(self):
        self._process.kill()
