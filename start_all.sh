#!/bin/bash
# Script para iniciar backend e frontend simultaneamente

cd "$(dirname "$0")"

echo "🚀 Iniciando Sistema de Detecção de Fadiga..."
echo ""

# Função para cleanup ao sair
cleanup() {
    echo ""
    echo "🛑 Encerrando processos..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Iniciar backend
echo "📡 Iniciando backend..."
cd backend
./run.sh &
BACKEND_PID=$!
cd ..

# Aguardar backend iniciar
sleep 5

# Iniciar frontend
echo "🎨 Iniciando frontend..."
cd frontend
./run.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Sistema iniciado com sucesso!"
echo "📡 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Pressione Ctrl+C para encerrar"
echo ""

# Aguardar processos
wait $BACKEND_PID $FRONTEND_PID

