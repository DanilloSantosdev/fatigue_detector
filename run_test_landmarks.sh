#!/bin/bash
# Script para executar o teste de landmarks com supressão de avisos

echo "============================================================"
echo "Iniciando Teste de Landmarks..."
echo "============================================================"

# Ativar ambiente virtual
source .v/bin/activate

# Executar o teste
python3 test_landmarks.py

echo ""
echo "Teste encerrado."

