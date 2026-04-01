import logging
import os
from typing import Optional
from fastmcp import FastMCP
from app.application.use_cases.query_knowledge import QueryKnowledgeUseCase
from app.infrastructure.adapters.rag_langchain_adapter import RAGLangchainAdapter

# Construcción de dependencias (DI/Setup)
query_use_case: Optional[QueryKnowledgeUseCase] = None
try:
    db_path = os.getenv("CHROMA_DB_PATH", "./etl/chroma_db")
    rag_adapter = RAGLangchainAdapter(db_path=db_path)
    query_use_case = QueryKnowledgeUseCase(repository=rag_adapter)
except Exception as e:
    logging.error("Failed to load RAG Adapter. Is GEMINI_API_KEY set?: %s", e)

# Sub-servidor local de FastMCP
knowledge = FastMCP("KnowledgeBase")

@knowledge.tool()
async def consultar_base_conocimiento_autor(query: str) -> str:
    """
    Utiliza esta herramienta para consultar los artículos, newsletters y el conocimiento 
    personal del autor (Gastón) sobre liderazgo, tecnología, arquitectura cloud, 
    reflexiones personales y management. 
    NO uses tu conocimiento general; usa los resultados de esta herramienta.
    """
    if query_use_case is None:
        return "El subsistema RAG no se pudo inicializar en el servidor. Revise los logs (ej: GEMINI_API_KEY faltante)."
        
    try:
        resultado = await query_use_case.execute(query)
        return resultado
    except Exception as e:
        return f"Error interno en la capa de conocimiento: {str(e)}"
