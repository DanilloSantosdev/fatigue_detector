#!/bin/bash
# Script de instalação rápida do Sistema de Detecção de Fadiga

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Sistema de Detecção de Fadiga - Instalação Rápida      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Verificar se está rodando no Raspberry Pi
print_info "Verificando sistema..."
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo ""
    print_error "Este script foi desenvolvido para Raspberry Pi"
    echo "  Você pode continuar, mas alguns recursos podem não funcionar."
    read -p "  Continuar mesmo assim? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi

# Verificar Python
print_info "Verificando Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 não encontrado!"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION"

# Verificar Node.js
print_info "Verificando Node.js..."
if ! command -v node &> /dev/null; then
    print_error "Node.js não encontrado!"
    echo "  Instale com: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js $NODE_VERSION"

# Verificar PostgreSQL
print_info "Verificando PostgreSQL..."
if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL não encontrado!"
    echo "  Instale com: sudo apt install postgresql postgresql-contrib -y"
    exit 1
fi
print_success "PostgreSQL instalado"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Instalando Backend"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd backend

# Criar ambiente virtual
print_info "Criando ambiente virtual..."
python3 -m venv venv
print_success "Ambiente virtual criado"

# Ativar ambiente virtual e instalar dependências
print_info "Instalando dependências do backend..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependências do backend instaladas"

# Configurar .env se não existir
if [ ! -f ".env" ]; then
    print_info "Criando arquivo .env..."
    cat > .env << EOF
DATABASE_URL=postgresql+asyncpg://fatigue_user:senha123@localhost:5432/fatigue_db
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
UPLOADS_DIR=../uploads
CORS_ORIGINS=http://localhost:3000,https://*.ngrok.io
EOF
    print_success "Arquivo .env criado (ATENÇÃO: Configure a senha do banco!)"
else
    print_info ".env já existe, mantendo configurações atuais"
fi

cd ..

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Instalando Frontend"
echo "═══════════════════════════════════════════════════════════"
echo ""

cd frontend

# Verificar se node_modules já existe
if [ -d "node_modules" ]; then
    print_info "node_modules já existe, pulando instalação do frontend"
else
    echo ""
    print_info "Instalando dependências do frontend..."
    echo "⚠️  ATENÇÃO: Isso pode demorar de 10 a 30 minutos no Raspberry Pi!"
    echo "   Você verá o progresso abaixo. Seja paciente!"
    echo ""
    
    # Perguntar se quer instalar agora
    read -p "Deseja instalar agora? (s/N/pular): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        # Instalar com output visível para mostrar progresso
        print_info "Instalando... (você verá o progresso)"
        npm install --loglevel=info
        
        if [ $? -eq 0 ]; then
            print_success "Dependências do frontend instaladas com sucesso!"
        else
            print_error "Erro ao instalar dependências do frontend"
            echo "   Você pode instalar manualmente depois com:"
            echo "   cd frontend && npm install"
        fi
    else
        print_info "Instalação do frontend pulada"
        echo "   Para instalar depois, execute:"
        echo "   ${YELLOW}cd frontend && npm install${NC}"
    fi
fi

cd ..

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Instalando Detector"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Verificar se ambiente virtual do detector existe
if [ ! -d ".v" ]; then
    print_info "Criando ambiente virtual do detector..."
    python3 -m venv .v
    print_success "Ambiente virtual do detector criado"
fi

# Instalar dependências do detector
print_info "Instalando dependências do detector..."
source .v/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
print_success "Dependências do detector instaladas"
deactivate

# Criar diretório de uploads
print_info "Criando diretório de uploads..."
mkdir -p uploads
print_success "Diretório de uploads criado"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                 Instalação Concluída!                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Verificar status do frontend
if [ -d "frontend/node_modules" ]; then
    print_success "Backend instalado ✓"
    print_success "Frontend instalado ✓"
    print_success "Detector instalado ✓"
else
    print_success "Backend instalado ✓"
    print_error "Frontend NÃO instalado (pulado)"
    print_success "Detector instalado ✓"
    echo ""
    echo "Para instalar o frontend depois:"
    echo "   ${YELLOW}cd frontend && ./install_frontend.sh${NC}"
fi

echo ""
echo "⚠️  PRÓXIMOS PASSOS:"
echo ""
echo "1. Configure o banco de dados PostgreSQL:"
echo "   ${YELLOW}sudo -u postgres psql${NC}"
echo "   ${YELLOW}CREATE DATABASE fatigue_db;${NC}"
echo "   ${YELLOW}CREATE USER fatigue_user WITH PASSWORD 'senha123';${NC}"
echo "   ${YELLOW}GRANT ALL PRIVILEGES ON DATABASE fatigue_db TO fatigue_user;${NC}"
echo ""
echo "2. Edite backend/.env com suas credenciais do banco"
echo ""

if [ -d "frontend/node_modules" ]; then
    echo "3. Inicie o sistema completo:"
    echo "   ${YELLOW}./start_all.sh${NC}"
else
    echo "3. Instale o frontend primeiro:"
    echo "   ${YELLOW}cd frontend && ./install_frontend.sh${NC}"
    echo ""
    echo "4. Depois inicie o sistema:"
    echo "   ${YELLOW}./start_all.sh${NC}"
fi

echo ""
echo "💡 DICAS:"
echo "   • Backend sozinho: ${YELLOW}cd backend && ./run.sh${NC}"
echo "   • Frontend sozinho: ${YELLOW}cd frontend && npm run dev${NC}"
echo "   • Problemas? Veja: ${YELLOW}TROUBLESHOOTING.md${NC}"
echo ""

