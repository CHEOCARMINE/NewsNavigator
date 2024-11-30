import mysql.connector
from dotenv import load_dotenv
import os
import logging
from flask_bcrypt import Bcrypt

load_dotenv()
bcrypt = Bcrypt()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT')),
            charset='utf8mb4'
        )
        return connection
    except mysql.connector.Error as error:
        logging.error(f"Error al conectar a la base de datos: {error}")
        raise

# Función para verificar si el usuario ya existe
def existe_usuario(usuario):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = %s", (usuario,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

# Función para insertar un nuevo usuario (registro)
def registrar_usuario(usuario, contraseña, rol='usuario'):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Encriptar la contraseña
    hashed_password = bcrypt.generate_password_hash(contraseña).decode('utf-8')
    
    sql = "INSERT INTO usuarios (usuario, contraseña, rol) VALUES (%s, %s, %s)"
    values = (usuario, hashed_password, rol)

    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Usuario registrado: {usuario}")
    except Exception as e:
        logging.error(f"Error al registrar usuario: {e}")
    finally:
        cursor.close()
        connection.close()

# Función para autenticar un usuario
def autenticar_usuario(usuario, contraseña):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT contraseña, rol FROM usuarios WHERE usuario = %s", (usuario,))
    user_data = cursor.fetchone()

    cursor.close()
    connection.close()

    if user_data:
        hashed_password, rol = user_data
        if bcrypt.check_password_hash(hashed_password, contraseña):
            return True, rol
    return False, None

# Función para cambiar la contraseña
def cambiar_contraseña(usuario, contraseña_actual, nueva_contraseña):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT contraseña FROM usuarios WHERE usuario = %s", (usuario,))
    user_data = cursor.fetchone()

    if user_data:
        hashed_password = user_data[0]
        if bcrypt.check_password_hash(hashed_password, contraseña_actual):
            # Encriptar la nueva contraseña
            hashed_new_password = bcrypt.generate_password_hash(nueva_contraseña).decode('utf-8')
            sql = "UPDATE usuarios SET contraseña = %s WHERE usuario = %s"
            values = (hashed_new_password, usuario)

            try:
                cursor.execute(sql, values)
                connection.commit()
                logging.info(f"Contraseña cambiada para el usuario: {usuario}")
            except Exception as e:
                logging.error(f"Error al cambiar la contraseña: {e}")
        else:
            logging.error("Contraseña actual incorrecta.")
    else:
        logging.error("Usuario no encontrado.")
    
    cursor.close()
    connection.close()

# Función para modificar un usuario
def modificar_usuario(usuario_id, nuevo_usuario, nueva_contraseña=None, nuevo_rol=None):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Comenzamos la actualización
    if nueva_contraseña:
        hashed_new_password = bcrypt.generate_password_hash(nueva_contraseña).decode('utf-8')
        sql = "UPDATE usuarios SET usuario = %s, contraseña = %s, rol = %s WHERE id = %s"
        values = (nuevo_usuario, hashed_new_password, nuevo_rol, usuario_id)
    else:
        sql = "UPDATE usuarios SET usuario = %s, rol = %s WHERE id = %s"
        values = (nuevo_usuario, nuevo_rol, usuario_id)

    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Usuario modificado: {nuevo_usuario}")
    except Exception as e:
        logging.error(f"Error al modificar usuario: {e}")
    finally:
        cursor.close()
        connection.close()

# Función para eliminar un usuario
def eliminar_usuario(usuario_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    sql = "DELETE FROM usuarios WHERE id = %s"
    values = (usuario_id,)

    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Usuario eliminado con ID: {usuario_id}")
    except Exception as e:
        logging.error(f"Error al eliminar usuario: {e}")
    finally:
        cursor.close()
        connection.close()

# Informacion relevante
def exists_in_db_informacion_relevante(title):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM informacion_relevante WHERE titulo = %s", (title,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

def insert_into_db_informacion_relevante(item):
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

# Seguridad
def exists_in_db_seguridad(title):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM seguridad WHERE titulo = %s", (title,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

def insert_into_db_seguridad(item):
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

# Gobierno México
def exists_in_db_gobierno_mexico(title):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM gobierno_mexico WHERE titulo = %s", (title,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

def insert_into_db_gobierno_mexico(item):
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

# Género Opinión
def exists_in_db_genero_opinion(title):
    connection = get_db_connection()
    cursor = connection.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM genero_opinion WHERE titulo = %s", (title,))
    exists = cursor.fetchone()[0] > 0
    cursor.close()
    connection.close()
    return exists

def insert_into_db_genero_opinion(item):
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
