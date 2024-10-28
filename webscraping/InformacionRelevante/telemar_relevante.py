import requests
from bs4 import BeautifulSoup
import nltk
import spacy
from transformers import pipeline
import time
import locale
from datetime import datetime
import sys
import io
import logging
sys.path.append('C:/Users/cheo_/LABS/NewsNav')
from database import get_db_connection, exists_in_db_informacion_relevante, insert_into_db_informacion_relevante

# Configuración básica del logging
logging.basicConfig(level=logging.INFO)

#Forzar la salida UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Inicialización de las herramientas de NLP
nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Configuración de Localización
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Fecha Objetivo
#date = datetime.now().strftime("%d %B, %Y")
date= "25 octubre, 2024"
target_date = datetime.strptime(date, "%d %B, %Y")

# Truncar Descripciones
def truncate_description(description):
    tokenizer = sentiment_analyzer.tokenizer
    tokens = tokenizer(description, truncation=True, max_length=512, return_tensors="pt")
    truncated_description = tokenizer.decode(tokens['input_ids'][0], skip_special_tokens=True)
    return truncated_description

# Resumir Texto
def summarize_text(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    summary = " ".join([sent.text for sent in sentences[:2]])
    return summary

# Insertar los datos
def insert_into_db(item):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql = """INSERT INTO informacion_relevante (titulo, resumen, fecha, link, relevancia, fuente) 
             VALUES (%s, %s, %s, %s, %s, %s)"""
    values = (item['title'], item['summary'], item['date'], item['link'], item['relevance'], item['source'])
    
    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Datos insertados: {item['title']}")
    except Exception as e:
        logging.info(f"Error al insertar datos: {e}")
    finally:
        cursor.close()
        connection.close()

# Extraer Datos
def extract_data(existing_titles):
    logging.info("Extrayendo datos de las fuentes...")

    all_data = []
    urls = [
        "https://telemarcampeche.com/category/locales/",
        "https://telemarcampeche.com/category/locales/page/2/"
        "https://telemarcampeche.com/category/locales/page/3/",
        "https://telemarcampeche.com/category/municipales/",
        "https://telemarcampeche.com/category/municipales/page/2/",
        "https://telemarcampeche.com/category/municipales/page/3/",
        "https://telemarcampeche.com/category/expediente/",
        "https://telemarcampeche.com/category/expediente/page/2/"	
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.google.com/',
        'Origin': 'https://www.google.com',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    for url in urls:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el contenedor de las noticias
            container = soup.find('div', class_="cm-posts cm-layout-2 cm-layout-2-style-1 col-2")
            if not container:
                logging.info(f"No se encontró el contenedor principal en {url}")
                continue

            # Buscar las noticias
            articles = container.find_all('article')

            for article in articles:
                title_div = article.find('h2', class_='cm-entry-title')
                title = title_div.find('a').text.strip() if title_div else "No title found"
                
                # Filtrar el titulo duplicados
                if title in existing_titles:
                    logging.info(f"Noticia duplicada encontrada: {title}")
                    continue

                existing_titles.add(title)

                # Extraer la fecha de la noticia
                date_span = article.find('time', class_='entry-date')
                date = date_span.text.strip() if date_span else "No date found" 

                # Convertir la fecha a un objeto datetime
                try:
                    article_date = datetime.strptime(date, "%d %B, %Y")
                except ValueError:
                    logging.info(f"Formato de fecha no reconocido: {date}")
                    continue

                formatted_date = article_date.strftime("%Y-%m-%d")

                # Filtrar noticias según la fecha objetivo
                if article_date != target_date:
                    logging.info(f"Noticia fuera de la fecha objetivo: {title} - {date}")
                    continue

                # Extraer el enlace de la noticia
                link_div = article.find('h2', class_='cm-entry-title')
                link = link_div.find('a').get('href') if link_div else "No link found"

                # Extraer la descripción completa
                try:
                    link_response = requests.get(link, headers=headers)
                    link_response.raise_for_status()
                    link_soup = BeautifulSoup(link_response.text, 'html.parser')
                    description_div = link_soup.find('div', class_='cm-entry-summary')
                    description = " ".join([p.text.strip() for p in description_div.find_all('p')]) if description_div else "No description found"

                except requests.exceptions.RequestException as e:
                    description = "No description found"

                # Imprimir detalles de la noticia
                logging.info(f"Title: {title}")
                logging.info(f"Description: {description}")
                logging.info(f"Date: {date}")
                logging.info(f"Link: {link}")

                # Lista de datos recopilados
                news_item = {
                    'title': title,
                    'description': description,
                    'date': formatted_date,
                    'link': link
                }
                all_data.append(news_item)
            
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            logging.info(f"Error al extraer datos de la página de noticias {url}: {e}")

    return all_data

# Preprocesar Datos
def preprocess_data(data):
    logging.info("Preprocesando los datos...")
    processed_data = []

    for item in data:
        item['title'] = item['title'].upper()
        item['description'] = item['description'].upper()
        item['date'] = item['date'].upper()
        item['link'] = item['link'].lower()
        item['source'] = "static/images/logos/TelemarLogo.png"
        processed_data.append(item)

    return processed_data

# Detectar Palabras Clave
def detect_keywords(description, keywords):
    return any(keyword in description.lower() for keyword in keywords)

# Clasificar Datos
def classify_data(data):
    logging.info("Clasificando la relevancia de las noticias...")
    keywords = ['marcha', 'protesta', 'bloqueo', 'huelga', 'paro', 'manifestación', 'movilización', 'resistencia', 'denuncia', 'inconformidad', 'queja', 'asamblea', 'sindicato', 'desastre', 'inundación', 'deslave', 'huracán', 'terremoto', 'evacuación', 'emergencia', 'corrupción', 'fraude', 'detención', 'conflicto', 'violencia', 'ataque', 'secuestro', 'extorsión', 'levantamiento', 'ocupación', 'bloqueo carretero', 'cierre de vialidad', 'aeropuerto bloqueado', 'caseta de peaje bloqueada', 'vía férrea bloqueada', 'proceso electoral interrumpido', 'demanda de apoyo', 'afectación gubernamental', 'protesta social', 'huelga del magisterio', 'universidad en paro', 'manifestación masiva', 'interrupción de servicio público', 'paralización de actividades', 'contingencia gubernamental', 'resistencia civil', 'atención a afectados', 'brigadas de ayuda', 'pescadores', 'campesinos', 'trabajadores','salud', 'estudiantes', 'comunidad indígena', 'defensa de tierras', 'protestas laborales', 'movimientos campesinos', 'comunidades afectadas', 'exigencia de derechos', 'lucha sindical', 'conflictos comunitarios', 'protesta por servicios públicos', 'economía local', 'grupo parlamentario', 'congreso del estado', 'censo de afectados', 'bienestar social', 'condiciones de vida', 'problemas de infraestructura', 'colapsos viales', 'comunicaciones interrumpidas', 'acciones preventivas', 'sindicato', 'maestros', 'estudiantes', 'pescadores', 'pensionados'] # Palabras clave
    
    classified_data = []
    for item in data:
        truncated_description = truncate_description(item['description'])
        sentiment = sentiment_analyzer(truncated_description)[0]['label']
        contains_keyword = detect_keywords(item['description'], keywords)
        
        # Asignar relevancia
        if contains_keyword:
            item['relevance'] = 'alta' if sentiment == 'NEGATIVE' else 'media'
        else:
            item['relevance'] = 'baja'
        
        classified_data.append(item)

    return classified_data

# Resumir Datos
def summarize_data(data):
    logging.info("Resumiendo las descripciones de las noticias...")
    for item in data:
        item['summary'] = summarize_text(item['description'])
    return data

# Presentar Resultados
def present_results(data):
    logging.info("Presentando los resultados...")
    for item in data:
        if item['relevance'] == 'alta':
            logging.info("\n")
            logging.info(f"Titulo: {item['title']}")
            logging.info(f"Resumen: {item['summary']}")
            logging.info(f"Fecha: {item['date']}")
            logging.info(f"Link: {item['link']}")
            logging.info(f"Importancia: {item['relevance']}")
            logging.info(f"Fuente: {item['source']}")

            # Verificar si el título ya existe antes de insertar
            if not exists_in_db_informacion_relevante(item['title']):
                insert_into_db_informacion_relevante(item)
            else:
                logging.info(f"El título ya existe en la base de datos: {item['title']}")

# Función Principal
def scrape_data():
    existing_titles = set()  # Evitar duplicados

    raw_data = extract_data(existing_titles)  # Paso 1: Extraer datos
    processed_data = preprocess_data(raw_data)  # Paso 2: Preprocesar datos
    classified_data = classify_data(processed_data)  # Paso 3: Clasificar relevancia
    summarized_data = summarize_data(classified_data)  # Paso 4: Resumir descripciones
    present_results(summarized_data)  # Paso 5: Presentar resultados

if __name__ == "__main__":
    scrape_data()
