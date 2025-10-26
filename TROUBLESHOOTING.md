# 🔧 Guia de Solução de Problemas

## 🚨 Problemas Comuns e Soluções

---

## 1. Instalação do Frontend Trava ou Demora Muito

### Sintomas:
- `npm install` demora mais de 30 minutos
- Terminal para de responder
- Processo trava sem erro

### Soluções:

#### A) Use o instalador otimizado (RECOMENDADO):
```bash
cd frontend
./install_frontend.sh
# Escolha opção 1 (Rápido)
```

#### B) Instale manualmente com flags otimizadas:
```bash
cd frontend

# Configurar npm
npm config set audit false
npm config set fund false

# Instalar
npm install --no-audit --no-fund --prefer-offline --loglevel=info
```

#### C) Se continuar travando, instale em partes:
```bash
cd frontend

# Limpar cache
npm cache clean --force

# Instalar dependências principais primeiro
npm install vue@^3.4.0 --no-audit --no-fund

# Depois o resto
npm install --no-audit --no-fund
```

#### D) Última opção - aumentar memória swap:
```bash
# Verificar swap atual
free -h

# Aumentar swap temporariamente (se menor que 2GB)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Mudar CONF_SWAPSIZE para 2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 2. Backend Não Inicia

### Sintomas:
- Erro ao executar `./backend/run.sh`
- "ModuleNotFoundError"
- "Connection refused"

### Soluções:

#### A) Verificar ambiente virtual:
```bash
cd backend

# Verificar se venv existe
ls -la venv/

# Se não existir, criar:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### B) Verificar PostgreSQL:
```bash
# Ver se está rodando
sudo systemctl status postgresql

# Se não estiver, iniciar:
sudo systemctl start postgresql

# Testar conexão
psql -U fatigue_user -d fatigue_db
# (senha: senha123 ou a que você configurou)
```

#### C) Verificar .env:
```bash
cat backend/.env

# Deve ter:
DATABASE_URL=postgresql+asyncpg://fatigue_user:senha123@localhost:5432/fatigue_db
```

#### D) Ver erros detalhados:
```bash
cd backend
source venv/bin/activate
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

---

## 3. Frontend Não Conecta ao Backend

### Sintomas:
- Erro CORS no console do browser
- "Network Error"
- Dados não carregam

### Soluções:

#### A) Verificar se backend está rodando:
```bash
curl http://localhost:8000/health
# Deve retornar: {"status":"healthy"}
```

#### B) Verificar proxy do Vite:
```bash
# Editar frontend/vite.config.js
# Verificar se tem:
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

#### C) Limpar cache do frontend:
```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

#### D) Verificar CORS no backend:
```bash
# Editar backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 4. Detector Não Envia Alertas

### Sintomas:
- Detector roda mas alertas não aparecem no frontend
- "API desabilitada"
- Erro de conexão

### Soluções:

#### A) Verificar VEHICLE_ID:
```bash
# Ver se está configurado
cat .env | grep VEHICLE_ID

# Deve ter um UUID válido
# Se não tiver, cadastre um veículo primeiro
```

#### B) Testar conexão manualmente:
```bash
# Cadastrar veículo de teste
curl -X POST http://localhost:8000/api/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Teste",
    "placa": "TEST-001"
  }'

# Copiar o "id" retornado

# Editar .env
nano .env
# Adicionar: VEHICLE_ID=uuid-copiado-aqui
```

#### C) Verificar dependências:
```bash
source .v/bin/activate
pip install requests
```

#### D) Ver logs do detector:
```bash
# Executar e ver mensagens
python3 detector.py

# Deve aparecer:
# "✅ API configurada: http://localhost:8000"
# "✅ Alerta enviado ao backend com sucesso!"
```

---

## 5. Erro ao Gerar Relatórios

### Sintomas:
- Erro ao exportar PDF/Excel
- "No alerts found"
- Download não inicia

### Soluções:

#### A) Verificar se há alertas:
```bash
curl http://localhost:8000/api/alerts | jq
```

#### B) Testar geração manual:
```bash
cd backend
source venv/bin/activate
python -c "
from app.report_generator import generate_pdf_report
print('ReportLab OK')
"
```

#### C) Verificar dependências:
```bash
cd backend
source venv/bin/activate
pip install reportlab pandas openpyxl
```

---

## 6. Porta Já Em Uso

### Sintomas:
- "Address already in use"
- "Port 8000 is already allocated"

### Soluções:

#### A) Encontrar e matar processo:
```bash
# Backend (porta 8000)
sudo lsof -ti:8000 | xargs kill -9

# Frontend (porta 3000)
sudo lsof -ti:3000 | xargs kill -9
```

#### B) Usar portas diferentes:
```bash
# Backend
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8001

# Frontend (editar package.json ou)
cd frontend
npm run dev -- --port 3001
```

---

## 7. Imagens Não Aparecem

### Sintomas:
- Alertas aparecem mas sem imagem
- 404 ao carregar imagem
- Placeholder "imagem não disponível"

### Soluções:

#### A) Verificar diretório uploads:
```bash
ls -la uploads/

# Se não existir
mkdir -p uploads
chmod 755 uploads
```

#### B) Verificar configuração do detector:
```bash
# No detector.py, linha ~299
screenshots_dir = Path(__file__).parent / "../uploads"

# Deve criar automaticamente, mas se não:
mkdir -p /home/tecnoly/Documents/testCam/fatigue_detector/uploads
```

#### C) Verificar permissões:
```bash
sudo chown -R tecnoly:tecnoly uploads/
chmod -R 755 uploads/
```

---

## 8. Raspberry Pi Lento/Travando

### Sintomas:
- Sistema lento
- Detector com baixo FPS
- Frontend demorando

### Soluções:

#### A) Aumentar swap:
```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Mudar CONF_SWAPSIZE para 2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### B) Desabilitar interface do detector:
```bash
# Editar detector.py, linha ~53
SHOW_INTERFACE = False  # Não mostrar janela OpenCV
```

#### C) Reduzir qualidade da câmera:
```bash
# Editar detector.py, linhas 39-40
CAMERA_WIDTH = 320   # Era 640
CAMERA_HEIGHT = 240  # Era 480
```

#### D) Fechar outros programas:
```bash
# Ver processos
htop

# Fechar browser se não precisar
# Desabilitar serviços desnecessários
```

---

## 9. Banco de Dados Corrompido

### Sintomas:
- Erros ao consultar dados
- "relation does not exist"
- Dados perdidos

### Soluções:

#### A) Recriar tabelas:
```bash
# Entrar no PostgreSQL
sudo -u postgres psql fatigue_db

# Dropar e recriar (CUIDADO: apaga dados!)
DROP TABLE alerts;
DROP TABLE vehicles;
\q

# Reiniciar backend (recria tabelas)
cd backend
./run.sh
```

#### B) Fazer backup antes:
```bash
# Backup
pg_dump -U fatigue_user fatigue_db > backup.sql

# Restaurar
psql -U fatigue_user fatigue_db < backup.sql
```

---

## 10. Erro de Memória no npm install

### Sintomas:
- "JavaScript heap out of memory"
- "Killed"
- npm trava

### Soluções:

#### A) Aumentar limite de memória do Node:
```bash
cd frontend

# Instalar com mais memória
NODE_OPTIONS="--max-old-space-size=512" npm install --no-audit --no-fund
```

#### B) Instalar em partes:
```bash
cd frontend

# Instalar dependências principais
npm install vue vue-router axios

# Instalar Vuetify separadamente
npm install vuetify

# Instalar o resto
npm install
```

---

## 📞 Comandos Úteis de Diagnóstico

```bash
# Ver status de tudo
systemctl status postgresql
ps aux | grep uvicorn
ps aux | grep "npm run dev"
ps aux | grep detector.py

# Ver logs do sistema
sudo journalctl -xe

# Ver uso de recursos
htop
free -h
df -h

# Testar conectividade
curl http://localhost:8000/health
curl http://localhost:3000

# Ver processos nas portas
sudo lsof -i :8000
sudo lsof -i :3000

# Limpar tudo e recomeçar
cd backend && rm -rf venv
cd frontend && rm -rf node_modules
./install.sh
```

---

## 🆘 Ainda Com Problemas?

1. **Ver logs detalhados**:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --log-level debug
   ```

2. **Testar componentes individualmente**:
   - PostgreSQL: `psql -U fatigue_user fatigue_db`
   - Backend: `curl http://localhost:8000/docs`
   - Frontend: Abrir console do browser (F12)
   - Detector: Ver output no terminal

3. **Reiniciar tudo**:
   ```bash
   # Parar todos os processos
   pkill -f uvicorn
   pkill -f "npm run dev"
   pkill -f detector.py
   
   # Reiniciar
   ./start_all.sh
   ```

4. **Verificar logs do sistema**:
   ```bash
   sudo journalctl -n 100
   dmesg | tail -50
   ```

---

## 💡 Dicas de Prevenção

- ✅ Sempre use o instalador otimizado para frontend
- ✅ Mantenha o sistema atualizado
- ✅ Faça backup regular do banco de dados
- ✅ Monitore uso de memória
- ✅ Use swap adequado (2GB+)
- ✅ Feche programas desnecessários
- ✅ Reinicie o Raspberry Pi periodicamente

---

**Última atualização:** 2024

