# 🎯 Sistema de Detecção de Fadiga com MediaPipe

Sistema avançado de detecção de fadiga em tempo real usando MediaPipe Face Mesh, otimizado para Raspberry Pi 5.

## 📋 Características

- ✅ Detecção de olhos fechados (EAR - Eye Aspect Ratio)
- ✅ Detecção de bocejos (MAR - Mouth Aspect Ratio)
- ✅ Calibração automática personalizada
- ✅ Alertas visuais e sonoros
- ✅ Contornos precisos dos landmarks
- ✅ Log limpo sem avisos de depreciação
- ✅ Interface em tempo real com métricas

## 📁 Arquivos do Projeto

```
testCam/
├── detector.py              # Detector principal de fadiga
├── test_landmarks.py        # Ferramenta de teste de landmarks
├── run_detector.sh          # Script para executar o detector
├── run_test_landmarks.sh    # Script para teste de landmarks
├── install_dependencies.sh  # Script de instalação automática
├── requirements.txt         # Dependências do projeto
├── GUIA_RAPIDO.txt         # Guia rápido de uso
└── README.md               # Este arquivo
```

## 📦 Instalação

### Método 1: Script Automático (Recomendado)

```bash
# Executar script de instalação
./install_dependencies.sh
```

### Método 2: Manual

```bash
# Criar ambiente virtual
python3 -m venv .v

# Ativar ambiente virtual
source .v/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Dependências Necessárias:
- `opencv-python` - Processamento de imagem e vídeo
- `mediapipe` - Detecção de landmarks faciais
- `numpy` - Computação numérica
- `scipy` - Cálculos científicos (distâncias)
- `protobuf` - Compatibilidade com MediaPipe

## 🚀 Início Rápido

### 1. Executar o Detector

```bash
# Opção 1: Script automático (recomendado)
./run_detector.sh

# Opção 2: Manual
source .v/bin/activate
python3 detector.py
```

### 2. Testar Landmarks

```bash
# Opção 1: Script automático
./run_test_landmarks.sh

# Opção 2: Manual
source .v/bin/activate
python3 test_landmarks.py
```

## ⏱️ Tempos de Detecção

| Evento | Frames | Tempo | Como Testar |
|--------|--------|-------|-------------|
| **Bocejo** | 15 | 0.50s | Manter boca aberta por meio segundo |
| **Olhos fechados** | 20 | 0.67s | Manter olhos fechados por 0.67s |
| **Calibração** | 30 | 1.0s | Expressão neutra no início |

## 🎮 Controles

Durante a execução do detector:

| Tecla | Ação |
|-------|------|
| `q` | Sair do programa |
| `r` | Resetar contadores e recalibrar |
| `s` | Ligar/desligar alerta sonoro |
| `l` | Ligar/desligar visualização dos landmarks |

Durante o teste de landmarks:

| Tecla | Ação |
|-------|------|
| `q` | Sair |
| `a` | Mostrar todos os 468 landmarks |
| `n` | Ligar/desligar números dos landmarks |

## 🔧 Configuração

Edite `detector.py` (linhas 28-31) para ajustar a sensibilidade:

```python
class Config:
    # Thresholds
    EAR_THRESHOLD = 0.25      # Menor = mais sensível para olhos
    EAR_CONSEC_FRAMES = 20    # Menos frames = detecta mais rápido
    
    MAR_THRESHOLD = 0.75      # Menor = mais sensível para bocejo
    MAR_CONSEC_FRAMES = 15    # Menos frames = detecta mais rápido
    
    # Câmera
    CAMERA_INDEX = 8          # Índice da sua webcam
```

### Exemplos de Sensibilidade

**Mais sensível (detecta mais facilmente):**
```python
MAR_THRESHOLD = 0.60
MAR_CONSEC_FRAMES = 10
```

**Menos sensível (evita falsos positivos):**
```python
MAR_THRESHOLD = 0.90
MAR_CONSEC_FRAMES = 25
```

## 📊 Métricas Exibidas

### No Vídeo:
- **EAR** (Eye Aspect Ratio) - Verde: normal, Vermelho: olhos fechados
- **MAR** (Mouth Aspect Ratio) - Verde: normal, Vermelho: bocejando
- **Piscadas** - Contador total de piscadas
- **FPS** - Taxa de quadros por segundo
- **Contadores** - Frames consecutivos de olhos fechados/bocejo

### No Console:
- `[OK]` - Operação bem-sucedida
- `[ERRO]` - Erro no sistema
- `[!!! ALERTA !!!]` - Fadiga detectada

## 🎨 Visualização

- **Verde**: Estado normal
- **Vermelho**: Alerta de fadiga
- **Banner vermelho inferior**: Alerta ativo com descrição

## 🧪 Processo de Calibração

1. **Inicialização**: Ao iniciar, o sistema entra em modo de calibração
2. **Duração**: 1 segundo (30 frames a 30 FPS)
3. **Instruções**: Mantenha expressão facial neutra
4. **Resultado**: Sistema aprende seu MAR normal e ajusta automaticamente

## 📝 Logs Limpos

O sistema suprime automaticamente:
- Avisos de depreciação do Protocol Buffers
- Avisos do Symbol Database
- Logs verbosos do TensorFlow

## 🔍 Landmarks do MediaPipe

O sistema usa landmarks específicos do MediaPipe Face Mesh (468 pontos):

- **Olho esquerdo**: 16 pontos do contorno
- **Olho direito**: 16 pontos do contorno
- **Boca**: 20 pontos do contorno externo

Use `test_landmarks.py` para visualizar e verificar os pontos.

## 🛠️ Dependências

```bash
pip install opencv-python mediapipe numpy scipy
```

## 💡 Dicas de Uso

1. **Iluminação**: Mantenha boa iluminação facial
2. **Calibração**: Refaça a calibração (tecla `r`) se mudar de ambiente
3. **Óculos**: O sistema funciona com óculos, mas pode precisar ajuste
4. **Posição**: Mantenha o rosto centralizado na câmera
5. **Distância**: Fique a aproximadamente 50-70cm da câmera

## 🐛 Solução de Problemas

### Câmera não abre
```bash
# Verificar dispositivos de vídeo disponíveis
ls -la /dev/video*

# Ajustar CAMERA_INDEX no arquivo Config
```

### Muitos falsos positivos
```bash
# Aumentar thresholds e frames necessários
EAR_THRESHOLD = 0.20  # Mais baixo
MAR_THRESHOLD = 0.85  # Mais alto
MAR_CONSEC_FRAMES = 20  # Mais frames
```

### Não detecta fadiga
```bash
# Diminuir thresholds e frames necessários
EAR_THRESHOLD = 0.28  # Mais alto
MAR_THRESHOLD = 0.65  # Mais baixo
MAR_CONSEC_FRAMES = 10  # Menos frames
```

## 📄 Licença

Este projeto foi desenvolvido para fins educacionais e de pesquisa.

## 🤝 Contribuindo

Para melhorias ou correções, sinta-se à vontade para modificar o código conforme necessário.

---

**Desenvolvido com MediaPipe e OpenCV**
**Otimizado para Raspberry Pi 5**

