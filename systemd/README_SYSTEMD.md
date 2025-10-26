# Configuração de Serviços Systemd

Este diretório contém arquivos de configuração para executar o sistema como serviços do systemd.

## 📋 Serviços Disponíveis

### 1. fatigue-backend.service
Backend FastAPI que gerencia a API e banco de dados.

### 2. fatigue-detector.service
Detector de fadiga que captura vídeo e envia alertas ao backend.

---

## 🚀 Instalação

### 1. Editar arquivos de serviço

Antes de instalar, **EDITE** os arquivos para ajustar aos seus caminhos:

```bash
# Editar backend service
nano fatigue-backend.service
# Verificar:
# - User e Group (seu usuário)
# - WorkingDirectory (caminho completo)
# - Environment PATH

# Editar detector service
nano fatigue-detector.service
# Verificar:
# - User e Group
# - WorkingDirectory
# - Environment VEHICLE_ID (UUID do veículo cadastrado)
```

### 2. Copiar arquivos para systemd

```bash
# Copiar serviços
sudo cp fatigue-backend.service /etc/systemd/system/
sudo cp fatigue-detector.service /etc/systemd/system/

# Definir permissões
sudo chmod 644 /etc/systemd/system/fatigue-backend.service
sudo chmod 644 /etc/systemd/system/fatigue-detector.service
```

### 3. Recarregar systemd

```bash
sudo systemctl daemon-reload
```

---

## ⚙️ Gerenciamento dos Serviços

### Habilitar (iniciar automaticamente no boot)

```bash
sudo systemctl enable fatigue-backend
sudo systemctl enable fatigue-detector
```

### Iniciar serviços

```bash
# Iniciar backend
sudo systemctl start fatigue-backend

# Aguardar 5 segundos

# Iniciar detector
sudo systemctl start fatigue-detector
```

### Ver status

```bash
sudo systemctl status fatigue-backend
sudo systemctl status fatigue-detector
```

### Parar serviços

```bash
sudo systemctl stop fatigue-detector
sudo systemctl stop fatigue-backend
```

### Desabilitar (não iniciar no boot)

```bash
sudo systemctl disable fatigue-detector
sudo systemctl disable fatigue-backend
```

### Reiniciar serviços

```bash
sudo systemctl restart fatigue-backend
sudo systemctl restart fatigue-detector
```

---

## 📝 Ver Logs

### Logs em tempo real

```bash
# Backend
sudo journalctl -u fatigue-backend -f

# Detector
sudo journalctl -u fatigue-detector -f
```

### Logs históricos

```bash
# Ver últimas 100 linhas
sudo journalctl -u fatigue-backend -n 100

# Ver logs de hoje
sudo journalctl -u fatigue-backend --since today

# Ver logs de um período
sudo journalctl -u fatigue-backend --since "2024-01-01" --until "2024-01-02"
```

---

## 🔧 Troubleshooting

### Serviço falha ao iniciar

1. Verificar logs:
   ```bash
   sudo journalctl -u fatigue-backend -xe
   ```

2. Verificar se caminhos estão corretos:
   ```bash
   # Verificar se venv existe
   ls -la /home/tecnoly/Documents/testCam/fatigue_detector/backend/venv
   
   # Verificar se .env está configurado
   cat /home/tecnoly/Documents/testCam/fatigue_detector/backend/.env
   ```

3. Testar manualmente:
   ```bash
   cd /home/tecnoly/Documents/testCam/fatigue_detector/backend
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Backend inicia mas detector não

1. Verificar VEHICLE_ID:
   ```bash
   sudo systemctl cat fatigue-detector | grep VEHICLE_ID
   ```

2. Editar service e atualizar:
   ```bash
   sudo nano /etc/systemd/system/fatigue-detector.service
   sudo systemctl daemon-reload
   sudo systemctl restart fatigue-detector
   ```

### Permissões negadas

```bash
# Garantir que o usuário tem permissão
sudo chown -R tecnoly:tecnoly /home/tecnoly/Documents/testCam/fatigue_detector
```

---

## 🎯 Ordem de Inicialização

O systemd está configurado para iniciar na ordem correta:

1. **PostgreSQL** (dependência)
2. **Backend** (aguarda PostgreSQL)
3. **Detector** (aguarda Backend)

---

## 📊 Monitoramento

### Ver se serviços estão rodando

```bash
systemctl list-units --type=service --state=running | grep fatigue
```

### Ver uso de recursos

```bash
# CPU e Memória
systemctl status fatigue-backend fatigue-detector

# Detalhado
top -p $(pgrep -f "uvicorn") -p $(pgrep -f "detector.py")
```

---

## 🔄 Atualização do Código

Após atualizar o código:

```bash
# Reinstalar dependências (se necessário)
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Reiniciar serviços
sudo systemctl restart fatigue-backend
sudo systemctl restart fatigue-detector
```

---

## ⚠️ Importante

- **VEHICLE_ID** deve ser um UUID válido de um veículo cadastrado
- Backend deve iniciar antes do detector
- PostgreSQL deve estar rodando
- Logs são importantes para debug
- Caminhos devem ser absolutos nos arquivos .service

---

## 📞 Comandos Úteis

```bash
# Ver todos os serviços do fatigue
systemctl list-units fatigue-*

# Reiniciar tudo
sudo systemctl restart fatigue-backend fatigue-detector

# Ver se há erros
sudo systemctl --failed | grep fatigue

# Limpar logs antigos
sudo journalctl --vacuum-time=7d
```

---

**Para mais informações, consulte:**
- `man systemctl`
- `man journalctl`
- `systemd.service(5)`

