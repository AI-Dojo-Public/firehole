import time
from multiprocessing import Process

from firehole.http_s.proxy import run_server, Handler


if __name__ == '__main__':
    processes = []

    p = Process(target=run_server, args=("localhost", 4433, Handler.PROXY))
    processes.append(p)
    p.start()

    p = Process(target=run_server, args=("localhost", 4434, Handler.TEST))
    processes.append(p)
    p.start()

    try:
        while True:
            time.sleep(999)
    except KeyboardInterrupt:
        for p in processes:
            p.kill()
            p.join()
