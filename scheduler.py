from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

# Importa tus scrapers
import webscraping.InformacionRelevante.telemar_relevante as telemar_relevante
import webscraping.InformacionRelevante.tribuna_relevante as tribuna_relevante

import webscraping.Seguridad.telemar_seguridad as telemar_seguridad
import webscraping.Seguridad.tribuna_seguridad as tribuna_seguridad

import webscraping.GobiernoMexico.telemar_gobierno as telemar_gobierno
import webscraping.GobiernoMexico.tribuna_gobierno as tribuna_gobierno

# Aún no tienes los scrapers de GenerosOpinion, pero los dejo preparados para cuando los agregues
# import webscraping.GenerosOpinion.telemar_opinion as telemar_opinion
# import webscraping.GenerosOpinion.tribuna_opinion as tribuna_opinion

# Función que ejecuta los scrapers
def ejecutar_scrapers():
    print(f"Ejecutando scrapers a las {datetime.now()}")

    # Scrapers de Información Relevante
    print("Ejecutando scrapers de Información Relevante")
    telemar_relevante.scrape()
    tribuna_relevante.scrape()

    # Scrapers de Seguridad
    print("Ejecutando scrapers de Seguridad")
    telemar_seguridad.scrape()
    tribuna_seguridad.scrape()

    # Scrapers de Gobierno Mexicano
    print("Ejecutando scrapers de Gobierno Mexicano")
    telemar_gobierno.scrape()
    tribuna_gobierno.scrape()

    # Scrapers de Generos de Opinión (comentados por ahora)
    # print("Ejecutando scrapers de Generos de Opinión")
    # telemar_opinion.scrape()
    # tribuna_opinion.scrape()

if __name__ == "__main__":
    # Crear un programador en segundo plano
    scheduler = BackgroundScheduler()

    # Configura la tarea para que se ejecute cada 2 horas
    scheduler.add_job(
        ejecutar_scrapers, 
        IntervalTrigger(hours=2), 
        start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
        end_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    )

    try:
        # Iniciar el programador
        scheduler.start()
        print("El programador ha iniciado.")
        
        # Mantener el proceso vivo para que el scheduler siga corriendo
        while True:
            pass
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("El programador ha sido detenido.")
