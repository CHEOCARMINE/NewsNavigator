import requests
from bs4 import BeautifulSoup
import nltk
import spacy
from transformers import pipeline
import time
import locale
from datetime import datetime

# Inicialización de las herramientas de NLP
nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Configurar locale para manejar fechas en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Establecer la fecha objetivo para filtrar las noticias
target_date = datetime.strptime("12 de septiembre de 2024", "%d de %B de %Y")

# Función para truncar descripciones largas al límite que soporta el modelo de transformers
def truncate_description(description):
    tokenizer = sentiment_analyzer.tokenizer
    tokens = tokenizer(description, truncation=True, max_length=512, return_tensors="pt")
    truncated_description = tokenizer.decode(tokens['input_ids'][0], skip_special_tokens=True)
    return truncated_description

# Función para resumir el texto de las descripciones
def summarize_text(text):
    doc = nlp(text)
    sentences = list(doc.sents)
    summary = " ".join([sent.text for sent in sentences[:2]])  # Tomar las primeras dos oraciones
    return summary

# Función para extraer datos de las fuentes de noticias
def extract_data(existing_titles):
    print("Extrayendo datos de las fuentes...")

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
        "https://tribunacampeche.com/category/policia/page/2/"
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
            
            # Buscar el contenedor específico de las noticias
            container = soup.find('div', class_='af-container-row aft-archive-wrapper clearfix archive-layout-list')
            if not container:
                print(f"No se encontró el contenedor principal en {url}")
                continue

            # Buscar las noticias dentro del contenedor
            articles = container.find_all('div', class_='read-details')

            for article in articles:
                title_div = article.find('div', class_='read-title')
                title = title_div.find('h4').text.strip() if title_div else "No title found"
                
                # Filtrar si el título ya existe para evitar duplicados
                if title in existing_titles:
                    print(f"Noticia duplicada encontrada: {title}")
                    continue

                existing_titles.add(title)

                # Extraer la fecha de la noticia
                date_span = article.find('span', class_='item-metadata posts-date')
                date = date_span.text.strip() if date_span else "No date found"

                # Convertir la fecha extraída a un objeto datetime
                try:
                    article_date = datetime.strptime(date, "%d de %B de %Y")
                except ValueError:
                    print(f"Formato de fecha no reconocido: {date}")
                    continue

                # Filtrar noticias según la fecha objetivo
                if article_date != target_date:
                    print(f"Noticia fuera de la fecha objetivo: {title} - {date}")
                    continue

                # Extraer el enlace de la noticia
                link_div = article.find('div', class_='read-title')
                link = link_div.find('a').get('href') if link_div else "No link found"

                # Extraer la descripción completa de la noticia visitando el enlace
                try:
                    link_response = requests.get(link, headers=headers)
                    link_response.raise_for_status()
                    link_soup = BeautifulSoup(link_response.text, 'html.parser')
                    description_div = link_soup.find('div', class_='entry-content')
                    description = " ".join([p.text.strip() for p in description_div.find_all('p')]) if description_div else "No description found"

                except requests.exceptions.RequestException as e:
                    description = "No description found"

                # Imprimir detalles de la noticia
                print(f"Title: {title}")
                print(f"Description: {description}")
                print(f"Date: {date}")
                print(f"Link: {link}")

                # Agregar la noticia a la lista de datos recopilados
                news_item = {
                    'title': title,
                    'description': description,
                    'date': date,
                    'link': link
                }
                all_data.append(news_item)
            
            time.sleep(2)  # Esperar 2 segundos entre peticiones para evitar sobrecargar el servidor

        except requests.exceptions.RequestException as e:
            print(f"Error al extraer datos de la página de noticias {url}: {e}")

    return all_data

# Función para preprocesar los datos (e.g., convertir a minúsculas)
def preprocess_data(data):
    print("Preprocesando los datos...")
    processed_data = []

    for item in data:
        item['title'] = item['title'].lower()
        item['description'] = item['description'].lower()
        item['date'] = item['date'].lower()
        item['link'] = item['link'].lower()
        processed_data.append(item)

    return processed_data

# Función para detectar palabras clave en las descripciones
def detect_keywords(description, keywords):
    return any(keyword in description for keyword in keywords)

# Función para clasificar la relevancia de las noticias
def classify_data(data):
    print("Clasificando la relevancia de las noticias...")
    keywords = ['marcha', 'protesta', 'bloqueo carretero', 'cierre de vialidad', 'bloqueo a inmueble', 'aeropuerto bloqueado', 'caseta de peaje bloqueada', 'vía férrea bloqueada', 'ataque a autoridad', 'ataque a actor público', 'ataque a policía', 'ataque a activista', 'proceso electoral interrumpido', 'demanda de apoyo', 'inconformidad con normatividad', 'desastre natural', 'afectación gubernamental', 'protesta social', 'huelga del magisterio', 'universidad en paro', 'bloqueo en aeropuerto', 'manifestación masiva', 'interrupción de servicio público', 'movilización social', 'paralización de actividades', 'asamblea pública', 'contingencia gubernamental', 'sindicato en protesta', 'denuncia contra gobierno', 'resistencia civil', 'queja contra autoridades', 'marchas', 'bloqueos carreteros', 'bloqueos en vialidades', 'bloqueos a inmuebles', 'aeropuertos', 'casetas de peaje', 'vías férreas', 'ataques a actores públicos', 'ataques a policías', 'ataques a activistas', 'autoridades', 'proceso electoral', 'demanda de apoyo', 'inconformidad con normatividad gubernamental', 'desastres naturales', 'magisterio', 'protestas sociales', 'universidades']#poner las palabras de las noticias para su filtro
    
    classified_data = []
    for item in data:
        truncated_description = truncate_description(item['description'])
        sentiment = sentiment_analyzer(truncated_description)[0]['label']
        contains_keyword = detect_keywords(item['description'], keywords)
        
        # Asignar relevancia basado en palabras clave y sentimiento
        if contains_keyword:
            item['relevance'] = 'alta' if sentiment == 'NEGATIVE' else 'media'
        else:
            item['relevance'] = 'baja'
        
        classified_data.append(item)

    return classified_data

# Función para agregar un resumen a la descripción de las noticias
def summarize_data(data):
    print("Resumiendo las descripciones de las noticias...")
    for item in data:
        item['summary'] = summarize_text(item['description'])
    return data

# Función para presentar los resultados finales
def present_results(data):
    print("Presentando los resultados...")
    for item in data:
        print(f"Titulo: {item['title']}")
        print(f"Resumen: {item['summary']}")
        print(f"Fecha: {item['date']}")
        print(f"Link: {item['link']}")
        print(f"Importancia: {item['relevance']}\n")

# Función principal que controla el flujo del programa
def main():
    existing_titles = set()  # Evitar duplicados

    raw_data = extract_data(existing_titles)  # Paso 1: Extraer datos
    processed_data = preprocess_data(raw_data)  # Paso 2: Preprocesar datos
    classified_data = classify_data(processed_data)  # Paso 3: Clasificar relevancia
    summarized_data = summarize_data(classified_data)  # Paso 4: Resumir descripciones
    present_results(summarized_data)  # Paso 5: Presentar resultados

if __name__ == "__main__":
    main()
