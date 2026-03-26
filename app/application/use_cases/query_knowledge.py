from app.domain.interfaces.knowledge_repository import KnowledgeRepository

class QueryKnowledgeUseCase:
    """
    Caso de Uso: Consultar la base de conocimientos RAG del autor.
    Delega de forma limpia la integración del LLM/Buscador a su Repositorio Inyectado.
    """
    def __init__(self, repository: KnowledgeRepository):
        self._repository = repository

    async def execute(self, query: str) -> str:
        """
        Ejecuta la orquestación para responder una pregunta en base al Knowledge Base.
        """
        if not query or len(query.strip()) == 0:
            return "El parámetro 'query' no puede estar vacío."
            
        return await self._repository.ask_question(query)
