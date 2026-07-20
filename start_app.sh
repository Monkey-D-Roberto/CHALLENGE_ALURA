#!/bin/bash
# Script de inicio para Streamlit

cd /opt/agente/CHALLENGE_ALURA
export GROQ_API_KEY=$(grep GROQ_API_KEY .env | cut -d '=' -f2)
export PYTHONPATH=/opt/agente/CHALLENGE_ALURA

source venv/bin/activate

streamlit run app_streamlit.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --logger.level info