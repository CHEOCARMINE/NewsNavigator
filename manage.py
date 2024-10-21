from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, Response
from database import get_db_connection
from webscraping import run_scraping
from apscheduler.schedulers.background import BackgroundScheduler  
import os
import sys
import io
import logging
import time

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuración de Flask
app = Flask(__name__)

# Función para ejecutar todos los scrapers
def ejecutar_todo_el_scraping():
    categories = ['informacion_relevante', 'seguridad', 'gobierno_mexicano', 'genero_opinion']
    for category in categories:
        logging.debug(f'Ejecutando scraping para la categoría: {category}')
        run_scraping(category)
        logging.debug(f'Scraping para la categoría {category} completado.')

# Configurar el programador
scheduler = BackgroundScheduler()
scheduler.add_job(ejecutar_todo_el_scraping, 'cron', hour=22, minute=30)  
scheduler.start()

# Ruta para la tabla "informacion_relevante"
@app.route('/')
def index():
    return render_template('index.html')  

# Ruta para la tabla "seguridad"
@app.route('/seguridad')
def seguridad():
    return render_template('seguridad.html')

# Ruta para la tabla "gobierno_mexico"
@app.route('/gobierno_mexico')
def gobierno_mexico():
    return render_template('gobierno_mexico.html')  

# Ruta para la tabla "genero_opinion"
@app.route('/genero_opinion')
def genero_opinion():
    return render_template('genero_opinion.html') 

# Ruta para obtener los datos de "informacion_relevante" en formato JSON con filtrado por fecha
@app.route('/api/data', methods=['GET'])
def get_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Obtener los parámetros de fecha de la solicitud
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = 'SELECT titulo, resumen, fecha, link FROM informacion_relevante WHERE 1=1'
    
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"
    
    query += ' ORDER BY fecha DESC'
    
    cursor.execute(query)
    data = cursor.fetchall()
    
    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3]
        }
        response.append(item)
    
    connection.close()
    return jsonify(response)

# Ruta para obtener los datos de "seguridad" en formato JSON con filtrado por fecha
@app.route('/api/seguridad', methods=['GET'])
def get_seguridad():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = 'SELECT titulo, resumen, fecha, link FROM seguridad WHERE 1=1'
    
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    query += ' ORDER BY fecha DESC'

    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3]
        }
        response.append(item)
    
    connection.close()
    return jsonify(response)

# Ruta para obtener los datos de "gobierno_mexico" en formato JSON con filtrado por fecha
@app.route('/api/gobierno_mexico', methods=['GET'])
def get_gobierno_mexico():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = 'SELECT titulo, resumen, fecha, link FROM gobierno_mexico WHERE 1=1'
    
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    query += ' ORDER BY fecha DESC'

    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3]
        }
        response.append(item)
    
    connection.close()
    return jsonify(response)

# Ruta para obtener los datos de "genero_opinion" en formato JSON con filtrado por fecha
@app.route('/api/genero_opinion', methods=['GET'])
def get_genero_opinion():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = 'SELECT titulo, resumen, fecha, link FROM genero_opinion WHERE 1=1'
    
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    query += ' ORDER BY fecha DESC'

    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3]
        }
        response.append(item)
    
    connection.close()
    return jsonify(response)

# Ruta para manejar el progreso del scraping
@app.route('/progress_scraping', methods=['GET'])
def progress_scraping():
    def generate_progress():
        for i in range(101):  
            time.sleep(0.1)  
            yield f"data:{i}\n\n"
    return Response(generate_progress(), mimetype='text/event-stream')

# Ruta para ejecutar el web scraping con progreso
@app.route('/scraping', methods=['POST'])
def scraping():   
    try:
        data = request.get_json()  
        category = data.get('category')  
        if not category:
            return jsonify({'status': 'error', 'message': 'Categoría no especificada.'}), 400

        logging.debug(f'Iniciando búsqueda para la categoría: {category}')
        run_scraping(category) 
        logging.debug(f'Búsqueda completada para la categoría: {category}')
        return jsonify({'status': 'success', 'message': f'Búsqueda para la categoría {category} completada.'})
    except Exception as e:
        logging.error(f'Error durante la búsqueda: {str(e)}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    with open(os.devnull, 'w') as f:
        sys.stdout = f  
        app.run(debug=True)
    sys.stdout = sys.__stdout__
