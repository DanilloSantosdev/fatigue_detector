#!/bin/bash

# Script otimizado para instalação de dependências do frontend
# Resolve problemas de conectividade IPv6 no Raspberry Pi

echo "🔧 Configurando npm para IPv4 e timeouts otimizados..."

# Configurar npm para usar IPv4 e timeouts mais longos
npm config set registry https://registry.npmjs.org/
npm config set fetch-retry-mintimeout 20000
npm config set fetch-retry-maxtimeout 120000
npm config set fetch-retries 3
npm config set fetch-retry-factor 2

# Criar arquivo .npmrc com configurações otimizadas
cat > .npmrc << EOF
registry=https://registry.npmjs.org/
fetch-retry-mintimeout=20000
fetch-retry-maxtimeout=120000
fetch-retries=3
fetch-retry-factor=2
prefer-offline=false
network-timeout=300000
EOF

echo "🧹 Limpando cache do npm..."
npm cache clean --force

echo "📦 Instalando dependências com IPv4 forçado..."
# Forçar IPv4 e usar configurações otimizadas
NODE_OPTIONS="--dns-result-order=ipv4first" npm install \
    --prefer-offline \
    --no-audit \
    --no-fund \
    --network-timeout=300000

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
    echo "🚀 Para executar o projeto: npm run dev"
else
    echo "❌ Erro na instalação. Tentando método alternativo..."
    
    # Método alternativo com yarn se disponível
    if command -v yarn &> /dev/null; then
        echo "🔄 Tentando com Yarn..."
        yarn install --network-timeout 300000
    else
        echo "❌ Falha na instalação. Verifique sua conexão de internet."
        exit 1
    fi
fi

echo "🎉 Instalação concluída!"

