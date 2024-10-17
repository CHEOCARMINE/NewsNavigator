from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from database import get_db_connection

load_dotenv()

# Configuración de Flask
app = Flask(__name__)

# Ruta para de la tabla "informacion_relevante"
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
    
    # Consulta SQL con filtrado por fecha
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

if __name__ == '__main__':
    app.run(debug=True)