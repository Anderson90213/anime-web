from flask import Flask, render_template, request, jsonify
import requests
from deep_translator import GoogleTranslator
from database import agregar_favorito, eliminar_favorito, obtener_favoritos, es_favorito

app = Flask(__name__)
traductor = GoogleTranslator(source='en', target='es')

# Diccionarios de traducción
ESTADOS_TRAD = {
    'Finished Airing': 'Emisión finalizada',
    'Currently Airing': 'En emisión',
    'Not yet aired': 'Aún no se emite'
}

GENEROS_TRAD = {
    'Action': 'Acción', 'Adventure': 'Aventura', 'Fantasy': 'Fantasía',
    'Comedy': 'Comedia', 'Drama': 'Drama', 'Romance': 'Romance',
    'Sci-Fi': 'Ciencia Ficción', 'Horror': 'Terror', 'Mystery': 'Misterio',
    'Suspense': 'Suspenso', 'Thriller': 'Thriller', 'Supernatural': 'Sobrenatural'
}

RATINGS_TRAD = {
    'G - All Ages': 'G - Todas las edades',
    'PG - Children': 'PG - Niños',
    'PG-13 - Teens 13 or older': 'PG-13 - Adolescentes 13+',
    'R - 17+ (violence & profanity)': 'R - 17+ (Violencia y lenguaje fuerte)',
    'R+ - Mild Nudity': 'R+ - Desnudez leve'
}

def traducir_genero(g):
    return GENEROS_TRAD.get(g, g)

def traducir_estado(e):
    return ESTADOS_TRAD.get(e, e)

def traducir_rating(r):
    return RATINGS_TRAD.get(r, r)

def traducir_texto(t):
    if not t or len(t) < 10: 
        return t
    try: 
        return traductor.translate(t)
    except: 
        return t

def obtener_top_animes():
    try:
        url = "https://api.jikan.moe/v4/top/anime?filter=bypopularity&limit=6"
        resp = requests.get(url)
        data = resp.json()
        top_animes = []
        for item in data.get('data', []):
            top_animes.append({
                'mal_id': item.get('mal_id'),
                'titulo': item.get('title', ''),
                'imagen': item.get('images', {}).get('jpg', {}).get('large_image_url', ''),
                'score': item.get('score', 'N/A')
            })
        return top_animes
    except Exception as e:
        print("Error obteniendo top animes:", e)
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    anime = None
    top_animes = obtener_top_animes()
    
    if request.method == 'POST':
        busqueda = request.form.get('busqueda')
        if busqueda:
            try:
                url = f"https://api.jikan.moe/v4/anime?q={busqueda}&limit=1"
                resp = requests.get(url)
                data = resp.json()
                
                if data.get('data'):
                    anime_raw = data['data'][0]
                    anime_id = anime_raw.get('mal_id')
                    
                    generos_en = [g['name'] for g in anime_raw.get('genres', [])]
                    generos = [traducir_genero(g) for g in generos_en]
                    
                    aired = anime_raw.get('aired', {})
                    fecha = aired.get('from', '')
                    if fecha:
                        fecha = fecha.split('-')[0]
                    
                    estado_en = anime_raw.get('status', '')
                    estado = traducir_estado(estado_en)
                    
                    rating_en = anime_raw.get('rating', '')
                    rating = traducir_rating(rating_en)
                    
                    sinopsis_en = anime_raw.get('synopsis', '')
                    sinopsis = traducir_texto(sinopsis_en)
                    
                    anime = {
                        'mal_id': anime_id,
                        'titulo': anime_raw.get('title', 'Sin título'),
                        'titulo_japones': anime_raw.get('title_japanese', ''),
                        'imagen': anime_raw.get('images', {}).get('jpg', {}).get('large_image_url', ''),
                        'sinopsis': sinopsis,
                        'score': anime_raw.get('score', 'N/A'),
                        'generos': generos,
                        'año': fecha or 'N/A',
                        'episodios': anime_raw.get('episodes') or 'En emisión',
                        'estado': estado or 'Desconocido',
                        'rating': rating or 'N/A',
                        'url': anime_raw.get('url', ''),
                        'es_favorito': es_favorito(anime_id)
                    }
            except Exception as e:
                print("Error en búsqueda:", e)
    
    return render_template('index.html', anime=anime, top_animes=top_animes)

@app.route('/favoritos')
def ver_favoritos():
    favoritos_raw = obtener_favoritos()
    favoritos = []
    for fav in favoritos_raw:
        favoritos.append({
            'anime_id': fav[1],
            'titulo': fav[2],
            'imagen': fav[3],
            'score': fav[4]
        })
    return render_template('favoritos.html', favoritos=favoritos)

@app.route('/api/favorito/<int:anime_id>', methods=['POST'])
def toggle_favorito(anime_id):
    data = request.json
    titulo = data.get('titulo', '')
    imagen = data.get('imagen', '')
    score = data.get('score', 0)
    accion = data.get('accion', 'toggle')
    
    print(f"📩 Recibido: ID={anime_id}, Acción={accion}") # Debug
    
    if accion == 'agregar' or accion == 'toggle':
        # Si es toggle, verificamos si ya existe para decidir
        if accion == 'toggle' and es_favorito(anime_id):
             eliminar_favorito(anime_id)
             return jsonify({'success': True, 'message': 'Eliminado (Toggle)'})
        else:
            resultado = agregar_favorito(anime_id, titulo, imagen, score)
            return jsonify({'success': resultado, 'message': 'Guardado'})
            
    elif accion == 'eliminar':
        resultado = eliminar_favorito(anime_id)
        return jsonify({'success': resultado, 'message': 'Eliminado'})
    
    return jsonify({'success': False, 'message': 'Acción no válida'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)