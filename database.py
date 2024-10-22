import mysql.connector
from dotenv import load_dotenv
import os
import logging

load_dotenv()

def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    return connection

#informacion_relevante
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
    
    sql = """INSERT INTO informacion_relevante (titulo, resumen, fecha, link, relevancia) 
             VALUES (%s, %s, %s, %s, %s)"""
    values = (item['title'], item['summary'], item['date'], item['link'], item['relevance'])
    
    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Datos insertados: {item['title']}")
    except Exception as e:
        logging.info(f"Error al insertar datos: {e}")
    finally:
        cursor.close()
        connection.close()

#seguridad
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
    
    sql = """INSERT INTO seguridad (titulo, resumen, fecha, link, relevancia) 
             VALUES (%s, %s, %s, %s, %s)"""
    values = (item['title'], item['summary'], item['date'], item['link'], item['relevance'])
    
    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Datos insertados: {item['title']}")
    except Exception as e:
        logging.info(f"Error al insertar datos: {e}")
    finally:
        cursor.close()
        connection.close()

#gobierno_mexico
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
    
    sql = """INSERT INTO gobierno_mexico (titulo, resumen, fecha, link, relevancia) 
             VALUES (%s, %s, %s, %s, %s)"""
    values = (item['title'], item['summary'], item['date'], item['link'], item['relevance'])
    
    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Datos insertados: {item['title']}")
    except Exception as e:
        logging.info(f"Error al insertar datos: {e}")
    finally:
        cursor.close()
        connection.close()

#genero_opinion
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
    
    sql = """INSERT INTO genero_opinion (titulo, resumen, fecha, link, relevancia) 
             VALUES (%s, %s, %s, %s, %s)"""
    values = (item['title'], item['summary'], item['date'], item['link'], item['relevance'])
    
    try:
        cursor.execute(sql, values)
        connection.commit()
        logging.info(f"Datos insertados: {item['title']}")
    except Exception as e:
        logging.info(f"Error al insertar datos: {e}")
    finally:
        cursor.close()
        connection.close()
