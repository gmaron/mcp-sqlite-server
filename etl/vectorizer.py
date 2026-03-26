"""
Document Chunking y Vectorización (RAG Data Pipeline - Paso 2)

Dependencias necesarias:
pip install langchain langchain-community sentence-transformers chromadb
"""

import os
import json
import shutil
import logging
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuración básica de logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def load_documents(json_path: str) -> List[Document]:
    """Carga el corpus desde un JSON y lo transforma a objetos Document de LangChain."""
    if not os.path.exists(json_path):
        logging.error(f"El archivo '{json_path}' no existe. Ejecute el paso 1 primero.")
        return []

    with open(json_path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    docs: List[Document] = []
    for item in data:
        # Extraer campos según la regla de negocio
        content = item.get("contenido", "")
        # Titulo e id van a metadata
        metadata = {"id": item.get("id", "N/A"), "titulo": item.get("titulo", "N/A")}
        docs.append(Document(page_content=content, metadata=metadata))

    return docs


def chunk_documents(docs: List[Document]) -> List[Document]:
    """Aplica estrategia de chunking semántico sobre los documentos usando RecursiveCharacterTextSplitter."""
    # Chunk Size 1000, Overlap 200 según especificación
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200, add_start_index=True
    )
    chunks = splitter.split_documents(docs)
    return chunks


def get_embeddings_model() -> HuggingFaceEmbeddings:
    """Inicializa y devuelve el modelo de Embeddings pre-entrenado local."""
    # Se recomienda all-MiniLM-L6-v2 para entorno local sin costo
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def create_vector_store(chunks: List[Document], persist_directory: str) -> Chroma:
    """Calcula embeddings e inserta los chunks en la base de datos Chroma local, garantizando idempotencia."""

    # Manejo de Idempotencia: limpiar directorio existente para evitar duplicidad si el script corre > 1 vez
    if os.path.exists(persist_directory):
        logging.info(
            f"Colección local detectada en '{persist_directory}'. Limpiando para no duplicar datos..."
        )
        try:
            shutil.rmtree(persist_directory)
        except Exception as e:
            logging.error(
                f"Fallo al intentar limpiar el directorio ChromaDb previo: {e}"
            )

    logging.info("Cargando modelo de embeddings de HuggingFace en memoria...")
    embeddings_model = get_embeddings_model()

    logging.info(
        f"Generando embeddings e insertando {len(chunks)} chunks en ChromaDB..."
    )

    # Crea el vector store e indexa al generar este llamado
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings_model,
        persist_directory=persist_directory,
    )

    logging.info("Vectores almacenados correctamente.")
    return vector_store


def main() -> None:
    input_file = "./output/corpus_limpio.json"
    persist_db_dir = "./chroma_db"

    print("\n--- RAG Pipeline Paso 2: Chunking y Vectorización ---")

    # 1. Carga de Datos
    docs = load_documents(input_file)
    if not docs:
        print("Finalizando: No hay datos procesados en la etapa origen.")
        return

    print(f"✅ Total de artículos procesados: {len(docs)}")

    # 2. Chunking
    chunks = chunk_documents(docs)
    print(f"✅ Total de chunks generados: {len(chunks)}")

    # 3. Modelado e Inserción Local
    create_vector_store(chunks, persist_db_dir)
    print(f"✅ Base de datos vectorial persistida en disco: {persist_db_dir}\n")


if __name__ == "__main__":
    main()
