#!/bin/bash
# Script otimizado para instalar frontend no Raspberry Pi

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}→${NC} $1"; }

cd "$(dirname "$0")"

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       Instalação do Frontend - Otimizado para RPi         ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Verificar Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js não encontrado!"
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION"

# Verificar se já está instalado
if [ -d "node_modules" ]; then
    echo ""
    print_info "node_modules já existe!"
    read -p "Deseja reinstalar? Isso apagará e reinstalará tudo (s/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        print_info "Removendo node_modules..."
        rm -rf node_modules package-lock.json
        print_success "Removido"
    else
        print_info "Mantendo instalação existente"
        exit 0
    fi
fi

echo ""
echo "Escolha o método de instalação:"
echo ""
echo "1) Rápido - Sem cache, sem audit (RECOMENDADO para Raspberry Pi)"
echo "2) Completo - Instalação normal (LENTO no RPi, pode travar)"
echo "3) Cancelar"
echo ""
read -p "Opção (1/2/3): " -n 1 -r
echo ""

case $REPLY in
    1)
        print_info "Instalação rápida selecionada"
        echo ""
        print_info "Iniciando instalação..."
        echo "⚠️  Tempo estimado: 10-20 minutos"
        echo "⚠️  Você verá o progresso abaixo"
        echo ""
        
        # Configurar npm para ser mais rápido
        npm config set audit false
        npm config set fund false
        npm config set update-notifier false
        
        # Instalar com flags otimizadas
        npm install --no-audit --no-fund --prefer-offline --loglevel=info
        
        if [ $? -eq 0 ]; then
            echo ""
            print_success "✨ Frontend instalado com sucesso!"
            echo ""
            print_info "Para executar:"
            echo "   ${YELLOW}npm run dev${NC}"
            echo ""
        else
            print_error "Erro na instalação"
            exit 1
        fi
        ;;
    
    2)
        print_info "Instalação completa selecionada"
        echo ""
        print_info "⚠️  ATENÇÃO: Pode demorar 30-60 minutos e usar muita memória!"
        echo ""
        read -p "Tem certeza? (s/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Ss]$ ]]; then
            print_info "Instalando..."
            npm install --loglevel=info
            
            if [ $? -eq 0 ]; then
                print_success "Frontend instalado!"
            else
                print_error "Erro na instalação"
                exit 1
            fi
        else
            print_info "Cancelado"
            exit 0
        fi
        ;;
    
    3|*)
        print_info "Cancelado"
        exit 0
        ;;
esac

echo ""
print_success "Instalação concluída!"
echo ""

