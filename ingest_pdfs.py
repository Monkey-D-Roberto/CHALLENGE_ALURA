import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# CONFIGURACIÓN DE EMBEDDINGS
local_embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)
print("✅ Embeddings multilingües cargados.")

# CARGA DE PDFs
all_docs = []
pdf_files = [f for f in os.listdir("./documentos") if f.endswith(".pdf")]

if not pdf_files:
    raise FileNotFoundError(
        "❌ No se encontraron archivos PDF en la carpeta './documentos'"
    )


for file in pdf_files:
    loader = PyMuPDFLoader(os.path.join("./documentos", file))
    docs = loader.load()
    for doc in docs:
        doc.metadata["source"] = file

        if "page" in doc.metadata and isinstance(doc.metadata["page"], int):
            doc.metadata["page"] = doc.metadata["page"] + 1
    all_docs.extend(docs)

# FRAGMENTACIÓN CON MI RECURSIVE
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, chunk_overlap=200, separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(all_docs)

# crea indice faiss a partir de lso frag y embeddings
vectorstore = FAISS.from_documents(chunks, local_embeddings)
vectorstore.save_local("faiss_index_pdfs")
print("✅ Índice guardado.")
