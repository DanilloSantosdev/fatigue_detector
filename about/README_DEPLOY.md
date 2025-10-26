# 🚀 Guia de Implantação - Sistema de Detecção de Fadiga

## 📋 Visão Geral

Este guia fornece instruções completas para implantar o sistema de detecção de fadiga, incluindo:
- Backend FastAPI com PostgreSQL
- Frontend Vue 3 + Vuetify 3
- Detector de fadiga integrado
- Acesso via internet com ngrok

---

## 📦 Pré-requisitos

### Sistema
- Raspberry Pi 5 com câmera CSI configurada
- Sistema operacional: Raspberry Pi OS (recomendado)
- Python 3.9 ou superior
- Node.js 18+ e npm
- PostgreSQL 13+

### Instalações básicas

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Instalar Node.js (se não tiver)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Instalar pip e venv
sudo apt install python3-pip python3-venv -y
```

---

## 🗄️ Configuração do Banco de Dados

### 1. Criar banco de dados e usuário

```bash
# Acessar PostgreSQL como superusuário
sudo -u postgres psql

# Executar comandos SQL:
CREATE DATABASE fatigue_db;
CREATE USER fatigue_user WITH PASSWORD 'senha_segura_aqui';
GRANT ALL PRIVILEGES ON DATABASE fatigue_db TO fatigue_user;
\q
```

### 2. Configurar acesso remoto (opcional)

Editar `/etc/postgresql/*/main/postgresql.conf`:
```
listen_addresses = 'localhost'
```

Editar `/etc/postgresql/*/main/pg_hba.conf`:
```
local   all             fatigue_user                            md5
```

Reiniciar PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## 🔧 Configuração do Backend

### 1. Criar ambiente virtual e instalar dependências

```bash
cd /home/tecnoly/Documents/testCam/fatigue_detector/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

Criar arquivo `.env` no diretório `backend/`:

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://fatigue_user:senha_segura_aqui@localhost:5432/fatigue_db
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
UPLOADS_DIR=../uploads
CORS_ORIGINS=http://localhost:3000,https://*.ngrok.io
```

### 3. Inicializar banco de dados

```bash
# O banco será inicializado automaticamente na primeira execução
# mas você pode testar manualmente com:
cd backend
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 4. Executar backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ou criar um script `backend/run.sh`:

```bash
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

```bash
chmod +x backend/run.sh
./backend/run.sh
```

---

## 🎨 Configuração do Frontend

### 1. Instalar dependências

```bash
cd /home/tecnoly/Documents/testCam/fatigue_detector/frontend
npm install
```

### 2. Configurar variáveis de ambiente (opcional)

Criar arquivo `.env` no diretório `frontend/` (opcional):

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000
```

### 3. Executar frontend em desenvolvimento

```bash
cd frontend
npm run dev
```

Acesse: `http://localhost:3000`

### 4. Build para produção

```bash
cd frontend
npm run build
# Arquivos gerados em: frontend/dist/
```

Para servir em produção, você pode usar nginx ou servir diretamente:

```bash
npm install -g serve
serve -s dist -l 3000
```

---

## 📸 Configuração do Detector

### 1. Cadastrar veículo

Primeiro, cadastre um veículo através do frontend ou API:

**Via Frontend:**
1. Acesse `http://localhost:3000/vehicles`
2. Preencha o formulário e cadastre
3. Copie o ID do veículo criado

**Via API (curl):**
```bash
curl -X POST http://localhost:8000/api/vehicles \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Ônibus 001",
    "placa": "ABC-1234",
    "motorista": "João Silva",
    "frota": "Frota A",
    "rota": "Centro-Bairro"
  }'
```

Copie o `id` retornado.

### 2. Configurar detector

Editar o arquivo ou criar `.env` no diretório raiz:

```bash
# .env (na raiz do projeto)
API_BASE_URL=http://localhost:8000
VEHICLE_ID=uuid-do-veiculo-aqui
```

Ou editar diretamente no `detector.py` (linhas 59-61):

```python
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
VEHICLE_ID = os.getenv("VEHICLE_ID", "cole-uuid-aqui")
ENABLE_API = True
```

### 3. Instalar dependências do detector

```bash
cd /home/tecnoly/Documents/testCam/fatigue_detector
source .v/bin/activate
pip install -r requirements.txt
```

### 4. Executar detector

```bash
source .v/bin/activate
python3 detector.py
```

---

## 🌐 Acesso via Internet com ngrok

### 1. Instalar ngrok

```bash
# Download ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm64.tgz
tar xvzf ngrok-v3-stable-linux-arm64.tgz
sudo mv ngrok /usr/local/bin/

# Autenticar (crie conta em https://ngrok.com/)
ngrok config add-authtoken SEU_TOKEN_AQUI
```

### 2. Expor backend

```bash
ngrok http 8000
```

Anote a URL pública gerada (ex: `https://abcd1234.ngrok.io`)

### 3. Atualizar configurações

**Backend `.env`:**
```bash
CORS_ORIGINS=http://localhost:3000,https://abcd1234.ngrok.io,https://*.ngrok.io
```

**Frontend (para acesso remoto):**
Editar `frontend/.env`:
```bash
VITE_API_URL=https://abcd1234.ngrok.io
```

Rebuild frontend:
```bash
cd frontend
npm run build
```

### 4. Expor frontend (opcional)

Em outro terminal:
```bash
ngrok http 3000
```

---

## 🔄 Execução Automática (systemd)

### Backend Service

Criar `/etc/systemd/system/fatigue-backend.service`:

```ini
[Unit]
Description=Fatigue Detection Backend
After=network.target postgresql.service

[Service]
Type=simple
User=tecnoly
WorkingDirectory=/home/tecnoly/Documents/testCam/fatigue_detector/backend
Environment="PATH=/home/tecnoly/Documents/testCam/fatigue_detector/backend/venv/bin"
ExecStart=/home/tecnoly/Documents/testCam/fatigue_detector/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Detector Service

Criar `/etc/systemd/system/fatigue-detector.service`:

```ini
[Unit]
Description=Fatigue Detection System
After=network.target fatigue-backend.service

[Service]
Type=simple
User=tecnoly
WorkingDirectory=/home/tecnoly/Documents/testCam/fatigue_detector
Environment="PATH=/home/tecnoly/Documents/testCam/fatigue_detector/.v/bin"
Environment="API_BASE_URL=http://localhost:8000"
Environment="VEHICLE_ID=uuid-do-veiculo"
ExecStart=/home/tecnoly/Documents/testCam/fatigue_detector/.v/bin/python detector.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Ativar serviços

```bash
sudo systemctl daemon-reload
sudo systemctl enable fatigue-backend
sudo systemctl enable fatigue-detector
sudo systemctl start fatigue-backend
sudo systemctl start fatigue-detector

# Ver status
sudo systemctl status fatigue-backend
sudo systemctl status fatigue-detector

# Ver logs
sudo journalctl -u fatigue-backend -f
sudo journalctl -u fatigue-detector -f
```

---

## 📊 Testando o Sistema

### 1. Verificar backend

```bash
curl http://localhost:8000/health
# Deve retornar: {"status":"healthy"}
```

### 2. Verificar banco de dados

```bash
curl http://localhost:8000/api/vehicles
# Deve retornar lista de veículos
```

### 3. Acessar frontend

Abra o navegador: `http://localhost:3000`

Você deve ver:
- Dashboard com estatísticas
- Lista de veículos
- Opções de relatórios

### 4. Testar detector

Execute o detector e simule fadiga:
- Feche os olhos por 1 segundo
- Faça um bocejo prolongado

Verifique no frontend se os alertas aparecem.

---

## 🐛 Solução de Problemas

### Erro de conexão com PostgreSQL

```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Ver logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Erro ao importar módulos Python

```bash
# Verificar ambiente virtual ativado
which python
# Deve apontar para o venv

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Frontend não conecta ao backend

1. Verificar se backend está rodando: `curl http://localhost:8000/health`
2. Verificar proxy no `vite.config.js`
3. Verificar CORS no backend `.env`

### Detector não envia alertas

1. Verificar `VEHICLE_ID` configurado corretamente
2. Verificar se veículo existe no banco
3. Verificar logs do detector
4. Testar conexão manualmente:
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
     -H "Content-Type: application/json" \
     -d '{
       "vehicle_id": "uuid-do-veiculo",
       "timestamp": "2024-01-01T12:00:00",
       "tipo": "eyes_closed",
       "severity": "critical",
       "ear_value": 0.2,
       "mar_value": 1.5
     }'
   ```

---

## 📱 Próximos Passos

### Para MVP
✅ Sistema funcional localmente  
✅ Acesso via ngrok  
✅ Cadastro de veículos  
✅ Visualização de alertas  
✅ Geração de relatórios  

### Para Produção
- [ ] Migrar para VPS (AWS, DigitalOcean, etc)
- [ ] Configurar domínio próprio
- [ ] Implementar HTTPS com Let's Encrypt
- [ ] Adicionar autenticação JWT
- [ ] Backup automático do banco de dados
- [ ] Monitoramento e alertas
- [ ] Dashboard em tempo real com WebSockets

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs do sistema
2. Consultar documentação das tecnologias usadas
3. Revisar configurações de rede e firewall

---

**Sistema desenvolvido para Raspberry Pi 5 com câmera CSI**  
**Stack: FastAPI + PostgreSQL + Vue 3 + Vuetify 3**

