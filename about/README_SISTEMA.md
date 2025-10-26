# 🚗 Sistema de Detecção de Fadiga - Completo

## 📋 Descrição do Projeto

Sistema completo de detecção e monitoramento de fadiga em condutores de veículos, desenvolvido para Raspberry Pi 5 com câmera CSI e inferências Hailo8.

### Funcionalidades

✅ **Detecção em Tempo Real**
- Detecção de olhos fechados (Eye Aspect Ratio)
- Detecção de bocejos (Mouth Aspect Ratio)
- Calibração automática personalizada
- Alertas visuais e sonoros

✅ **Backend API (FastAPI + PostgreSQL)**
- Cadastro de veículos
- Registro de alertas com timestamp
- Captura e armazenamento de screenshots
- API RESTful completa
- Geração de relatórios (PDF/Excel)

✅ **Frontend Web (Vue 3 + Vuetify 3)**
- Dashboard com estatísticas em tempo real
- Visualização de alertas com imagens
- Filtros por data, tipo e veículo
- Exportação de relatórios personalizados
- Gerenciamento de veículos

✅ **Integração Completa**
- Detector envia dados automaticamente para API
- Screenshots salvos e acessíveis via web
- Relatórios com histórico completo de ocorrências

## 🏗️ Arquitetura

```
┌─────────────────────┐
│  Raspberry Pi 5     │
│  ┌───────────────┐  │
│  │   Detector    │  │──┐
│  │  (detector.py)│  │  │ HTTP POST
│  └───────────────┘  │  │
└─────────────────────┘  │
                         ▼
                  ┌─────────────┐
                  │   Backend   │
                  │  (FastAPI)  │
                  │             │
                  │ PostgreSQL  │
                  └─────────────┘
                         ▲
                         │ HTTP GET
                         │
                  ┌─────────────┐
                  │  Frontend   │
                  │   (Vue 3)   │
                  │             │
                  │  Navegador  │
                  └─────────────┘
```

## 📂 Estrutura de Diretórios

```
fatigue_detector/
├── backend/                    # Backend FastAPI
│   ├── app/
│   │   ├── main.py            # Aplicação principal
│   │   ├── database.py        # Configuração PostgreSQL
│   │   ├── models.py          # Modelos SQLAlchemy
│   │   ├── schemas.py         # Schemas Pydantic
│   │   ├── crud.py            # Operações CRUD
│   │   ├── report_generator.py # Geração de relatórios
│   │   └── api/
│   │       ├── alerts.py      # Endpoints de alertas
│   │       ├── vehicles.py    # Endpoints de veículos
│   │       └── reports.py     # Endpoints de relatórios
│   ├── requirements.txt
│   ├── .env.example
│   └── run.sh
│
├── frontend/                   # Frontend Vue 3
│   ├── src/
│   │   ├── components/
│   │   │   └── AlertDetail.vue
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Reports.vue
│   │   │   └── VehicleConfig.vue
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── plugins/
│   │   │   └── vuetify.js
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   ├── vite.config.js
│   └── run.sh
│
├── uploads/                    # Screenshots dos alertas
│
├── detector.py                 # Detector de fadiga (modificado)
├── test_landmarks.py
├── requirements.txt            # Dependências do detector
│
├── start_all.sh               # Inicia backend + frontend
├── .env.example
├── .gitignore
│
├── README.md                   # Documentação original
├── README_SISTEMA.md          # Este arquivo
└── README_DEPLOY.md           # Guia de implantação detalhado
```

## 🚀 Início Rápido

### 1. Configurar Banco de Dados

```bash
# Criar banco PostgreSQL
sudo -u postgres psql
CREATE DATABASE fatigue_db;
CREATE USER fatigue_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE fatigue_db TO fatigue_user;
\q
```

### 2. Configurar Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar .env
cp .env.example .env
# Editar .env com suas credenciais do banco
```

### 3. Configurar Frontend

```bash
cd frontend
npm install
```

### 4. Iniciar Sistema

```bash
# Opção 1: Iniciar tudo de uma vez
./start_all.sh

# Opção 2: Iniciar separadamente
cd backend && ./run.sh    # Terminal 1
cd frontend && ./run.sh   # Terminal 2
```

### 5. Cadastrar Veículo

Acesse `http://localhost:3000/vehicles` e cadastre seu primeiro veículo.
Copie o ID gerado.

### 6. Configurar Detector

```bash
# Criar .env na raiz
cp .env.example .env

# Editar .env
nano .env
```

Adicionar:
```
API_BASE_URL=http://localhost:8000
VEHICLE_ID=cole-uuid-do-veiculo-aqui
```

### 7. Executar Detector

```bash
source .v/bin/activate
python3 detector.py
```

## 📊 Uso do Sistema

### Dashboard

- **URL:** `http://localhost:3000`
- Visualize estatísticas de alertas em tempo real
- Filtre por veículo, tipo de alerta e data
- Clique em um alerta para ver detalhes e imagem

### Relatórios

- **URL:** `http://localhost:3000/reports`
- Selecione período e veículo
- Exporte em PDF (com ou sem imagens) ou Excel
- Relatórios incluem todas as informações dos alertas

### Veículos

- **URL:** `http://localhost:3000/vehicles`
- Cadastre novos veículos
- Edite informações (motorista, frota, rota)
- Copie ID do veículo para configurar no Raspberry Pi

### API Docs

- **URL:** `http://localhost:8000/docs`
- Documentação interativa (Swagger UI)
- Teste endpoints diretamente
- Veja schemas e exemplos

## 🔧 Configuração Avançada

### Acesso via Internet (ngrok)

```bash
# Instalar ngrok
# Baixar de https://ngrok.com/

# Expor backend
ngrok http 8000

# Atualizar .env do detector com URL pública
API_BASE_URL=https://sua-url.ngrok.io
```

### Execução Automática (systemd)

Veja o arquivo `README_DEPLOY.md` para configuração de serviços systemd.

### Ajuste de Sensibilidade

Editar `detector.py` (linhas 33-36):

```python
EAR_THRESHOLD = 0.25      # Menor = mais sensível para olhos
EAR_CONSEC_FRAMES = 20    # Menos frames = detecta mais rápido
MAR_THRESHOLD = 1.25      # Ajustado automaticamente na calibração
MAR_CONSEC_FRAMES = 10    # Menos frames = detecta mais rápido
```

## 📈 Fluxo de Dados

1. **Detector captura frame da câmera**
   - MediaPipe detecta landmarks faciais
   - Calcula EAR (olhos) e MAR (boca)
   - Identifica fadiga baseado em thresholds

2. **Alerta disparado**
   - Screenshot capturado e salvo em `/uploads`
   - Dados enviados via POST para `/api/alerts`
   - Backend salva no PostgreSQL

3. **Frontend consulta dados**
   - GET `/api/alerts` lista alertas
   - GET `/api/alerts/stats` estatísticas
   - GET `/uploads/{filename}` exibe imagens

4. **Geração de relatório**
   - Usuário seleciona filtros
   - GET `/api/reports/export` gera PDF/Excel
   - Download automático do arquivo

## 🗃️ Estrutura do Banco de Dados

### Tabela: vehicles

```sql
id          UUID PRIMARY KEY
nome        VARCHAR(200) NOT NULL
placa       VARCHAR(20) UNIQUE NOT NULL
motorista   VARCHAR(200)
frota       VARCHAR(100)
rota        VARCHAR(200)
created_at  TIMESTAMP DEFAULT NOW()
```

### Tabela: alerts

```sql
id          UUID PRIMARY KEY
vehicle_id  UUID FOREIGN KEY -> vehicles(id)
timestamp   TIMESTAMP NOT NULL
tipo        ENUM('eyes_closed', 'yawning')
severity    ENUM('critical', 'moderate')
ear_value   FLOAT
mar_value   FLOAT
image_path  VARCHAR(500)
created_at  TIMESTAMP DEFAULT NOW()
```

## 🔐 Segurança

### Para MVP
- CORS configurado para localhost e ngrok
- Sem autenticação (sistema local)

### Para Produção (próximos passos)
- [ ] Implementar JWT Authentication
- [ ] HTTPS obrigatório
- [ ] Rate limiting
- [ ] Validação de inputs mais rigorosa
- [ ] Logs de auditoria
- [ ] Backup automático

## 📱 Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM async
- **Pydantic** - Validação de dados
- **ReportLab** - Geração de PDF
- **Pandas** - Manipulação de dados / Excel

### Frontend
- **Vue 3** - Framework JavaScript progressivo
- **Vuetify 3** - Framework de componentes Material Design
- **Vue Router** - Roteamento
- **Axios** - Cliente HTTP
- **Vite** - Build tool

### Detector
- **MediaPipe** - Detecção de landmarks faciais
- **OpenCV** - Processamento de imagem
- **Picamera2** - Interface com câmera CSI
- **NumPy** - Computação numérica
- **SciPy** - Cálculos científicos

## 🐛 Problemas Conhecidos

- Frontend pode demorar alguns segundos para carregar imagens grandes
- Relatório PDF com muitas imagens pode ser lento
- ngrok gratuito tem limite de conexões

## 📝 TODO / Melhorias Futuras

- [ ] Dashboard em tempo real com WebSockets
- [ ] Notificações push quando alertas são criados
- [ ] Gráficos de evolução temporal
- [ ] Mapa de calor de horários com mais alertas
- [ ] App mobile (React Native ou Flutter)
- [ ] Análise de padrões de fadiga por motorista
- [ ] Integração com sistemas de telemetria veicular
- [ ] Múltiplos idiomas

## 📄 Documentação Adicional

- `README.md` - Documentação original do detector
- `README_DEPLOY.md` - Guia completo de implantação
- `GUIA_RAPIDO.txt` - Guia rápido do detector

## 🤝 Contribuindo

Este é um MVP. Sugestões e melhorias são bem-vindas!

---

**Desenvolvido para Raspberry Pi 5 com MediaPipe e Hailo8**  
**MVP - Versão 1.0.0**

