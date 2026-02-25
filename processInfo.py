import re

def procesar_ejercicio(texto_crudo):
    mapeo_groups = {
        "pectoral": "Pecho",
        "tríceps": "Tríceps",
        "triceps": "Tríceps",
        "abdominales": "Abdomen",
        "hombros": "Hombros"
    }

    # 1. Extraer Título (Texto antes de DIFICULTAD)
    # Buscamos todo lo que esté al inicio hasta encontrar "DIFICULTAD"
    match_titulo = re.search(r'^(.*?)\s*DIFICULTAD:', texto_crudo, re.DOTALL | re.IGNORECASE)
    titulo = match_titulo.group(1).strip() if match_titulo else "Sin título"

    # 2. Contar Emojis en DIFICULTAD
    # Buscamos la línea de dificultad y contamos el emoji de músculo 💪
    match_dif = re.search(r'DIFICULTAD:\s*(.*)', texto_crudo, re.IGNORECASE)
    dificultad_num = 0
    if match_dif:
        linea_dif = match_dif.group(1)
        dificultad_num = linea_dif.count("💪")

    # 3. Mapeo de Músculos
    # Extraemos lo que hay entre "MÚSCULOS IMPLICADOS:" y la siguiente etiqueta
    match_musculos = re.search(r'MÚSCULOS IMPLICADOS:\s*(.*?)(?=\n[A-ZÁÉÍÓÚ\s]+:|$)', texto_crudo, re.DOTALL | re.IGNORECASE)
    musculos_procesados = []
    if match_musculos:
        # Separamos por "y" o comas, limpiamos espacios y pasamos a minúsculas
        lista_raw = re.split(r',| y ', match_musculos.group(1).lower())
        for m in lista_raw:
            limpio = m.strip()
            # Si el músculo está en nuestro mapa, usamos el valor nuevo, si no, el original capitalizado
            musculos_procesados.append(mapeo_groups.get(limpio, limpio.capitalize()))

    # 4. Extraer Descripción
    # Todo lo que esté después de "DESCRIPCIÓN:"
    match_desc = re.search(r'DESCRIPCIÓN:\s*(.*)', texto_crudo, re.DOTALL | re.IGNORECASE)
    descripcion = match_desc.group(1).strip() if match_desc else ""

    return {
        "titulo": titulo,
        "nivel_dificultad": dificultad_num,
        "grupos_musculares": musculos_procesados,
        "descripcion": descripcion
    }

texto_ejemplo = """Guía Completa de Calistenia y Street Workout 
 
23 
 
FLEXIONES ESFINGE 
 
DIFICULTAD:  💪 💪 
MÚSCULOS IMPLICADOS: Tríceps 
PROGRESIONES PARA CONSEGUIRLO: Flexiones, 
flexiones diamante. 
SIRVE DE PROGRESIÓN PARA: Flexiones a codos,
extensiones de tríceps en barra baja, esfinge en x.
DESCRIPCIÓN: Las manos se colocan en posición
adelantada y los codos apoyados en el suelo.
Ejercicio de aislamiento de tríceps.
"""

resultado = procesar_ejercicio(texto_ejemplo)
print(resultado)