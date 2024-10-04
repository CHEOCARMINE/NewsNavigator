import time
from telemar_seguridad import main as telemar_main
from tribuna_seguridad import main as tribuna_main

def run_scrapers():
    while True:
        telemar_main()
        tribuna_main()
        time.sleep(600)

if __name__ == "__main__":
    run_scrapers()