import streamlit as st
import os
import time
from consulta_agent import responder, reindex_pdfs, get_qa_chain
import base64

st.set_page_config(
    page_title="Asistente de Documentos Internos | AI RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ==============================================================
# CONFIGURACION PARA DEPLOY EN OCI

#  Directorio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Config rutas
PDF_FOLDER = os.path.join(BASE_DIR, "documentos")
INDEX_PATH = os.path.join(BASE_DIR, "faiss_index_pdfs")
ENV_PATH = os.path.join(BASE_DIR, ".env")

os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)

# Configuración de memoria (para la shape Micro del oci)
# Limitamos el uso de memoria de pyTorch (embeddings)
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
os.environ["OMP_NUM_THREADS"] = "1"

# ====================================================================


# Cargamos el CSS
def load_css(file_name):
    """Carga un archivo CSS desde la carpeta styles/"""
    css_path = os.path.join("styles", file_name)
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


main_css = load_css("main.css")
header_css = load_css("header.css")

# Inyectamos CSS
st.markdown(
    f"""
    <style>
        /* Estilos generales */
        {main_css}
        
        /* Estilos especificos del header */
        {header_css}
    </style>
    """,
    unsafe_allow_html=True,
)

#  INICIALIZAR ESTADO DE SESIÓN

if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_ready" not in st.session_state:
    try:
        get_qa_chain()
        st.session_state.qa_ready = True
    except Exception as e:
        st.session_state.qa_ready = False
        st.session_state.qa_error = str(e)

#  HEADER
logo_path = "image/logo.png"
logo_exists = os.path.exists(logo_path)


if logo_exists:

    with open(logo_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <div class="header-logo-container">
            <div class="logo-wrapper">
                <img src="data:image/png;base64,{img_base64}" 
                     alt="Logo de la empresa">
            </div>
            <h1>🤖 Asistente de Documentos Internos</h1>
            <h1 style="font-size: 1.5rem; margin-top: -0.3rem;">Santo Pegasus Soluciones</h1>
            
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <div class="header-simple-container">
            <div class="header-icon">🤖</div>
            <h1>Asistente de Documentos Internos</h1>
            <p>💡 Consulta en lenguaje natural tus manuales, guías y políticas empresariales</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


logo_chat_path = "image/logochat.png"
logo_chat_exists = os.path.exists(logo_chat_path)

col_chat_logo, col_chat_title = st.columns([1, 20])
with col_chat_logo:
    if logo_chat_exists:
        st.image(logo_chat_path, width=35)
    else:
        st.markdown("💬")
with col_chat_title:
    st.markdown(
        "### 💬 Consulta sobre: Arquitectura de Microservicios, Back end, Front-end, Onboarding, Protocolo de respuestas a incidentes."
    )


#  BARRA LATERAL
with st.sidebar:

    st.markdown("### 📁 Gestión de Documentos")

    if st.session_state.qa_ready:
        st.markdown(
            '<span class="status-badge success">✅ Sistema listo</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge error">⚠️ Sistema no listo</span>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("#### 📄 Documentos Cargados")
    pdf_folder = "documentos"
    if os.path.exists(pdf_folder):
        pdfs = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
        if pdfs:
            for pdf in pdfs:
                st.markdown(
                    f"""
                <div class="pdf-item">
                    <span class="pdf-icon">📄</span>
                    <span class="pdf-name">{pdf}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            st.caption(f"📊 Total: {len(pdfs)} documentos")
        else:
            st.warning("⚠️ No hay PDFs en la carpeta 'documentos'.")
    else:
        st.error("❌ La carpeta 'documentos' no existe.")

    st.divider()

    # Subir nuevos PDFs
    st.markdown("#### ⬆️ Subir Documentos")
    uploaded_files = st.file_uploader(
        "Arrastra o selecciona archivos PDF",
        type="pdf",
        accept_multiple_files=True,
        key="pdf_uploader",
        help="Soporta archivos PDF de hasta 200MB",
    )

    if uploaded_files:
        if not os.path.exists(pdf_folder):
            os.makedirs(pdf_folder)

        # Guardar archivos
        for uploaded_file in uploaded_files:
            file_path = os.path.join(pdf_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

        st.success(f"✅ {len(uploaded_files)} archivo(s) guardado(s)")

        # Botón de reindexación
        if st.button(
            "🔄 Reindexar Documentos",
            use_container_width=True,
            type="primary",
            help="Procesa los nuevos documentos para hacerlos consultables",
        ):
            with st.spinner(
                "🔄 Procesando documentos... Esto puede tomar varios segundos."
            ):
                try:
                    resultado = reindex_pdfs(pdf_folder="documentos")
                    if resultado:
                        st.session_state.qa_ready = True
                        st.session_state.messages = []
                        st.success("✅ ¡Documentos procesados exitosamente!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Error en el procesamiento")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.session_state.qa_ready = False

    st.divider()

    with st.expander("ℹ️ Acerca del Asistente", expanded=False):
        st.markdown("""
        **Tecnologías:**
        - 🧠 **Modelo:** Llama 3.3 70B (Groq)
        - 📚 **RAG:** LangChain + FAISS
        - 🌐 **Embeddings:** multilingual-e5-small
        
        **Características:**
        - ✅ Consultas en lenguaje natural
        - 📎 Soporte para múltiples PDFs
        - 🔍 Búsqueda semántica avanzada
        - 📊 Fuentes citadas en cada respuesta
        """)

    st.divider()
    st.markdown("#### 📊 Estadísticas")
    if os.path.exists(pdf_folder):
        total_pdfs = len([f for f in os.listdir(pdf_folder) if f.endswith(".pdf")])
        total_msgs = len(st.session_state.messages)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📄 Documentos", total_pdfs)
        with col2:
            st.metric("💬 Consultas", total_msgs // 2)


#  historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


if prompt := st.chat_input("💬 Escribe tu pregunta aquí..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Obtener respuesta
    with st.chat_message("assistant"):
        if not st.session_state.qa_ready:
            st.error(
                "⚠️ El asistente no está listo. Por favor, reindexa los documentos."
            )
        else:
            try:
                with st.spinner("🔍 Buscando en los documentos..."):
                    start = time.time()
                    respuesta, fuentes = responder(prompt)
                    elapsed = time.time() - start

                # respuesta con formato nuevoo
                full_response = (
                    f"{respuesta}\n\n---\n**📚 Fuentes consultadas:**\n{fuentes}"
                )
                st.markdown(full_response)
                st.caption(f"⏱️ Tiempo de respuesta: {elapsed:.2f} segundos")

                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response}
                )
            except Exception as e:
                st.error(f"❌ Ocurrió un error: {e}")


# FOOTER

st.markdown(
    """
<div class="footer">
    <p>🔒 Las consultas se procesan localmente. No se almacenan datos sensibles.</p>
    <p style="font-size: 0.8rem; opacity: 0.7;">
        Desarrollado usando LangChain, Groq y Streamlit | Gracias a @Alura Latam
    </p>
</div>
""",
    unsafe_allow_html=True,
)
