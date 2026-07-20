import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import List

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("❌ No se encontró GROQ_API_KEY en el archivo .env")

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    max_tokens=1024,
    api_key=GROQ_API_KEY,
)

# PROMPT

custom_prompt_template = """
Eres un asistente de IA especializado en responder preguntas sobre documentación interna de la empresa.

INSTRUCCIONES IMPORTANTES:
1. Analiza el CONTEXTO proporcionado y responde ÚNICAMENTE basándote en él.
2. Si encuentras información relevante en la "Guía Oficial Back end.pdf", utilízala con prioridad.
3. PERO si la pregunta es específica sobre front-end, NO IGNORES la "Guía Oficial de Ingeniería Front-end.pdf" - utilízala sin restricciones.
4. Si la pregunta contiene sinónimos o expresiones similares al texto original, debes interpretarlas correctamente (ej. "cómo se aplica" = "aplicación de", "en el front-end" = "al front-end").
5. Si NO encuentras información en NINGÚN documento del contexto, responde: "Lo siento, no encontré esa información en los documentos proporcionados."
6. NO uses tus conocimientos previos ni inventes datos.

REGLAS DE PRIORIDAD:
- Para preguntas de BACK-END: prioriza "Guía Oficial Back end.pdf"
- Para preguntas de FRONT-END: prioriza "Guía Oficial de Ingeniería Front-end.pdf"
- Para preguntas GENERALES: usa la información más completa de cualquier documento

CONTEXTO (fragmentos de documentos):
{context}

PREGUNTA DEL USUARIO:
{question}

RESPUESTA (basada exclusivamente en el contexto, sin inventar información):
"""

PROMPT = PromptTemplate(
    template=custom_prompt_template, input_variables=["context", "question"]
)


# 4. RETRIEVER PERSONALIZADO
class PriorityRetriever(BaseRetriever):
    base_retriever: BaseRetriever
    k_final: int = 5

    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        initial_docs = self.base_retriever.invoke(query, **kwargs)
        priority_docs = [
            doc
            for doc in initial_docs
            if "Guía Oficial Back end.pdf" in doc.metadata.get("source", "")
        ]
        other_docs = [
            doc
            for doc in initial_docs
            if "Guía Oficial Back end.pdf" not in doc.metadata.get("source", "")
        ]
        return (priority_docs + other_docs)[: self.k_final]

    async def _aget_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        return self._get_relevant_documents(query, **kwargs)


# 5. VARIABLE GLOBAL Y FUNCIONES DE CONSTRUCCION
_qa_chain = None


def build_qa_chain(index_path="faiss_index_pdfs"):
    """Construye la cadena RAG a partir del índice FAISS guardado."""
    global _qa_chain

    # Verificar que el índice existe
    if not os.path.exists(index_path):
        raise FileNotFoundError(
            f"❌ El índice '{index_path}' no existe. Ejecuta primero ingest_pdfs.py"
        )

    vectorstore = FAISS.load_local(
        index_path, embeddings, allow_dangerous_deserialization=True
    )
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    priority_retriever = PriorityRetriever(base_retriever=base_retriever, k_final=5)
    _qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=priority_retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT},
    )
    return _qa_chain


def get_qa_chain():
    global _qa_chain
    if _qa_chain is None:
        _qa_chain = build_qa_chain()
    return _qa_chain


#  FUNCIÓN DE REINDEXACIÓN


def reindex_pdfs(pdf_folder="documentos", index_path="faiss_index_pdfs"):
    """
    Vuelve a generar el índice FAISS a partir de los PDFs en pdf_folder
    y luego recarga la cadena RAG.
    """
    global _qa_chain

    if not os.path.exists(pdf_folder):
        raise FileNotFoundError(f"❌ La carpeta '{pdf_folder}' no existe.")

    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError(f"❌ No se encontraron PDFs en '{pdf_folder}'.")

    print("🔄 Cargando PDFs...")
    all_docs = []
    for file in pdf_files:
        loader = PyMuPDFLoader(os.path.join(pdf_folder, file))
        docs = loader.load()
        for doc in docs:
            doc.metadata["source"] = file
            if "page" in doc.metadata and isinstance(doc.metadata["page"], int):
                doc.metadata["page"] = doc.metadata["page"] + 1
        all_docs.extend(docs)
    print(f"✅ {len(all_docs)} páginas cargadas.")

    print("🧩 Fragmentando documentos...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(all_docs)
    print(f"✅ {len(chunks)} fragmentos generados.")

    print("💾 Generando nuevo índice FAISS...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(index_path)
    print("✅ Índice guardado.")

    # Recarga nuevo índice
    _qa_chain = build_qa_chain(index_path)
    print("✅ Cadena RAG recargada con éxito.")
    return True


# FUNCIONES DE CONSULTA
def responder(query):
    try:
        qa = get_qa_chain()
        resultado = qa.invoke({"query": query})
        respuesta = resultado["result"]
        fuentes = []
        for doc in resultado["source_documents"]:
            source = doc.metadata.get("source", "PDF desconocido")
            page = doc.metadata.get("page", "N/A")
            fuentes.append(f"- {source} (Pág. {page})")
        return respuesta, (
            "\n".join(fuentes)
            if fuentes
            else "📭 No se encontraron fuentes específicas."
        )
    except Exception as e:
        return f"❌ Error al procesar la consulta: {str(e)}", ""


# FUNCIÓN PARA PROBAR EN CONSOLA


def preguntar(query):
    resp, fuentes = responder(query)
    print("\n" + "=" * 50)
    print(f"🤖 RESPUESTA:\n{resp}")
    print("=" * 50)
    print("\n📚 FUENTES:")
    print(fuentes)
    print("=" * 50)


if __name__ == "__main__":
    print(
        "✅ Módulo pregunta agente cargado. Usa preguntar('tu pregunta') para probar."
    )
