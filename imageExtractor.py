import fitz  # PyMuPDF
import os

def extraer_imagenes(pdf_path, start_page, end_page, output_folder="imagenes"):
    
    os.makedirs(output_folder, exist_ok=True)

    doc = fitz.open(pdf_path)
    p_start = max(0, start_page - 1)
    p_end = min(len(doc), end_page)

    for num_pagina in range(p_start, p_end):
        pagina = doc[num_pagina]
        lista_imagenes = pagina.get_images(full=True)

        for i, img in enumerate(lista_imagenes):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            extension = base_image["ext"]

            nombre_imagen = f"pagina{num_pagina+1}_img{i+1}.{extension}"
            ruta = os.path.join(output_folder, nombre_imagen)

            with open(ruta, "wb") as f:
                f.write(image_bytes)

            print(f"Guardada: {ruta}")

    doc.close()

extraer_imagenes("GuiaCalistenia.pdf", 21, 31)