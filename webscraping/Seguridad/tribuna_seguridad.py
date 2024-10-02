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

#Forzar la salida UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Inicialización de las herramientas de NLP
nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")
sentiment_analyzer = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

# Configuración de Localización
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Fecha Objetivo
date= date= datetime.now().strftime("%d de %B de %Y")
target_date = datetime.strptime(date, "%d de %B de %Y")

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

# Extraer Datos
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
                print(f"No se encontró el contenedor principal en {url}")
                continue

            # Buscar las noticias
            articles = container.find_all('div', class_='read-details')

            for article in articles:
                title_div = article.find('div', class_='read-title')
                title = title_div.find('h4').text.strip() if title_div else "No title found"
                
                # Filtrar el titulo duplicados
                if title in existing_titles:
                    print(f"Noticia duplicada encontrada: {title}")
                    continue

                existing_titles.add(title)

                # Extraer la fecha de la noticia
                date_span = article.find('span', class_='item-metadata posts-date')
                date = date_span.text.strip() if date_span else "No date found"

                # Convertir la fecha a un objeto datetime
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
                print(f"Title: {title}")
                print(f"Description: {description}")
                print(f"Date: {date}")
                print(f"Link: {link}")

                # Lista de datos recopilados
                news_item = {
                    'title': title,
                    'description': description,
                    'date': date,
                    'link': link
                }
                all_data.append(news_item)
            
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"Error al extraer datos de la página de noticias {url}: {e}")

    return all_data

# Preprocesar Datos
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

# Detectar Palabras Clave
def detect_keywords(description, keywords):
    return any(keyword in description for keyword in keywords)

# Clasificar Datos
def classify_data(data):
    print("Clasificando la relevancia de las noticias...")
    keywords = ['delito federal', 'narcotráfico', 'tráfico de drogas', 'crimen organizado', 
                'lavado de dinero', 'corrupción', 'delitos fiscales', 'contrabando', 
                'fraude fiscal', 'evasión fiscal', 'delitos electorales', 'delincuencia organizada', 
                'tráfico de armas', 'secuestro', 'trata de personas', 'terrorismo', 
                'delitos contra la salud', 'falsificación de documentos', 'fraude', 
                'delitos financieros', 'delitos ambientales', 'crimen transnacional', 
                'extorsión', 'homicidio', 'robo de combustible', 'huachicol', 
                'delitos informáticos', 'hackeo', 'piratería']# Ppalabras clave
    
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
    print("Resumiendo las descripciones de las noticias...")
    for item in data:
        item['summary'] = summarize_text(item['description'])
    return data

# Presentar Resultados
def present_results(data):
    print("Presentando los resultados...")
    for item in data:
        print("\n")
        print(f"Titulo: {item['title']}".encode('utf-8', errors='ignore').decode('utf-8'))
        print(f"Resumen: {item['summary']}".encode('utf-8', errors='ignore').decode('utf-8'))
        print(f"Fecha: {item['date']}".encode('utf-8', errors='ignore').decode('utf-8'))
        print(f"Link: {item['link']}".encode('utf-8', errors='ignore').decode('utf-8'))
        print(f"Importancia: {item['relevance']}".encode('utf-8', errors='ignore').decode('utf-8'))
        print("\n")

# Función Principal
def main():
    existing_titles = set()  # Evitar duplicados

    raw_data = extract_data(existing_titles)  # Paso 1: Extraer datos
    processed_data = preprocess_data(raw_data)  # Paso 2: Preprocesar datos
    classified_data = classify_data(processed_data)  # Paso 3: Clasificar relevancia
    summarized_data = summarize_data(classified_data)  # Paso 4: Resumir descripciones
    present_results(summarized_data)  # Paso 5: Presentar resultados

if __name__ == "__main__":
    main()
