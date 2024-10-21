import logging
def run_scraping(category):
    
    if category == 'informacion_relevante':
        from .InformacionRelevante import telemar_relevante, tribuna_relevante
        telemar_relevante.scrape_data()
        tribuna_relevante.scrape_data()
    elif category == 'seguridad':
        from .Seguridad import telemar_seguridad, tribuna_seguridad
        telemar_seguridad.scrape_data()
        tribuna_seguridad.scrape_data()
    elif category == 'gobierno_mexicano':
        from .GobiernoMexico import telemar_gobierno, tribuna_gobierno
        telemar_gobierno.scrape_data()
        tribuna_gobierno.scrape_data()
    #elif category == 'genero_opinion':
        #from .GenerosOpinion import opinion_scraper  # Ajusta según tu estructura
        #opinion_scraper.scrape_data()  # Asegúrate de que este módulo tenga la función scrape_data
    else:
        raise ValueError(f'Categoría {category} no reconocida.')

    logging.info(f"Scraping para la categoría {category} completado.")
