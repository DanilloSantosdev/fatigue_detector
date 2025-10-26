# ⚡ Guia de Início Rápido

> **Coloque seu sistema de detecção de fadiga no ar em 10 minutos!**

---

## 📋 Pré-requisitos

- ✅ Raspberry Pi 5 com câmera CSI
- ✅ Python 3.9+ instalado
- ✅ Node.js 18+ instalado
- ✅ PostgreSQL instalado

---

## 🚀 Passo a Passo

### 1️⃣ Instalar Dependências (1min)

```bash
cd /home/tecnoly/Documents/testCam/fatigue_detector
./install.sh
```

### 2️⃣ Configurar Banco de Dados (2min)

```bash
# Entrar no PostgreSQL
sudo -u postgres psql

# Executar comandos (copie e cole tudo de uma vez):
CREATE DATABASE fatigue_db;
CREATE USER fatigue_user WITH PASSWORD 'senha123';
GRANT ALL PRIVILEGES ON DATABASE fatigue_db TO fatigue_user;
\q
```

### 3️⃣ Configurar Backend (1min)

```bash
# Editar arquivo de configuração
nano backend/.env

# Certifique-se que DATABASE_URL está correto:
DATABASE_URL=postgresql+asyncpg://fatigue_user:senha123@localhost:5432/fatigue_db
```

Salve com `Ctrl+O`, Enter, `Ctrl+X`

### 4️⃣ Iniciar Sistema (1min)

```bash
./start_all.sh
```

Aguarde abrir automaticamente:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### 5️⃣ Cadastrar Veículo (2min)

1. Acesse: http://localhost:3000/vehicles
2. Clique em "Novo Veículo"
3. Preencha:
   - Nome: `Ônibus 001`
   - Placa: `ABC-1234`
   - (outros campos opcionais)
4. Clique em "Cadastrar"
5. **COPIE O ID** que aparece na lista

### 6️⃣ Configurar Detector (1min)

```bash
# Criar arquivo de configuração
nano .env
```

Cole (substitua `COLE_UUID_AQUI` pelo ID copiado):

```
API_BASE_URL=http://localhost:8000
VEHICLE_ID=COLE_UUID_AQUI
```

Salve com `Ctrl+O`, Enter, `Ctrl+X`

### 7️⃣ Executar Detector (1min)

Em um novo terminal:

```bash
cd /home/tecnoly/Documents/testCam/fatigue_detector
source .v/bin/activate
python3 detector.py
```

### 8️⃣ Testar Sistema (1min)

1. Olhe para a câmera
2. Feche os olhos por 1 segundo → deve gerar alerta!
3. Faça um bocejo prolongado → deve gerar alerta!
4. Abra o navegador: http://localhost:3000
5. Veja os alertas na Dashboard ✅

---

## 🎉 Pronto!

Seu sistema está funcionando! Agora você pode:

- 📊 Ver alertas no Dashboard
- 🖼️ Visualizar screenshots capturados
- 📄 Gerar relatórios em PDF ou Excel
- 🚗 Cadastrar mais veículos

---

## 🔧 Comandos Úteis

```bash
# Parar sistema: Ctrl+C no terminal onde rodou ./start_all.sh

# Ver logs do backend:
# (já aparecem no terminal)

# Ver logs do detector:
# (já aparecem no terminal onde rodou detector.py)

# Reiniciar sistema:
./start_all.sh
```

---

## 🐛 Problemas Comuns

### "Erro ao conectar ao banco"
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### "VEHICLE_ID não configurado"
```bash
# Verificar se .env existe
cat .env

# Se não existir, criar:
nano .env
# Adicionar: VEHICLE_ID=uuid-do-veiculo
```

### "Porta 8000 já em uso"
```bash
# Matar processo na porta 8000
sudo lsof -ti:8000 | xargs kill -9
```

### "Frontend não carrega"
```bash
# Verificar se backend está rodando
curl http://localhost:8000/health
# Deve retornar: {"status":"healthy"}
```

---

## 📚 Próximos Passos

Após ter o sistema funcionando:

1. **Acesso Remoto**: [README_DEPLOY.md](README_DEPLOY.md) → Seção ngrok
2. **Execução Automática**: [systemd/README_SYSTEMD.md](systemd/README_SYSTEMD.md)
3. **Ajustar Sensibilidade**: [README.md](README.md) → Seção Configuração

---

## 💡 Dicas Importantes

- ✅ **Calibração**: Ao iniciar detector, fique com expressão neutra por 1s
- ✅ **Iluminação**: Mantenha boa luz no rosto
- ✅ **Posição**: Fique a 50-70cm da câmera
- ✅ **Teste**: Simule fadiga fechando olhos por 1s ou bocejando

---

## 🎯 Checklist de Instalação

- [ ] PostgreSQL instalado e rodando
- [ ] Banco de dados `fatigue_db` criado
- [ ] Usuário `fatigue_user` criado
- [ ] Backend `.env` configurado
- [ ] Backend iniciado (http://localhost:8000)
- [ ] Frontend iniciado (http://localhost:3000)
- [ ] Veículo cadastrado
- [ ] UUID do veículo copiado
- [ ] Detector `.env` configurado com VEHICLE_ID
- [ ] Detector rodando
- [ ] Teste de alerta funcionando ✅

---

## 📞 Precisa de Mais Ajuda?

Consulte a documentação completa:

- **Visão Geral**: [README_MAIN.md](README_MAIN.md)
- **Sistema Completo**: [README_SISTEMA.md](README_SISTEMA.md)
- **Deploy Detalhado**: [README_DEPLOY.md](README_DEPLOY.md)
- **Detector Original**: [README.md](README.md)

---

**Tempo total de instalação: ~10 minutos** ⏱️  
**Dificuldade: Iniciante** 🟢

---

Bom uso! 🚀

