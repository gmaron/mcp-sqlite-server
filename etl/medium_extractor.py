"""
Medium Export ETL Extractor (RAG Data Pipeline - Paso 1)

Dependencies:
pip install beautifulsoup4 lxml
"""

import os
import json
import logging
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# Configurar logging
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def read_files(directory_path: str) -> List[str]:
    """
    Lee todos los archivos HTML de un directorio dado.
    """
    html_files: List[str] = []
    if not os.path.exists(directory_path):
        logging.warning(f"El directorio '{directory_path}' no existe.")
        return html_files

    for filename in os.listdir(directory_path):
        if filename.endswith(".html"):
            html_files.append(os.path.join(directory_path, filename))

    return html_files


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extrae y limpia el título de un artículo.
    Busca etiqueta <title> o el primer <h1>. Limpia el sufijo " - Medium".
    """
    title_text = ""
    title_tag = soup.find("title")

    if title_tag and title_tag.string:
        title_text = title_tag.string
    else:
        h1_tag = soup.find("h1")
        if h1_tag:
            title_text = h1_tag.get_text()

    # Limpiar el sufijo
    if title_text.endswith(" - Medium"):
        title_text = title_text[:-9]

    # Limpieza básica de espacios
    return title_text.strip()


def sanitize_text(text: str) -> str:
    """
    Elimina espacios en blanco redundantes, tabulaciones y saltos de línea múltiples.
    """
    # Reemplazar múltiples espacios, tabulaciones y saltos de línea por un solo espacio
    cleaned_text = re.sub(r"\s+", " ", text)
    return cleaned_text.strip()


def parse_html(file_path: str) -> Optional[Dict[str, str]]:
    """
    Procesa un único archivo HTML y devuelve su representación estructurada.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, "lxml")

        # Eliminar explícitamente contenido no deseado
        for tag_name in ["script", "style", "nav", "footer"]:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        titulo = extract_title(soup)

        # Extraer cuerpo: contenido en etiquetas de contenido semántico
        target_tags = ["p", "h1", "h2", "h3", "blockquote", "li"]
        content_parts: List[str] = []

        # Iterar sobre las etiquetas semánticas para conservar el orden
        for tag in soup.find_all(target_tags):
            text = tag.get_text(separator=" ", strip=True)
            if text:
                content_parts.append(text)

        # Unir partes y sanitizar para texto plano limpio
        contenido_bruto = " ".join(content_parts)
        contenido_limpio = sanitize_text(contenido_bruto)

        id_archivo = os.path.basename(file_path)

        return {"id": id_archivo, "titulo": titulo, "contenido": contenido_limpio}

    except Exception as e:
        logging.warning(f"Error procesando el archivo '{file_path}': {e}")
        return None


def process_corpus(input_directory: str) -> List[Dict[str, str]]:
    """
    Orquesta la extracción iterando sobre la lista de archivos obtenidos.
    """
    files = read_files(input_directory)
    corpus: List[Dict[str, str]] = []

    for file_path in files:
        parsed_doc = parse_html(file_path)
        if parsed_doc is not None:
            corpus.append(parsed_doc)

    return corpus


def save_json(data: List[Dict[str, str]], output_path: str) -> None:
    """
    Guarda los datos procesados en un archivo JSON local.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error crítico al guardar el archivo JSON: {e}")


def main() -> None:
    input_directory = "./medium_export/posts/"
    output_path = "corpus_limpio.json"

    print(f"Iniciando extracción ETL desde: {input_directory}")

    corpus_data = process_corpus(input_directory)

    if corpus_data:
        save_json(corpus_data, output_path)
        print(
            f"Procesamiento completado. {len(corpus_data)} artículos guardados en '{output_path}'."
        )
    else:
        print("Finalizado. No se extrajo contenido válido. Evalúe alertas.")


if __name__ == "__main__":
    main()
