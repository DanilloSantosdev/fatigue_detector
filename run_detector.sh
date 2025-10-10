#!/bin/bash
# Script para executar o detector de fadiga com supressão de avisos

echo "============================================================"
echo "Iniciando Detector de Fadiga..."
echo "============================================================"

# Ativar ambiente virtual
source .v/bin/activate

# Executar o detector
python3 detector.py

echo ""
echo "Detector encerrado."

