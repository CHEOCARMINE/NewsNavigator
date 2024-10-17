import sys
import io
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import time

# Asegúrate de que stdout y stderr estén abiertos
def ensure_open_streams():
    if sys.stdout.closed:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.closed:
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Asegúrate de que los flujos estén abiertos al inicio
ensure_open_streams()

print("El programa ha comenzado.")

def job():
    print(f"Ejecutando tarea a las {datetime.now()}")

if __name__ == "__main__":
    # Crear un programador en segundo plano
    scheduler = BackgroundScheduler()
    scheduler.add_job(job, 'interval', seconds=10)

    try:
        # Iniciar el programador
        scheduler.start()
        print("El programador ha iniciado.")
        
        # Mantener el proceso vivo
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        print("Deteniendo el programador...")
        scheduler.shutdown()
        print("El programador ha sido detenido.")
