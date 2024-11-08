import logging

def run_scraping(category):
    
    if category == 'informacion_relevante':
        from .InformacionRelevante import telemar_relevante, tribuna_relevante,ncs_relevante
        telemar_relevante.scrape_data()
        tribuna_relevante.scrape_data()
        ncs_relevante.scrape_data()
    elif category == 'seguridad':
        from .Seguridad import telemar_seguridad, tribuna_seguridad, ncs_seguridad
        telemar_seguridad.scrape_data()
        tribuna_seguridad.scrape_data()
        ncs_seguridad.scrape_data()
    elif category == 'gobierno_mexico':
        from .GobiernoMexico import telemar_gobierno, tribuna_gobierno, ncs_gobierno
        telemar_gobierno.scrape_data()
        tribuna_gobierno.scrape_data()
        ncs_gobierno.scrape_data()
    elif category == 'genero_opinion':
        from .GenerosOpinion import ncs_opinion, financiero_opinion
        ncs_opinion.scrape_data()
        financiero_opinion.scrape_data()
    else:
        raise ValueError(f'Categoría {category} no reconocida.')

    logging.info(f"Scraping para la categoría {category} completado.")
