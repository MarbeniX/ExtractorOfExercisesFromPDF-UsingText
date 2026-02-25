import fitz
import re
import json
import os

def process_entire_pdf(pdf_path, start_page, end_page, output_folder="imagenes"):
    os.makedirs(output_folder, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    every_exercise = []

    p_start = max(0, start_page - 1)
    p_end = min(len(doc), end_page)

    for page_num in range(p_start, p_end): 
        page = doc.load_page(page_num)

        imagenes_por_pagina = page.get_images(full=True)
        for i, img in enumerate(imagenes_por_pagina):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            extension = base_image["ext"]

            nombre_imagen = f"pagina{page_num+1}_img{i+1}.{extension}"
            ruta = os.path.join(output_folder, nombre_imagen)

            with open(ruta, "wb") as f:
                f.write(image_bytes)

            print(f"Guardada: {ruta}")

        text = page.get_text()
        text = text.replace('\xa0', ' ')
        text = text.replace('\r\n', '\n')

        exercises_on_page = procesar_pagina_calistenia(text)
        for i, ex in enumerate(exercises_on_page):
            ex['image'] = f"pagina{page_num+1}_img{i+1}.{extension}"
        every_exercise.extend(exercises_on_page)

    doc.close()
    return every_exercise


def procesar_pagina_calistenia(texto_pagina):

    mapeo_groups = {
        "pectoral": "Pecho",
        "triceps": "Tríceps",
        "abdominales": "Abdomen",
        "hombros": "Hombros",
        "espalda": "Espalda",
        "bíceps": "Bíceps",
        "antebrazos": "Antebrazos",
        "cuadríceps": "Piernas",
        "glúteos": "Glúteos",
        "gemelos": "Pantorrillas",
        "femoral": "Piernas",
        "lumbares": "Lumbar",
        "lumbar": "Lumbar",
        "dorsal": "Espalda",
        "hombro": "Hombros",
        "core": "Abdomen",
        "oblícuos": "Oblicuos",
        "trapecio": "Trapecios",
    }

    # --- PASO 1: LIMPIEZA ---
    texto_limpio = texto_pagina.replace('\xa0', ' ')

    # --- PASO 2: SEGMENTACIÓN CORRECTA ---
    # Dividimos cuando empieza un nuevo ejercicio
    bloques_crudos = re.split(
        r'\n(?=[A-ZÁÉÍÓÚÑ\s]+\n\s*\nDIFICULTAD:)',
        texto_limpio
    )

    # Nos quedamos solo con bloques válidos
    bloques_crudos = [
        b.strip() for b in bloques_crudos
        if "DIFICULTAD:" in b and "MÚSCULOS IMPLICADOS:" in b
    ]

    resultados = []

    for bloque in bloques_crudos:

        # --- TÍTULO ---
        match_titulo = re.search(r'(.*?)\s*DIFICULTAD:', bloque, re.DOTALL)
        if not match_titulo:
            continue

        lineas = [l.strip() for l in match_titulo.group(1).split('\n') if l.strip()]
        titulo = lineas[-1] if lineas else "Sin Título"
        titulo = titulo.lower().capitalize()

        # --- DIFICULTAD ---
        match_dif = re.search(r'DIFICULTAD:\s*([^\n]*)', bloque)
        nivel = match_dif.group(1).count("💪") if match_dif else 0

        # --- MÚSCULOS ---
        musculos = []
        match_musc = re.search(
            r'MÚSCULOS IMPLICADOS:\s*(.*?)(?=PROGRESIONES|SIRVE|DESCRIPCIÓN|$)',
            bloque,
            re.DOTALL
        )

        if match_musc:
            txt_m = (
                match_musc.group(1)
                .replace('\n', ' ')
                .replace('.', '')
                .lower()
            )

            items = re.split(r',|\sy\s', txt_m)

            musculos = [
                mapeo_groups.get(i.strip(), i.strip().capitalize())
                for i in items if i.strip()
            ]

            # Eliminar duplicados manteniendo orden
            musculos = list(dict.fromkeys(musculos))

        # --- DESCRIPCIÓN ---
        descripcion = ""
        match_desc = re.search(r'DESCRIPCIÓN:\s*(.*)', bloque, re.DOTALL)

        if match_desc:
            desc_raw = match_desc.group(1).strip()
            desc_clean = re.split(r'\n\s*\n', desc_raw)[0]
            descripcion = " ".join(desc_clean.split())

        resultados.append({
            "name": titulo,
            "level": nivel,
            "muscles": musculos,
            "description": descripcion
        })

    return resultados
        
resultados = process_entire_pdf("GuiaCalistenia.pdf", 21, 31)
print(json.dumps(resultados, indent=4, ensure_ascii=False))