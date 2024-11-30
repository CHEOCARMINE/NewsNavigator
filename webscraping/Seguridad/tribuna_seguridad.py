import requests
from bs4 import BeautifulSoup
import nltk
import spacy
from transformers import pipeline
import time
import locale
from datetime import datetime
import sys
import os
import io
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_db_connection, exists_in_db_seguridad, insert_into_db_seguridad

# Configuración básica del logging
logging.basicConfig(level=logging.INFO)

# Forzar la salida UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Ruta local para cargar datos de nltk
nltk_data_path = os.path.join(os.path.dirname(__file__), '../../nltk_data')
nltk.data.path.append(nltk_data_path)

# Inicialización de las herramientas de NLP
nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Configuración de Localización
locale.setlocale(locale.LC_TIME, 'C.UTF-8')

# Fecha Objetivo
date = datetime.now().strftime("%d %B %Y")
target_date = datetime.strptime(date, "%d %B %Y")

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
    
    sql = """INSERT INTO seguridad (titulo, resumen, fecha, link, relevancia, fuente) 
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
        "https://tribunacampeche.com/category/local/",
        "https://tribunacampeche.com/category/local/page/2/",
        "https://tribunacampeche.com/category/local/page/3/",
        "https://tribunacampeche.com/category/municipios/",
        "https://tribunacampeche.com/category/municipios/page/2/",
        "https://tribunacampeche.com/category/municipios/page/3/",
        "https://tribunacampeche.com/category/carmen/",
        "https://tribunacampeche.com/category/carmen/page/2/",
        "https://tribunacampeche.com/category/expediente/",
        "https://tribunacampeche.com/category/expediente/page/2/",
        "https://tribunacampeche.com/category/policia/",
        "https://tribunacampeche.com/category/policia/page/2/",
        "https://tribunacampeche.com/date/2024/",
        "https://tribunacampeche.com/date/2024/page/2/",
        "https://tribunacampeche.com/date/2024/page/3/"
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
            container = soup.find('div', class_='af-container-row aft-archive-wrapper clearfix archive-layout-list')
            if not container:
                logging.info(f"No se encontró el contenedor principal en {url}")
                continue

            # Buscar las noticias
            articles = container.find_all('div', class_='read-details')

            for article in articles:
                title_div = article.find('div', class_='read-title')
                title = title_div.find('h4').text.strip() if title_div else "No title found"
                
                # Filtrar el titulo duplicados
                if title in existing_titles:
                    logging.info(f"Noticia duplicada encontrada: {title}")
                    continue

                existing_titles.add(title)

                meses_espanol_a_ingles = {
                'enero': 'January', 
                'febrero': 'February', 
                'marzo': 'March', 
                'abril': 'April', 
                'mayo': 'May', 
                'junio': 'June', 
                'julio': 'July', 
                'agosto': 'August', 
                'septiembre': 'September',
                'octubre': 'October', 
                'noviembre': 'November', 
                'diciembre': 'December'
                    }

                # Extraer la fecha de la noticia
                date_span = article.find('span', class_='item-metadata posts-date')
                date = date_span.text.strip() if date_span else "No date found"

                # Eliminar "de" y convertir el mes a inglés
                date = date.replace(" de ", " ")
                for mes_espanol, mes_ingles in meses_espanol_a_ingles.items():
                    if mes_espanol in date.lower():
                        date = date.replace(mes_espanol, mes_ingles)

                # Convertir la fecha a un objeto datetime
                try:
                    article_date = datetime.strptime(date, "%d %B %Y")
                except ValueError:
                    logging.info(f"Formato de fecha no reconocido: {date}")
                    continue

                formatted_date = article_date.strftime("%Y-%m-%d")

                # Filtrar noticias según la fecha objetivo
                if article_date != target_date:
                    logging.info(f"Noticia fuera de la fecha objetivo: {title} - {date}")
                    continue

                # Extraer el enlace de la noticia
                link_div = article.find('div', class_='read-title')
                link = link_div.find('a').get('href') if link_div else "No link found"

                # Extraer la descripción completa
                try:
                    link_response = requests.get(link, headers=headers)
                    link_response.raise_for_status()
                    link_soup = BeautifulSoup(link_response.text, 'html.parser')
                    description_div = link_soup.find('div', class_='entry-content')
                    description = " ".join([p.text.strip() for p in description_div.find_all('p')]) if description_div else "No description found"

                except requests.exceptions.RequestException as e:
                    description = "No description found"

                # Imprimir detalles de la noticia
                logging.info(f"Title: {title}")
                logging.info(f"Description: {description}")
                logging.info(f"Date: {formatted_date}")
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
        item['title'] = item['title'].capitalize()
        item['description'] = '. '.join(sentence.capitalize() for sentence in item['description'].split('. '))
        item['date'] = item['date'].capitalize()
        item['link'] = item['link'].lower()
        item['source'] = "static/images/logos/TribunaLogo.png"
        processed_data.append(item)

    return processed_data

# Detectar Palabras Clave
def detect_keywords(description, keywords):
    return any(keyword in description.lower() for keyword in keywords)

# Clasificar Datos
def classify_data(data):
    logging.info("Clasificando la relevancia de las noticias...")
    keywords = ['delito federal', 'narcotráfico', 'tráfico de drogas', 'crimen organizado', 'lavado de dinero', 'corrupción', 'delitos fiscales', 'contrabando', 'fraude fiscal', 'evasión fiscal', 'delitos electorales', 'delincuencia organizada', 'tráfico de armas', 'secuestro', 'trata de personas', 'terrorismo', 'delitos contra la salud', 'falsificación de documentos', 'fraude', 'delitos financieros', 'delitos ambientales', 'crimen transnacional', 'extorsión', 'homicidio', 'robo de combustible', 'huachicol', 'delitos informáticos', 'hackeo', 'piratería','ejecución', 'homicidio sicarial', 'disparos', 'grupo delictivo', 'usura', 'amenaza de deudores', 'desapariciones', 'menores desaparecidos', 'localización de desaparecidos', 'búsqueda de desaparecidos', 'movilización policial', 'detención', 'orden de aprehensión', 'operativo policial', 'sustancias ilegales', 'armas de fuego', 'detenido', 'investigación de delitos', 'alto impacto', 'cártel de drogas', 'venta de estupefacientes', 'narcomenudeo', 'laboratorio clandestino', 'cultivo de drogas', 'arsenal incautado', 'porte ilegal de armas', 'fabricación de armas', 'armamento pesado', 'municiones ilegales', 'balacera', 'enfrentamiento armado', 'ajuste de cuentas', 'célula criminal', 'banda delictiva', 'violencia organizada', 'conflicto armado', 'violencia en aumento', 'cateo policial', 'redada', 'incautación', 'persecución', 'detención en flagrancia', 'detenido por tráfico', 'allanamiento', 'intervención policial', 'comando armado', 'cibercrimen', 'fraude electrónico', 'lavado de activos', 'soborno', 'malversación de fondos', 'fraude financiero', 'crimen de cuello blanco', 'colombiano', 'colombianos']# Palabras clave
    
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
            if not exists_in_db_seguridad(item['title']):
                insert_into_db_seguridad(item)
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