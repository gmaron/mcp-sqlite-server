from abc import ABC, abstractmethod

class KnowledgeRepository(ABC):
    """Interfaz abstracta (Port) para el repositorio de Base de Conocimiento RAG."""
    
    @abstractmethod
    async def ask_question(self, query: str) -> str:
        """
        Consulta la base de conocimiento y retorna la respuesta procesada.
        
        Args:
            query (str): La pregunta o consulta a responder.
            
        Returns:
            str: Respuesta enriquecida basada en el conocimiento (incluyendo fuentes si aplica).
        """
