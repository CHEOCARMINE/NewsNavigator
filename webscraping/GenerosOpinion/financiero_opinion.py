import requests
from bs4 import BeautifulSoup
import nltk
import spacy
from transformers import pipeline
import time
import locale
from datetime import datetime, timedelta
import sys
import os
import io
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from database import get_db_connection, exists_in_db_genero_opinion, insert_into_db_genero_opinion

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
date = datetime.now().strftime("%B %d, %Y")
target_date = datetime.strptime(date, "%B %d, %Y")

# Función para truncar descripciones
def truncate_description(description):
    tokenizer = sentiment_analyzer.tokenizer
    tokens = tokenizer(description, truncation=True, max_length=512, return_tensors="pt")
    truncated_description = tokenizer.decode(tokens['input_ids'][0], skip_special_tokens=True)
    return truncated_description

# Resumir texto
def summarize_text(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    summary = " ".join([sent.text for sent in sentences[:2]])
    return summary

# Insertar datos en la base de datos
def insert_into_db(item):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    sql = """INSERT INTO genero_opinion (titulo, resumen, fecha, link, relevancia, fuente) 
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
    url = "https://www.elfinanciero.com.mx/opinion/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'https://www.google.com/',
        'Origin': 'https://www.google.com',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar los artículos
        articles = soup.find_all('div', class_='col-sm-12 col-md-undefined col-md-xl-4 margin-sm-bottom')

        for article in articles:
            # Extraer el enlace de la noticia
            link_tag = article.find('a', class_='color_black text_left decoration_none cursor_pointer')
            link = link_tag.get('href') if link_tag else "No link found"
            link = "https://www.elfinanciero.com.mx" + link if link and not link.startswith("http") else link

            # Extraer el título de la noticia
            title = link_tag.get('title', '').strip() if link_tag else "No title found"

            # Filtrar el título duplicados
            if title in existing_titles:
                logging.info(f"Noticia duplicada encontrada: {title}")
                continue

            existing_titles.add(title)

            try:
                link_response = requests.get(link, headers=headers)
                link_response.raise_for_status()
                link_soup = BeautifulSoup(link_response.text, 'html.parser')

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
                date_tag = link_soup.find('time', class_='c-date b-date')
                date_text = date_tag.get('datetime', '') if date_tag else "No date found"
                
                # Si hay una fecha extraída
                if date_text:
                    try:
                        # Convertir la fecha a minúsculas para facilitar la sustitución
                        date_text_lower = date_text.lower()

                        # Traducir el mes en español al mes en inglés
                        for mes_es, mes_en in meses_espanol_a_ingles.items():
                            if mes_es in date_text_lower:
                                date_text = date_text.replace(mes_es, mes_en)

                        date_text = date_text.split("T")[0]

                        # Ahora que tenemos el mes en inglés, convertimos la fecha a un objeto datetime
                        article_date = datetime.strptime(date_text, "%B %d, %Y")
                        formatted_date = article_date.strftime("%Y-%m-%d")

                        # Filtrar noticias según la fecha objetivo
                        if article_date != target_date:
                            logging.info(f"Noticia fuera de la fecha objetivo: {title} - {formatted_date}")
                            continue

                    except ValueError:
                        logging.info(f"Formato de fecha no reconocido: {date_text}")
                        continue
                else:
                    logging.info("Fecha no encontrada.")
                    continue

                # Extraer la descripción completa
                description_div = link_soup.find('div', class_='col-sm-md-12 col-lg-xl-6 main-article-section ie-flex-100-percent-sm layout-section')
                description = " ".join([p.text.strip() for p in description_div.find_all('p', class_='c-paragraph')]) if description_div else "No description found"

            except requests.exceptions.RequestException as e:
                logging.info(f"Error al obtener los detalles de la noticia en {link}: {e}")
                continue

            logging.info(f"Title: {title}")
            logging.info(f"Description: {description}")
            logging.info(f"Date: {formatted_date}")
            logging.info(f"Link: {link}")

            news_item = {
                'title': title,
                'description': description,
                'date': formatted_date,
                'link': link
            }
            all_data.append(news_item)

        time.sleep(2)

    except requests.exceptions.RequestException as e:
        logging.info(f"Error al extraer datos de la página de noticias: {e}")

    return all_data

# Preprocesar datos
def preprocess_data(data):
    logging.info("Preprocesando los datos...")
    processed_data = []

    for item in data:
        item['title'] = item['title'].capitalize()
        item['description'] = '. '.join(sentence.capitalize() for sentence in item['description'].split('. '))
        item['date'] = item['date'].capitalize()
        item['link'] = item['link'].lower()
        item['source'] = "static/images/logos/ElFinancieroLogo.ico"
        processed_data.append(item)

    return processed_data

# Detectar palabras clave
def detect_keywords(description, keywords):
    return any(keyword in description.lower() for keyword in keywords)

# Clasificar relevancia
def classify_data(data):
    logging.info("Clasificando la relevancia de las noticias...")
    keywords = ['Claudia Sheinbaum', 'presidenta', 'gobierno', 'acciones', 'declaraciones', 'políticas públicas', 'proyectos', 'iniciativas', 'reformas', 'inversiones', 'reuniones', 'colaboraciones', 'programas sociales', 'anuncios', 'investigaciones', 'estrategias', 'desarrollo', 'mejoras', 'seguridad', 'infraestructura', 'promesas', 'resultados', 'evaluaciones', 'sesiones', 'reuniones de trabajo', 'discursos', 'convocatorias', 'rescate', 'ferrocarriles', 'sexenio', 'construcción', 'Tren México-Pachuca', 'circulación', 'huracán', 'categoría 4', 'lluvias', 'inseguridad', 'asesinato', 'alcalde', 'Chilpancingo', 'detenciones', 'selección de candidatos', 'campañas', 'votación', 'elección popular', 'Poder Judicial', 'líder empresarial', 'Consejo Coordinador Empresarial', 'propuestas', 'relaciones internacionales', 'Transparencia', 'Eficiencia', 'Responsabilidad', 'Participación', 'Sostenibilidad','Gobierno', 'Políticas', 'Administración', 'Reforma', 'Corrupción', 'Democracia','Legislación', 'Ejecución', 'Servicios públicos', 'Recursos', 'Confianza','Rendición de cuentas', 'Necesidades', 'Desarrollo', 'Estrategias', 'Educación','Salud', 'Seguridad', 'Justicia', 'Bienestar', 'Implementación', 'Estructura','Funcionamiento', 'Optimización', 'Decisiones', 'Acciones', 'Instituciones','Ciudadanía', 'Balance', 'Crecimiento', 'Ambiental', 'Economía', 'Revisión','Rendimiento', 'Calidad', 'Accesibilidad', 'Innovación', 'Eficacia', 'Planificación','Fiscalización', 'Impacto', 'Regulación', 'Evaluación', 'Control', 'Normativa','Legalidad', 'Cooperación', 'Infraestructura', 'Descentralización', 'Equidad','Inclusión', 'Ética', 'Gobernanza', 'Modernización', 'Digitalización', 'Datos abiertos','Auditoría', 'Monitoreo', 'Bienes públicos', 'Servicios esenciales', 'Seguridad social','Provisión', 'Subsidios', 'Asignación', 'Manejo', 'Gestión pública', 'Colaboración','Concertación', 'Estrategias públicas', 'Programas sociales', 'Acción gubernamental','Gobierno abierto', 'Participación ciudadana', 'Política fiscal', 'Presupuesto','Gasto público', 'Inversión pública', 'Desarrollo sostenible', 'Inclusión social','Justicia social', 'Desigualdad', 'Pobreza', 'Innovación tecnológica', 'Política ambiental','Cambio climático', 'Gestión de recursos naturales', 'Biodiversidad', 'Energías renovables','Seguridad energética', 'Movilidad sustentable', 'Urbanismo', 'Vivienda', 'Educación pública', 'Salud pública'] # Palabras clave
    
    classified_data = []
    for item in data:
        truncated_description = truncate_description(item['description'])
        sentiment = sentiment_analyzer(truncated_description)[0]['label']
        contains_keyword = detect_keywords(item['description'], keywords)
        
        if contains_keyword:
            item['relevance'] = 'alta' if sentiment == 'NEGATIVE' else 'media'
        else:
            item['relevance'] = 'baja'
        
        classified_data.append(item)

    return classified_data

# Resumir datos
def summarize_data(data):
    logging.info("Resumiendo las descripciones de las noticias...")
    for item in data:
        item['summary'] = summarize_text(item['description'])
    return data

# Presentar y almacenar resultados
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

            if not exists_in_db_genero_opinion(item['title']):
                insert_into_db_genero_opinion(item)
            else:
                logging.info(f"El título ya existe en la base de datos: {item['title']}")

# Función principal de scraping
def scrape_data():
    existing_titles = set()  # Evitar duplicados

    raw_data = extract_data(existing_titles)  # Paso 1: Extraer datos
    processed_data = preprocess_data(raw_data)  # Paso 2: Preprocesar datos
    classified_data = classify_data(processed_data)  # Paso 3: Clasificar relevancia
    summarized_data = summarize_data(classified_data)  # Paso 4: Resumir descripciones
    present_results(summarized_data)  # Paso 5: Presentar resultados

if __name__ == "__main__":
    scrape_data()
