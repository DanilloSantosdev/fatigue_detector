#!/bin/bash
# Sistema de Detecção de Fadiga - MVP
# Otimizado para Raspberry Pi com câmera CSI

echo "🚗 Sistema de Detecção de Fadiga - MVP"
echo "======================================"
echo "📱 Iniciando sistema..."
echo ""

# Ativar ambiente virtual
source .venv/bin/activate

# Executar o detector
python3 detector.py

echo ""
echo "✅ Sistema encerrado."

