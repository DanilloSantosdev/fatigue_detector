# 🚗 Sistema Completo de Detecção de Fadiga

> **Sistema profissional de detecção e monitoramento de fadiga em condutores**  
> MVP desenvolvido para Raspberry Pi 5 com câmera CSI

---

## 🎯 O que é este sistema?

Este é um sistema completo que transforma seu detector de fadiga em um **produto comercializável**, incluindo:

- ✅ **Detector de Fadiga** - Detecção em tempo real com MediaPipe
- ✅ **Backend API** - FastAPI + PostgreSQL para armazenamento de dados
- ✅ **Frontend Web** - Dashboard profissional com Vue 3 + Vuetify 3
- ✅ **Relatórios** - Exportação em PDF e Excel
- ✅ **Screenshots** - Captura automática de imagens nos alertas
- ✅ **Multi-veículo** - Gerencie múltiplos veículos e condutores

---

## 🚀 Instalação Rápida

```bash
# 1. Clone ou navegue até o diretório do projeto
cd /home/tecnoly/Documents/testCam/fatigue_detector

# 2. Execute o instalador automático
./install.sh

# 3. Configure o banco de dados (instruções no final da instalação)

# 4. Inicie o sistema
./start_all.sh
```

---

## 📚 Documentação

Este projeto possui **três documentações principais**:

### 1. 📖 [README_SISTEMA.md](README_SISTEMA.md)
**Visão geral do sistema completo**
- Arquitetura e componentes
- Estrutura de diretórios
- Fluxo de dados
- Tecnologias utilizadas

### 2. 🚀 [README_DEPLOY.md](README_DEPLOY.md)
**Guia completo de implantação**
- Configuração passo a passo
- Configuração do banco de dados
- Setup de backend e frontend
- Acesso via internet (ngrok)
- Execução automática (systemd)
- Solução de problemas

### 3. 📝 [README.md](README.md)
**Documentação original do detector**
- Funcionamento do detector
- Configuração de sensibilidade
- Calibração automática
- Controles e parâmetros

---

## 🏗️ Arquitetura Simplificada

```
┌────────────────┐
│   Raspberry    │  Detector captura alertas
│   + Câmera     │  e envia para backend
└────────┬───────┘
         │
         ▼ HTTP POST (alertas + imagens)
┌────────────────┐
│    Backend     │  Armazena dados e serve
│   (FastAPI)    │  API REST
└────────┬───────┘
         │
         ▼ HTTP GET (consultas)
┌────────────────┐
│   Frontend     │  Dashboard web para
│    (Vue 3)     │  visualização e relatórios
└────────────────┘
```

---

## 💻 Requisitos

### Hardware
- Raspberry Pi 5 (ou 4)
- Câmera CSI ou USB
- 8GB+ RAM recomendado
- 32GB+ SD Card

### Software
- Raspberry Pi OS (Bookworm ou mais recente)
- Python 3.9+
- Node.js 18+
- PostgreSQL 13+

---

## 🎨 Interface do Sistema

### Dashboard
- Estatísticas de alertas em tempo real
- Tabela de alertas com filtros
- Visualização de imagens dos alertas
- Gráficos e métricas

### Relatórios
- Exportação em PDF (com ou sem imagens)
- Exportação em Excel para análise
- Filtros por data, veículo e tipo
- Personalização de conteúdo

### Gerenciamento
- Cadastro de veículos
- Edição de dados (motorista, placa, rota)
- Identificação única (UUID) para cada veículo

---

## 🔧 Comandos Principais

```bash
# Instalação completa
./install.sh

# Iniciar tudo (backend + frontend)
./start_all.sh

# Iniciar apenas backend
cd backend && ./run.sh

# Iniciar apenas frontend
cd frontend && ./run.sh

# Executar detector
source .v/bin/activate
python3 detector.py
```

---

## 📊 Acesso ao Sistema

Após iniciar o sistema:

| Componente | URL | Descrição |
|------------|-----|-----------|
| **Frontend** | http://localhost:3000 | Dashboard principal |
| **Backend** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Documentação interativa |
| **Imagens** | http://localhost:8000/uploads/{file} | Screenshots |

---

## 🌟 Funcionalidades Principais

### 1. Detecção em Tempo Real
- Olhos fechados (Eye Aspect Ratio)
- Bocejos (Mouth Aspect Ratio)
- Calibração automática
- Alertas visuais e sonoros

### 2. Armazenamento
- Todos os alertas salvos no PostgreSQL
- Screenshots capturados automaticamente
- Timestamp preciso de cada ocorrência
- Dados do veículo e condutor

### 3. Visualização
- Dashboard com estatísticas
- Filtros avançados (data, tipo, veículo)
- Visualização de imagens
- Detalhes completos de cada alerta

### 4. Relatórios
- PDF profissional
- Excel para análise
- Inclusão opcional de imagens
- Período personalizável

---

## 🔐 Segurança (MVP)

⚠️ **Este é um MVP** - Configurações de segurança básicas:

- CORS configurado para localhost e ngrok
- Sem autenticação (uso local)
- Banco de dados local

### Para Produção (próximos passos):
- [ ] JWT Authentication
- [ ] HTTPS obrigatório
- [ ] Rate limiting
- [ ] Validação rigorosa de inputs
- [ ] Logs de auditoria
- [ ] Backup automático

---

## 🛠️ Solução Rápida de Problemas

### Backend não inicia
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql

# Ver logs
cd backend && source venv/bin/activate
python -c "from app.database import init_db; import asyncio; asyncio.run(init_db())"
```

### Frontend não conecta
```bash
# Verificar se backend está rodando
curl http://localhost:8000/health

# Ver logs do browser (F12)
```

### Detector não envia dados
```bash
# Verificar configuração
cat .env | grep VEHICLE_ID

# Testar manualmente
curl http://localhost:8000/api/vehicles
```

---

## 📈 Próximos Passos (Roadmap)

### MVP ✅ (Atual)
- [x] Detector funcional
- [x] Backend API
- [x] Frontend completo
- [x] Relatórios PDF/Excel
- [x] Sistema integrado

### Fase 2 (Produção)
- [ ] Deploy em VPS
- [ ] Domínio próprio + HTTPS
- [ ] Autenticação de usuários
- [ ] Multi-tenant (vários clientes)
- [ ] Dashboard em tempo real (WebSockets)
- [ ] Notificações push/email

### Fase 3 (Escalabilidade)
- [ ] App mobile
- [ ] Análise de padrões (IA)
- [ ] Integração com telemetria
- [ ] API pública para integrações
- [ ] Backup em nuvem

---

## 🤝 Suporte

### Documentação
- [README_SISTEMA.md](README_SISTEMA.md) - Visão geral
- [README_DEPLOY.md](README_DEPLOY.md) - Guia de implantação
- [README.md](README.md) - Detector original

### Logs
```bash
# Backend
cd backend && source venv/bin/activate
# Ver output do terminal

# Frontend
# Ver console do browser (F12)

# Detector
# Ver output do terminal
```

---

## 📝 Estrutura de Arquivos Principais

```
fatigue_detector/
├── install.sh              # Instalador automático
├── start_all.sh           # Inicia backend + frontend
├── detector.py            # Detector modificado
├── .env.example           # Exemplo de configuração
│
├── backend/               # Backend FastAPI
│   ├── app/              # Código da aplicação
│   ├── requirements.txt  # Dependências
│   ├── .env.example      # Configuração
│   └── run.sh            # Executa backend
│
├── frontend/             # Frontend Vue 3
│   ├── src/             # Código-fonte
│   ├── package.json     # Dependências
│   └── run.sh           # Executa frontend
│
├── uploads/             # Screenshots dos alertas
│
└── README_*.md          # Documentações
```

---

## 🎓 Como Funciona

1. **Detector** roda no Raspberry Pi monitorando o condutor
2. Quando detecta fadiga:
   - Captura screenshot
   - Salva em `/uploads`
   - Envia dados para backend via HTTP POST
3. **Backend** recebe e armazena:
   - Dados do alerta no PostgreSQL
   - Referência para imagem
4. **Frontend** consulta backend:
   - Exibe alertas em tempo real
   - Mostra imagens
   - Gera relatórios

---

## 💡 Dicas

- **Calibração**: Deixe o sistema calibrar por 1 segundo com expressão neutra
- **Iluminação**: Mantenha boa iluminação no rosto do condutor
- **Posição**: Rosto centralizado a ~50-70cm da câmera
- **Rede**: Para acesso remoto, use ngrok (instruções no README_DEPLOY.md)
- **Backup**: Faça backup regular do banco de dados PostgreSQL

---

## 📞 Contato

Este é um MVP desenvolvido para demonstração e testes.  
Para implantação em produção, consulte README_DEPLOY.md.

---

**Sistema desenvolvido com ❤️ para Raspberry Pi 5**  
**Stack: Python + FastAPI + PostgreSQL + Vue 3 + Vuetify 3**

---

**Versão:** 1.0.0 (MVP)  
**Última atualização:** 2024

