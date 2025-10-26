#!/bin/bash
# Script para executar o frontend Vue

cd "$(dirname "$0")"

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "❌ Dependências não instaladas!"
    echo "Execute: npm install"
    exit 1
fi

echo "🚀 Iniciando frontend Vue 3..."
echo "📍 URL: http://localhost:3000"
echo ""

# Executar servidor de desenvolvimento
npm run dev

