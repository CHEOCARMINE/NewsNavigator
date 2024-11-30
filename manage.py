from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, Response, redirect, url_for, session, flash, send_file
from database import get_db_connection, registrar_usuario, autenticar_usuario, existe_usuario, modificar_usuario, eliminar_usuario
from webscraping import run_scraping
from apscheduler.schedulers.background import BackgroundScheduler  
from functools import wraps
from datetime import datetime
import pandas as pd
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
app.secret_key = 'tu_clave_secreta'

# Función para ejecutar todos los scrapers
def ejecutar_todo_el_scraping():
    categories = ['informacion_relevante', 'seguridad', 'gobierno_mexico', 'genero_opinion']
    for category in categories:
        logging.debug(f'Ejecutando scraping para la categoría: {category}')
        run_scraping(category)
        logging.debug(f'Scraping para la categoría {category} completado.')

# Configurar el programador
scheduler = BackgroundScheduler()
scheduler.add_job(ejecutar_todo_el_scraping, 'cron', hour=23, minute=30)  
scheduler.start() 

# Rutas para obtener datos en formato JSON "informacion_relevante"
@app.route('/api/data', methods=['GET'])
def get_data():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    source = request.args.get('source')

    query = 'SELECT titulo, resumen, fecha, link, fuente FROM informacion_relevante WHERE 1=1'

    # Filtrar por fecha
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    # Filtrar por fuente
    if source:
        query += f" AND fuente = '{source}'"

    query += ' ORDER BY fecha DESC'

    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3],
            'fuente': row[4]
        }
        response.append(item)

    connection.close()
    return jsonify(response)

# Rutas para obtener datos en formato JSON "seguridad" 
@app.route('/api/seguridad', methods=['GET'])
def get_seguridad():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    source = request.args.get('source')

    query = 'SELECT titulo, resumen, fecha, link, fuente FROM seguridad WHERE 1=1'
    
    # Filtrar por fecha
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    # Filtrar por fuente
    if source:
        query += f" AND fuente = '{source}'"

    query += ' ORDER BY fecha DESC'
    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3],
            'fuente': row[4]
        }
        response.append(item)

    connection.close()
    return jsonify(response)

# Rutas para obtener datos en formato JSON "gobierno_mexico"
@app.route('/api/gobierno_mexico', methods=['GET'])
def get_gobierno_mexico():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    source = request.args.get('source')

    query = 'SELECT titulo, resumen, fecha, link, fuente FROM gobierno_mexico WHERE 1=1'

    # Filtrar por fecha
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    # Filtrar por fuente
    if source:
        query += f" AND fuente = '{source}'"

    query += ' ORDER BY fecha DESC'

    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3],
            'fuente': row[4]
        }
        response.append(item)

    connection.close()
    return jsonify(response)

# Rutas para obtener datos en formato JSON "genero_opinion"
@app.route('/api/genero_opinion', methods=['GET'])
def get_genero_opinion():
    connection = get_db_connection()
    cursor = connection.cursor()

    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    source = request.args.get('source')

    query = 'SELECT titulo, resumen, fecha, link, fuente FROM genero_opinion WHERE 1=1'

    # Filtrar por fecha
    if start_date:
        query += f" AND fecha >= '{start_date}'"
    if end_date:
        query += f" AND fecha <= '{end_date}'"

    # Filtrar por fuente
    if source:
        query += f" AND fuente = '{source}'"

    query += ' ORDER BY fecha DESC'

    cursor.execute(query)
    data = cursor.fetchall()

    response = []
    for row in data:
        item = {
            'titulo': row[0],
            'descripcion': row[1],
            'fecha': row[2],
            'link': row[3],
            'fuente': row[4]
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

# Ruta para ejecutar el web scraping
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

# Ruta para exportar a Excel
@app.route('/exportar_a_excel', methods=['GET'])
def exportar_a_excel():
    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')

    connection = get_db_connection()
    cursor = connection.cursor()

    # Consulta para 'informacion_relevante'
    query_informacion_relevante = 'SELECT titulo, resumen, fecha, link FROM informacion_relevante WHERE 1=1'
    if fecha_desde:
        query_informacion_relevante += f" AND fecha >= '{fecha_desde}'"
    if fecha_hasta:
        query_informacion_relevante += f" AND fecha <= '{fecha_hasta}'"
    query_informacion_relevante += ' ORDER BY fecha DESC'
    
    cursor.execute(query_informacion_relevante)
    data_informacion_relevante = cursor.fetchall()

    # Consulta para 'seguridad'
    query_seguridad = 'SELECT titulo, resumen, fecha, link FROM seguridad WHERE 1=1'
    if fecha_desde:
        query_seguridad += f" AND fecha >= '{fecha_desde}'"
    if fecha_hasta:
        query_seguridad += f" AND fecha <= '{fecha_hasta}'"
    query_seguridad += ' ORDER BY fecha DESC'
    
    cursor.execute(query_seguridad)
    data_seguridad = cursor.fetchall()

    # Consulta para 'gobierno_mexico'
    query_gobierno_mexico = 'SELECT titulo, resumen, fecha, link FROM gobierno_mexico WHERE 1=1'
    if fecha_desde:
        query_gobierno_mexico += f" AND fecha >= '{fecha_desde}'"
    if fecha_hasta:
        query_gobierno_mexico += f" AND fecha <= '{fecha_hasta}'"
    query_gobierno_mexico += ' ORDER BY fecha DESC'
    
    cursor.execute(query_gobierno_mexico)
    data_gobierno_mexico = cursor.fetchall()

    # Consulta para 'genero_opinion'
    query_genero_opinion = 'SELECT titulo, resumen, fecha, link FROM genero_opinion WHERE 1=1'
    if fecha_desde:
        query_genero_opinion += f" AND fecha >= '{fecha_desde}'"
    if fecha_hasta:
        query_genero_opinion += f" AND fecha <= '{fecha_hasta}'"
    query_genero_opinion += ' ORDER BY fecha DESC'
    
    cursor.execute(query_genero_opinion)
    data_genero_opinion = cursor.fetchall()

    # Crear DataFrames con los datos
    df_informacion_relevante = pd.DataFrame(data_informacion_relevante, columns=['Título', 'Descripción', 'Fecha', 'Link'])
    df_seguridad = pd.DataFrame(data_seguridad, columns=['Título', 'Descripción', 'Fecha', 'Link'])
    df_gobierno_mexico = pd.DataFrame(data_gobierno_mexico, columns=['Título', 'Descripción', 'Fecha', 'Link'])
    df_genero_opinion = pd.DataFrame(data_genero_opinion, columns=['Título', 'Descripción', 'Fecha', 'Link'])

    # Crear el directorio temporal si no existe
    temp_dir = os.path.join(os.getcwd(), 'tmp')  
    os.makedirs(temp_dir, exist_ok=True)  
    temp_path = os.path.join(temp_dir, 'reporte_completo.xlsx')

    # Escribe múltiples hojas en un archivo Excel
    with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
        df_informacion_relevante.to_excel(writer, sheet_name='Información Relevante', index=False)
        df_seguridad.to_excel(writer, sheet_name='Seguridad', index=False)
        df_gobierno_mexico.to_excel(writer, sheet_name='Gobierno de México', index=False)
        df_genero_opinion.to_excel(writer, sheet_name='Géneros de Opinión', index=False)

    connection.close()

    # Devolver el archivo Excel como respuesta
    return send_file(temp_path, as_attachment=True, download_name='reporte_completo.xlsx')

# Decorador para requerir autenticación en ciertas rutas
def login_requerido(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Debes iniciar sesión primero.", "danger")
            return redirect(url_for('login'))
    return wrap

# Decorador para requerir rol de administrador
def admin_requerido(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('rol') == 'administrador':
            return f(*args, **kwargs)
        else:
            flash("No tienes permiso para acceder a esta página.", "danger")
            return redirect(url_for('index'))
    return wrap

# Ruta de login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        # Autenticar usuario
        autenticado, rol = autenticar_usuario(usuario, contraseña)
        if autenticado:
            session['logged_in'] = True
            session['usuario'] = usuario
            session['rol'] = rol
            flash(f"Bienvenido, {usuario}!", "success")
            return redirect(url_for('index'))
        else:
            flash("Credenciales incorrectas, por favor intenta de nuevo.", "danger")
    return render_template('login.html')

# Ruta de logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente.", "success")
    return redirect(url_for('login'))

# Ruta protegida para administradores
@app.route("/admin_dashboard", methods=['GET', 'POST'])
@login_requerido
@admin_requerido
def admin_dashboard():
    current_date = datetime.now().strftime('%Y-%m-%d')
    usuarios = obtener_usuarios() 

    if request.method == 'POST':
        if 'registrar' in request.form:
            usuario = request.form['usuario']
            contraseña = request.form['contraseña']
            rol = request.form['rol']

            if existe_usuario(usuario):
                flash("Este usuario ya existe.", "danger")
            else:
                registrar_usuario(usuario, contraseña, rol)
                flash(f"Usuario {usuario} registrado con éxito.", "success")

        elif 'modificar' in request.form:
            usuario_id = request.form['usuario_id']
            nuevo_usuario = request.form['nuevo_usuario']
            nueva_contraseña = request.form['nueva_contraseña']  
            nuevo_rol = request.form['nuevo_rol']
            
            # Verificamos si la nueva contraseña no está vacía antes de modificar
            if nueva_contraseña:
                modificar_usuario(usuario_id, nuevo_usuario, nueva_contraseña, nuevo_rol)
            else:
                modificar_usuario(usuario_id, nuevo_usuario, None, nuevo_rol)  
            
            flash("Usuario modificado con éxito.", "success")

        elif 'eliminar' in request.form:
            usuario_id = request.form['usuario_id_eliminar']
            eliminar_usuario(usuario_id)
            flash("Usuario eliminado con éxito.", "success")
        
        return redirect(url_for('admin_dashboard'))  
    
    return render_template('admin_dashboard.html', usuarios=usuarios, current_date=current_date)

# Función para obtener la lista de usuarios
def obtener_usuarios():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, usuario, rol FROM usuarios")  
    usuarios = cursor.fetchall()
    connection.close()
    return usuarios

# Ruta para la página principal
@app.route("/")
@login_requerido
def index():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('index.html', current_date=current_date)

# Ruta para la página seguridad
@app.route('/seguridad')
@login_requerido
def seguridad():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('seguridad.html', current_date=current_date)

# Ruta para la página gobierno_mexico
@app.route('/gobierno_mexico')
@login_requerido
def gobierno_mexico():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('gobierno_mexico.html', current_date=current_date)  

# Ruta para la página genero_opinion
@app.route('/genero_opinion')
@login_requerido
def genero_opinion():
    current_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('genero_opinion.html', current_date=current_date) 

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(debug=False, host='0.0.0.0', port=port)