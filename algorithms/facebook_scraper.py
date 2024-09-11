import requests
import json

# Tu token de acceso de Facebook
ACCESS_TOKEN = '1f579e17a50a9b09a212cab028b08c0e'

# Endpoint base de la API Graph
base_url = 'https://graph.facebook.com/v16.0/'

# Definir un término de búsqueda, en este caso "Campeche"
search_query = 'Campeche'
# Puedes ajustar los parámetros como tipo de resultado, idioma, etc.
search_url = f'{base_url}search?q={search_query}&type=page&access_token={ACCESS_TOKEN}'

def search_facebook_pages(search_url):
    # Realizar la solicitud a la API de Facebook
    response = requests.get(search_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error en la solicitud: {response.status_code}, {response.text}")

# Ejecutar la búsqueda
resultados = search_facebook_pages(search_url)

# Imprimir los resultados obtenidos
for page in resultados.get('data', []):
    print(f"Nombre: {page['name']}")
    print(f"ID: {page['id']}")
    print('---')

# Luego, puedes usar los IDs de las páginas para obtener sus publicaciones
def get_page_posts(page_id, access_token):
    posts_url = f'{base_url}{page_id}/posts?access_token={access_token}'
    response = requests.get(posts_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error en la solicitud: {response.status_code}, {response.text}")

# Por ejemplo, obteniendo las publicaciones de una página en específico
page_id = 'ID_DE_UNA_PAGINA'
posts = get_page_posts(page_id, ACCESS_TOKEN)

# Imprimir las publicaciones obtenidas
for post in posts.get('data', []):
    print(f"Post ID: {post['id']}")
    print(f"Mensaje: {post.get('message', 'No hay mensaje')}")
    print('---')
