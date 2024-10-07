from celery import Celery, group
import importlib

# Configuración de Celery
app = Celery('news_scraper', broker='redis://localhost:6379/0')

# Configuración para ejecutar los scrapers 
app.conf.beat_schedule = {
    'scrape-all-every-10-minutes': {
        'task': 'manage.run_all_scrapers_in_parallel',
        'schedule': 600.0,  # 10 minutos
        'options': {'expires': 600},  # La tarea debe completarse dentro de 10 minutos
    },
}

app.conf.timezone = 'UTC'


# Tarea principal que ejecuta todos los scrapers en paralelo
@app.task
def run_all_scrapers_in_parallel():
    task_group = group([
        run_scraper_seguridad.s(),
        run_scraper_relevante.s(),
        run_scraper_gobierno.s(),
        #run_scraper_opinion.s()
    ])
    task_group.apply_async()


# Tareas individuales para cada conjunto de scrapers
@app.task
def run_scraper_relevante():
    # Scrapers de información relevante
    telemar_main_relevante = importlib.import_module('webscraping.InformacionRelevante.telemar_relevante').main
    tribuna_main_relevante = importlib.import_module('webscraping.InformacionRelevante.tribuna_relevante').main
    telemar_main_relevante()
    tribuna_main_relevante()
@app.task
def run_scraper_seguridad():
    # Scrapers de seguridad
    telemar_main_seguridad = importlib.import_module('webscraping.seguridad.telemar_seguridad').main
    tribuna_main_seguridad = importlib.import_module('webscraping.seguridad.tribuna_seguridad').main
    telemar_main_seguridad()
    tribuna_main_seguridad()

@app.task
def run_scraper_gobierno():
    # Scrapers de gobierno mexicano
    telemar_main_gobierno = importlib.import_module('webscraping.GobiernoMexicano.telemar_gobierno').main
    tribuna_main_gobierno = importlib.import_module('webscraping.GobiernoMexicano.tribuna_gobierno').main
    telemar_main_gobierno()
    tribuna_main_gobierno()

#@app.task
#def run_scraper_opinion():
    # Scraper de géneros de opinión
#    genero_opinion_main = importlib.import_module('webscraping.GenerosOpinion.nombre_del_archivo_de_scraping_opinion').main
#   genero_opinion_main()
