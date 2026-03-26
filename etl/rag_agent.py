"""
RAG Orchestrator con Gemini API (RAG Data Pipeline - Paso 3)

Dependencias necesarias:
pip install langchain langchain-community langchain-chroma langchain-google-genai sentence-transformers python-dotenv
"""

import os
import sys
from dotenv import load_dotenv

# LangChain - Core & Chains
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# LangChain - Integrations
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI


def setup_environment() -> None:
    """Valida la carga de variables de entorno críticas."""
    load_dotenv()
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ Error: Variable 'GEMINI_API_KEY' no encontrada.")
        print("Por favor, agregue su clave de Google Gemini al archivo .env.")
        sys.exit(1)


def initialize_rag_pipeline():
    """Construye y devuelve la cadena RAG vinculando Retriever + Generador."""

    print("Iniciando modelo de Embeddings local (all-MiniLM-L6-v2)...")
    embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    persist_db_dir = "./chroma_db"
    if not os.path.exists(persist_db_dir):
        print(f"❌ Error: La base de datos local no existe en '{persist_db_dir}'.")
        print(
            "Asegúrate de haber ejecutado el pipeline de vectorización (Paso 2) previamente."
        )
        sys.exit(1)

    print("Conectando con ChromaDB local...")
    # Inicializa el vector store
    vector_store = Chroma(
        persist_directory=persist_db_dir, embedding_function=embeddings_model
    )

    # Retriever para Top-3 documentos más similares
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    print("Inicializando modelo de chat Gemini (gemini-2.5-flash)...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,  # Baja temperatura para evitar alucinaciones
    )

    # System Message estricto según requerimientos
    system_prompt = (
        "Eres un asistente técnico y estratégico basado en los escritos y conocimientos del autor. "
        "Utiliza ÚNICAMENTE los siguientes fragmentos de contexto recuperados para responder a la pregunta. "
        "Si no sabes la respuesta o el contexto no contiene la información, di explícitamente "
        "'No tengo información sobre eso en mi base de conocimiento'. No inventes información.\n\n"
        "Contexto: {context}"
    )

    prompt = ChatPromptTemplate.from_messages(
        [("system", system_prompt), ("human", "Pregunta: {input}")]
    )

    # Helper format para LangChain Expression Language (LCEL)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Ensamblaje de la cadena RAG final en LCEL nativo puro
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain = RunnablePassthrough.assign(
        context=(lambda x: retriever.invoke(x["input"]))
    ).assign(
        answer=rag_chain_from_docs
    )

    return rag_chain


def run_interactive_agent(rag_chain) -> None:
    """Ejecuta un entorno CLI interactivo para responder consultas."""
    print("\n" + "=" * 80)
    print("🤖 Agente RAG Inicializado. Basado en corpus local de artículos.")
    print("   Modo interactivo activo. Escriba 'salir' para terminar.")
    print("=" * 80 + "\n")

    while True:
        try:
            query = input("\n👤 Pregunta: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo del asistente...")
            break

        if query.lower() in ["salir", "exit", "quit"]:
            print("Finalizando sesión del agente... ¡Hasta pronto!")
            break

        if not query:
            continue

        print("⏳ Buscando contexto relevante e invocando a Gemini...\n")

        try:
            # Ejecución del orquestador (Llamada RAG)
            response = rag_chain.invoke({"input": query})

            # Formateo de las salidas de texto principal
            answer = response.get("answer", "No se generó respuesta.")
            print(f"🤖 Respuesta de Gemini:\n{answer}\n")

            # Extracción y despliegue de fuentes
            source_docs = response.get("context", [])
            print("📚 Fuentes utilizadas:")
            if source_docs:
                # set() previene duplicidad si dos chunks provienen del mismo título
                titulos_fuentes = set()
                for idx, doc in enumerate(source_docs, start=1):
                    titulo = doc.metadata.get("titulo", f"Documento_{idx}")
                    titulos_fuentes.add(titulo)
                for titulo in titulos_fuentes:
                    print(f"  - {titulo}")
            else:
                print("  - Ninguna fuente en la BBDD coincidió semánticamente.")

        except Exception as e:
            print(f"❌ Error durante la generación RAG: {e}")


def main() -> None:
    setup_environment()
    rag_orchestrator = initialize_rag_pipeline()
    run_interactive_agent(rag_orchestrator)


if __name__ == "__main__":
    main()
