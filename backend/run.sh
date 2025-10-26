#!/bin/bash
# Script para executar o backend FastAPI

cd "$(dirname "$0")"

# Verificar se venv existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "Execute: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Ativar ambiente virtual
source venv/bin/activate

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando a partir do .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Arquivo .env criado. Por favor, configure as variáveis necessárias."
    else
        echo "❌ .env.example não encontrado!"
        exit 1
    fi
fi

echo "🚀 Iniciando backend FastAPI..."
echo "📍 URL: http://0.0.0.0:8000"
echo "📚 Docs: http://0.0.0.0:8000/docs"
echo ""

# Executar servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

