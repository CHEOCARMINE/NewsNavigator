import requests
from bs4 import BeautifulSoup
import nltk
import spacy
from transformers import pipeline
import time
import locale
from datetime import datetime, timedelta
import sys
import io
import logging
sys.path.append('C:/Users/cheo_/LABS/NewsNav')
from database import get_db_connection, exists_in_db_gobierno_mexico, insert_into_db_gobierno_mexico

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
date = datetime.now() - timedelta(days=1)
target_date = date.strftime("%B %d, %Y")
formatted_target_date = datetime.strptime(target_date, "%B %d, %Y")

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
    
    sql = """INSERT INTO gobierno_mexico (titulo, resumen, fecha, link, relevancia, fuente) 
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
        'https://ncscampeche.com/nacional/?qtajax=true'
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
            container = soup.find('div', class_='elementor-posts-container')
            if not container:
                logging.info(f"No se encontró el contenedor principal en {url}")
                continue

            # Buscar las noticias
            articles = container.find_all('article', class_='elementor-post')

            for article in articles:
                # Extraer el enlace de la noticia
                title_tag = article.find('a', class_='elementor-post__thumbnail__link')
                link = title_tag.get('href') if title_tag else "No link found"

                # Evitar duplicados
                if link in existing_titles:
                    logging.info(f"Noticia duplicada encontrada: {link}")
                    continue

                existing_titles.add(link)

                # Extraer detalles de la noticia desde el enlace
                try:
                    link_response = requests.get(link, headers=headers)
                    link_response.raise_for_status()
                    link_soup = BeautifulSoup(link_response.text, 'html.parser')

                    # Extraer fecha de la noticia
                    date_tag = link_soup.find('h4', class_='qt-subtitle')
                    date_text = date_tag.text.strip() if date_tag else "No date found"

                    # Convertir fecha al formato necesario
                    date_text = date_text.split(" el ")[-1].strip()
                    try:
                        article_date = datetime.strptime(date_text, "%B %d, %Y")
                        formatted_date = article_date.strftime("%Y-%m-%d")
                    except ValueError:
                        logging.info(f"Formato de fecha no reconocido: {date_text}")
                        continue

                    # Título
                    title = link_soup.find('h1').text.strip() if link_soup.find('h1') else "No title found"

                    # Descripción
                    description_div = link_soup.find('div', class_='qt-the-content')
                    description = " ".join([p.text.strip() for p in description_div.find_all('p')]) if description_div else "No description found"

                    # Imprimir detalles de la noticia
                    logging.info(f"Title: {title}")
                    logging.info(f"Description: {description}")
                    logging.info(f"Date: {formatted_date}")
                    logging.info(f"Link: {link}")

                    # Agregar noticia a los datos recopilados
                    news_item = {
                        'title': title,
                        'description': description,
                        'date': formatted_date,
                        'link': link
                    }
                    all_data.append(news_item)

                except requests.exceptions.RequestException as e:
                    logging.info(f"No se pudo acceder al enlace: {link} - {e}")
                    continue
            
            # Esperar para evitar sobrecargar el servidor
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
        item['source'] = "static/images/logos/NCSLogo.png"
        processed_data.append(item)

    return processed_data

# Detectar Palabras Clave
def detect_keywords(description, keywords):
    return any(keyword in description.lower() for keyword in keywords)

# Clasificar Datos
def classify_data(data):
    logging.info("Clasificando la relevancia de las noticias...")
    keywords = ['Claudia Sheinbaum', 'presidenta', 'gobierno', 'acciones', 'declaraciones', 'políticas públicas', 'proyectos', 'iniciativas', 'reformas', 'inversiones', 'reuniones', 'colaboraciones', 'programas sociales', 'anuncios', 'investigaciones', 'estrategias', 'desarrollo', 'mejoras', 'seguridad', 'infraestructura', 'promesas', 'resultados', 'evaluaciones', 'sesiones', 'reuniones de trabajo', 'discursos', 'convocatorias', 'rescate', 'ferrocarriles', 'sexenio', 'construcción', 'Tren México-Pachuca', 'circulación', 'huracán', 'categoría 4', 'lluvias', 'inseguridad', 'asesinato', 'alcalde', 'Chilpancingo', 'detenciones', 'selección de candidatos', 'campañas', 'votación', 'elección popular', 'Poder Judicial', 'líder empresarial', 'Consejo Coordinador Empresarial', 'propuestas', 'relaciones internacionales', 'gira presidencial', 'anuncio de políticas', 'informe de gobierno', 'rendición de cuentas', 'discurso oficial', 'plan nacional', 'decreto presidencial', 'ley aprobada', 'sesión extraordinaria', 'prioridades de gobierno', 'objetivos de desarrollo', 'agenda nacional', 'proyectos estratégicos', 'transformación nacional', 'modernización', 'corredor transístmico', 'obras prioritarias', 'programa de construcción', 'infraestructura ferroviaria', 'conectividad nacional', 'desarrollo urbano', 'mejoras viales', 'progreso rural', 'fomento al turismo', 'impulso industrial', 'desarrollo sustentable', 'proyectos ecológicos', 'energía renovable', 'programa de seguridad', 'plan de paz', 'política de justicia', 'combate al crimen', 'seguridad fronteriza', 'cambio en procuraduría', 'policía federal', 'reforma judicial', 'transparencia', 'operativos nacionales', 'investigación federal', 'acciones de combate al narcotráfico', 'reforma de seguridad', 'protección civil', 'acuerdo bilateral', 'relación diplomática', 'cooperación internacional', 'visita de estado', 'tratado de libre comercio', 'relaciones exteriores', 'alianza económica', 'inversión extranjera', 'política exterior', 'frontera sur', 'integración económica', 'foros internacionales', 'representación mexicana', 'embajador', 'agenda pública', 'programas federales', 'encuentro gubernamental', 'proyecto de ley', 'prioridades de gobierno', 'partido en el poder', 'gestión pública', 'reformas administrativas', 'presupuesto de egresos', 'plan de austeridad', 'programa de bienestar', 'ministerio de finanzas', 'poder ejecutivo'] # Palabras clave
    
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
            if not exists_in_db_gobierno_mexico(item['title']):
                insert_into_db_gobierno_mexico(item)
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
