import sys
import time
import importlib
from pathlib import Path

# Añadir directorios de scraping al sys.path
sys.path.append(str(Path(__file__).resolve().parent / 'webscraping' / 'InformacionRelevante'))
sys.path.append(str(Path(__file__).resolve().parent / 'webscraping' / 'seguridad'))
sys.path.append(str(Path(__file__).resolve().parent / 'webscraping' / 'GobiernoMexicano'))
sys.path.append(str(Path(__file__).resolve().parent / 'webscraping' / 'GenerosOpinion'))

# InformacionRelevante
telemar_main_relevante = importlib.import_module('telemar_relevante').main
tribuna_main_relevante = importlib.import_module('tribuna_relevante').main

# Seguridad
telemar_main_seguridad = importlib.import_module('telemar_seguridad').main
tribuna_main_seguridad = importlib.import_module('tribuna_seguridad').main

# GobiernoMexicano
telemar_main_gobierno = importlib.import_module('telemar_gobierno').main
tribuna_main_gobierno = importlib.import_module('tribuna_gobierno').main

# GeneroOpinion

def run_scrapers():
    while True:
        # Ejecutar scrapers de InformacionRelevante
        telemar_main_relevante()
        tribuna_main_relevante()
        
        # Ejecutar scrapers de Seguridad
        telemar_main_seguridad()
        tribuna_main_seguridad()

        # Ejecutar scrapers de GobiernoMexicano
        telemar_main_gobierno()
        tribuna_main_gobierno()

        # Ejecutar scraper de GenerosOpinion
        
        time.sleep(600) # 10 minutes

if __name__ == "__main__":
    run_scrapers()
