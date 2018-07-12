import lyrebird
import pip
import threading


if __name__ == '__main__':
    pip.main(['install', '.',  '--upgrade'])
    lyrebird.debug()
    threading.Event().wait()

