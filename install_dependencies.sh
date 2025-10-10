#!/bin/bash
# Script de instalação de dependências do Detector de Fadiga

echo "============================================================"
echo "Instalacao de Dependencias - Detector de Fadiga"
echo "============================================================"
echo ""

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "[ERRO] Arquivo requirements.txt nao encontrado!"
    echo "Execute este script no diretorio testCam"
    exit 1
fi

# Verificar se o ambiente virtual existe
if [ ! -d ".v" ]; then
    echo "[INFO] Criando ambiente virtual..."
    python3 -m venv .v
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao criar ambiente virtual!"
        exit 1
    fi
    echo "[OK] Ambiente virtual criado com sucesso!"
    echo ""
fi

# Ativar ambiente virtual
echo "[INFO] Ativando ambiente virtual..."
source .v/bin/activate

# Atualizar pip
echo ""
echo "[INFO] Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo ""
echo "[INFO] Instalando dependencias do requirements.txt..."
pip install -r requirements.txt

# Verificar instalação
echo ""
echo "============================================================"
echo "Verificando instalacao..."
echo "============================================================"

python3 << 'EOF'
import sys

packages = {
    'cv2': 'opencv-python',
    'mediapipe': 'mediapipe',
    'numpy': 'numpy',
    'scipy': 'scipy'
}

all_ok = True
for module, package in packages.items():
    try:
        __import__(module)
        print(f"[OK] {package:20s} - instalado")
    except ImportError:
        print(f"[ERRO] {package:20s} - NAO instalado")
        all_ok = False

if all_ok:
    print("\n[OK] Todas as dependencias foram instaladas com sucesso!")
    sys.exit(0)
else:
    print("\n[ERRO] Algumas dependencias falharam. Tente instalar manualmente.")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "Instalacao concluida com sucesso!"
    echo "============================================================"
    echo ""
    echo "Para executar o detector:"
    echo "  ./run_detector.sh"
    echo ""
    echo "Para testar landmarks:"
    echo "  ./run_test_landmarks.sh"
    echo ""
else
    echo ""
    echo "[ERRO] Houve problemas na instalacao."
    echo "Tente instalar manualmente com: pip install -r requirements.txt"
fi

