# 🤖 SHADOW : Asistente de Documentos Internos con IA (RAG)

## 📌 Descripción del Proyecto
**SHADOW** es un agente diseñado para la **Recuperación Aumentada por IA (RAG)** que permite consultar documentos internos de la empresa "SANTO PEGASUS SOLUCIONES" (manuales, guías, políticas) en lenguaje natural. 🤖 SHADOW procesa archivos PDF, genera embeddings semánticos y responde preguntas específicas citando las fuentes exactas.

**Características principales:**
- 📄 **Procesamiento de PDFs**: Carga y fragmentación inteligente de documentos
- 🔍 **Búsqueda semántica**: Recuperación de información por similitud vectorial (FAISS)
- 💬 **Chat interactivo**: Interfaz en Streamlit con historial de conversación
- 📊 **Fuentes citadas**: Cada respuesta incluye el documento y página exacta
- 🚀 **Rápido y eficiente**: Optimizado para minimizar consumo de tokens
- ☁️ **Desplegado en OCI**: Accesible desde cualquier lugar

---

## 🎥 Demo del Proyecto

[![Ver Demo de SHADOW en YouTube](https://img.youtube.com/vi/bszW5tQLYrM/0.jpg)](https://www.youtube.com/watch?v=bszW5tQLYrM)

*Haz clic en la imagen para ver la demostración del asistente en acción.*

> ![pregunta 1](/evidencias/image-1.png) ![pregunta 2](/evidencias/image-2.png) ![pregunta 3](/evidencias/image-3.png)
![pregunta 4](/evidencias/image-4.png) ![pregunta 5](/evidencias/image-5.png) ![pregunta 6](/evidencias/image-6.png)
![pregunta 7](/evidencias/image-7.png) ![Interfaz del Asistente](/evidencias/image.png)
---
## 🏗️ Arquitectura del Sistema

![Arquitectura del sistema :](/evidencias/arquitectura_del_sistema.png)

### Flujo de Procesamiento

1. **Ingesta**: Los PDFs se cargan con `PyMuPDFLoader`
2. **Fragmentación**: División en chunks de 1000 caracteres con `RecursiveCharacterTextSplitter`
3. **Vectorización**: Generación de embeddings con `intfloat/multilingual-e5-small`
4. **Almacenamiento**: Índice FAISS persistente en disco (`faiss_index_pdfs/`)
5. **Consulta**: El usuario pregunta → recuperación de chunks relevantes → LLM genera respuesta

---

## 🧠 Componentes Clave

| Componente | Tecnología | Función |
|:-----------|:-----------|:--------|
| **Frontend** | Streamlit | Interfaz de usuario interactiva |
| **Orquestación** | LangChain | Coordinación del flujo RAG |
| **LLM** | Groq (Llama 3.3 70B) | Generación de respuestas en español |
| **Embeddings** | multilingual-e5-small | Vectorización de texto multilingüe |
| **Vector Store** | FAISS | Búsqueda semántica eficiente |
| **Procesamiento PDF** | PyMuPDF | Extracción de texto de documentos |
| **Infraestructura** | OCI (Oracle Cloud) | Alojamiento y despliegue |

### Retriever Personalizado (Priorización)

El sistema implementa un `PriorityRetriever` que:
- **Prioriza automáticamente** la "Guía Oficial Back end.pdf" para consultas técnicas
- **Balancea** con otros documentos según la naturaleza de la pregunta
- **Garantiza** que las respuestas más relevantes aparezcan primero en el contexto

---

## ✅ Prerrequisitos

- **Python 3.10+** (recomendado 3.12)
- **Pip** (gestor de paquetes)
- **Cuenta en Groq** (para obtener API Key)
- **Git** (para clonar el repositorio)
- **Espacio en disco**: ~2 GB (para dependencias e índice FAISS)
- **Cuenta en OCI** (para despliegue en la nube - opcional)

---

## ⚙️ Instalación y Configuración Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Monkey-D-Roberto/CHALLENGE_ALURA.git

cd CHALLENGE_ALURA
```
### 2. Crear y activar entorno virtual
**Windows**
```bash
python -m venv venv

venv\Scripts\activate
```

**Mac/Linux**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto:
```bash
GROQ_API_KEY=tu_api_key_aqui
```
⚠️ Importante: No subas el archivo .env a GitHub (debe estar en .gitignore)

### 5. Estructurar documentos
Crea una carpeta documentos/ y coloca tus archivos PDF:

```bash
mkdir documentos
```
### 6. Generar el índice FAISS (primera ejecución)
```bash
python ingest_pdfs.py
```
Esto procesará todos los PDFs en documentos/ y creará el índice en faiss_index_pdfs/.

### 7. Ejecutar la aplicación localmente
```bash
streamlit run app_streamlit.py
```
La aplicación estará disponible en http://localhost:8501

## ☁️ Despliegue en OCI (Oracle Cloud Infrastructure)
**Resumen del Proceso de Despliegue**
El proyecto fue desplegado en una instancia VM.Standard.E2.1.Micro (1 GB de RAM) con Oracle Linux 9. Los pasos clave fueron:
Configuración de SWAP: Se creó un archivo de swap de 4 GB para manejar las limitaciones de memoria.
Instalación de Python 3.12 y configuración del entorno virtual.
Clonación del repositorio desde GitHub.
Instalación de dependencias y actualización de imports obsoletos de LangChain.
Generación del índice FAISS (proceso que tomó ~10-20 minutos).
Configuración del servicio systemd para que la aplicación se inicie automáticamente.
Apertura del puerto 8501 en la Security List de OCI.
Deshabilitación de firewalld para permitir el tráfico externo.

### 🌐 Aplicación en Producción

La aplicación está desplegada en Oracle Cloud Infrastructure (OCI) y es accesible en:

🔗 **URL**: [http://147.15.123.91:8501]

### Comandos Útiles para el Despliegue
```bash
# Conectar a la instancia
ssh -i ~/.ssh/tu_clave opc@<IP_PUBLICA>

# Activar entorno virtual
cd /opt/agente/CHALLENGE_ALURA
source venv/bin/activate

# Generar índice FAISS (si es necesario)
python ingest_pdfs.py

# Reiniciar el servicio
sudo systemctl restart streamlit

# Ver estado del servicio
sudo systemctl status streamlit

# Ver logs en tiempo real
sudo journalctl -u streamlit -f
```
## 📚 Ejemplos de Preguntas y Respuestas
1. **¿Ques es Onboarding?**
2. **¿Que es arquitectura de Microservicios?**
3. **En la guia oficial back end , que nos menciona del termino microservicios?**
4. **¿Que me puedes mencionar sobre la pólitica de On-Call y pagerduty?**
5. **Que es el error Budget?**

## 🗂️ Estructura del Proyecto

![Estructura del proyecto: ](/evidencias/estructura_del_proyecto.png)

## ⚠️ Limitaciones y Consideraciones Técnicas
Este proyecto fue desplegado en una instancia de OCI con **Shape VM.Standard.E2.1.Micro** (1 GB de RAM), lo que impone ciertas restricciones:

### 1. Memoria y Rendimiento
Uso de Swap: Para cargar los modelos de embeddings (intfloat/multilingual-e5-small), fue obligatorio configurar un swap de 4 GB. Sin este, la aplicación no podría ejecutarse.

Tiempo de Carga Inicial: La primera carga de la aplicación en el navegador puede ser lenta (30 segundos - 2 minutos) porque el sistema necesita cargar el modelo de embeddings desde el disco (swap) a la memoria.

Tiempo de Ingesta: La generación del índice FAISS (python ingest_pdfs.py) es intensiva en memoria y puede tomar entre 10 y 20 minutos.

### 2. Limitaciones de la Arquitectura
Escalabilidad: Esta configuración es ideal para pruebas, demostraciones o uso con un equipo pequeño. No está diseñada para soportar múltiples usuarios concurrentes o documentos de gran tamaño.

Modelos de Embeddings: Se utiliza intfloat/multilingual-e5-small, que es un equilibrio entre rendimiento y tamaño. Para mejor rendimiento semántico, se podría usar un modelo más grande (requeriría más memoria).

Almacenamiento: El índice FAISS y los documentos se almacenan en el disco de la instancia.

### 3. Pasos a Futuro para una Versión de Producción
**Si el proyecto crece, se recomienda:**

Migrar a una instancia con más RAM (ej. VM.Standard.A1.Flex con 4 OCPU y 24 GB RAM).
Implementar un Load Balancer para gestionar el tráfico.
Utilizar Object Storage para almacenar PDFs e índices de forma persistente.
Migrar los embeddings a un servicio como OCI Gen AI Agents para una integración más nativa y escalable.

## 🛠️ Troubleshooting
### Error: "No se encontró GROQ_API_KEY"
Verifica que el archivo .env existe en la raíz
Revisa que la variable se llame exactamente GROQ_API_KEY

### Error: "El índice 'faiss_index_pdfs' no existe"
Ejecuta primero python ingest_pdfs.py
Verifica que la carpeta documentos/ contiene archivos PDF

### Error: "Rate limit excedido" (429)
El sistema está optimizado para una sola iteración por consulta
Si ocurre, espera 60 segundos y reintenta

### Error: "ModuleNotFoundError: No module named 'langchain.text_splitter'"
 
 ```bash
 # Cambiar:
from langchain.text_splitter import RecursiveCharacterTextSplitter
 # Por:
from langchain_text_splitters import RecursiveCharacterTextSplitter
```
Instala el paquete:
```bash
 pip install langchain-text-splitters
```

## 📝 Mejoras Futuras
- **Soporte para más formatos (Word, Excel, HTML)**
- **Sistema de feedback de respuestas**
- **Autenticación de usuarios**
- **Exportar conversaciones**
- **Dashboard de estadísticas de uso**
- **Búsqueda por metadatos (autor, fecha, categoría)**

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo LICENSE para más detalles.

## 👥 Autor
- **Roberto Carlos**
- **Proyecto desarrollado como parte del Challenge AluraLatam - Programa Oracle Next Education (ONE).**

![GitHub:] (https://github.com/Monkey-D-Roberto/CHALLENGE_ALURA)

![LinkedIn:] (https://www.linkedin.com/in/roberto-borja-04991834a/)

## 🙏 Agradecimientos
- **Alura Latam** : Por el desafío y la inspiración
- **Groq** : Por proporcionar el modelo LLM de alto rendimiento
- **LangChain** : Por la excelente framework de orquestación
- **Streamlit** : Por hacer la creación de interfaces tan sencilla
- **Oracle Cloud Infrastructure** : Por la plataforma de despliegue

## 📊 Estado del Proyecto
- ✅ Fase 1 (Ingesta y RAG) : Completada
- ✅ Fase 2 (Repositorio y Documentación) : Completada
- ✅ Fase 3 (Deploy en OCI) : Completada

⭐ Si te gusta este proyecto, no olvides darle una estrella en GitHub!
