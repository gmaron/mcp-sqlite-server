import logging
from app.domain.interfaces.knowledge_repository import KnowledgeRepository

# Langchain LCEL Core
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Langchain Integrations (Infrastructure dependencies)
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI


class RAGLangchainAdapter(KnowledgeRepository):
    """
    Adapter que implementa el KnowledgeRepository. 
    Contiene la lógica de inicialización y ejecución de la pipeline de LangChain con Gemini y ChromaDB local.
    """
    def __init__(self, db_path: str = "./etl/chroma_db"):
        self.db_path = db_path
        self._initialize_pipeline()
        
    def _initialize_pipeline(self):
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            vector_store = Chroma(
                persist_directory=self.db_path, 
                embedding_function=embeddings
            )
            # El top k=3 según el specification
            self.retriever = vector_store.as_retriever(search_kwargs={"k": 3})
            
            # El motor Generativo
            import os
            gemini_model = os.getenv("GEMINI_API_MODEL", "gemini-2.5-flash")
            self.llm = ChatGoogleGenerativeAI(
                model=gemini_model, 
                temperature=0.2
            )
            
            # Mantenemos el custom Prompt del spec.
            system_prompt = (
                "Eres un asistente técnico y estratégico basado en los escritos y conocimientos del autor. "
                "Utiliza ÚNICAMENTE los siguientes fragmentos de contexto recuperados para responder a la pregunta. "
                "Si no sabes la respuesta o el contexto no contiene la información, di explícitamente "
                "'No tengo información sobre eso en mi base de conocimiento'. No inventes información.\n\n"
                "Contexto: {context}"
            )
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "Pregunta: {input}")
            ])
            logging.info("RAG LangChain Adapter inicializado exitosamente.")
        except Exception as e:
            logging.error("Error crítico al inicializar el pipeline RAG Langchain: %s", e)
            raise e

    async def ask_question(self, query: str) -> str:
        # Format inline method para LCEL mapping
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        # Generación final Langchain Expression Language
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

        rag_chain = RunnablePassthrough.assign(
            context=(lambda x: self.retriever.invoke(x["input"]))
        ).assign(answer=rag_chain_from_docs)

        try:
            # Reemplazamos invoke por ainvoke para no bloquear el Event Loop local
            response = await rag_chain.ainvoke({"input": query})
            
            answer = response.get("answer", "No se pudo generar respuesta.")
            
            # Cosechando los Unique Titles
            source_docs = response.get("context", [])
            sources = set(doc.metadata.get("titulo", "N/A") for doc in source_docs)
            
            sources_text = "\n\n**Fuentes utilizadas:**\n" + "\n".join(f"- {s}" for s in sources) if sources else ""
            return str(answer) + sources_text
            
        except Exception as e:
            logging.error("Error ejecutando consulta RAG LCEL: %s", e)
            return f"Hubo un error al consultar la base de conocimiento: {str(e)}"
