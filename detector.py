#!/usr/bin/env python3
"""
Sistema de Detecção de Fadiga usando MediaPipe
Otimizado para Raspberry Pi 5 com Câmera CSI
"""

import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance as dist
import time
import subprocess
import threading
import warnings
import os
from picamera2 import Picamera2
import requests
from datetime import datetime
from pathlib import Path
import uuid
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Suprimir avisos de depreciação do MediaPipe
warnings.filterwarnings("ignore", category=UserWarning, module=".*protobuf.*")
warnings.filterwarnings("ignore", category=UserWarning, module=".*symbol_database.*")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suprimir avisos do TensorFlow

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

class Config:
    # Thresholds
    EAR_THRESHOLD = 0.25      # Eye Aspect Ratio
    EAR_CONSEC_FRAMES = 20    # ~0.67 segundos a 30fps
    MAR_THRESHOLD = 1.25      # Mouth Aspect Ratio (largura/altura - valor inicial)
    MAR_CONSEC_FRAMES = 10     # Bocejo detectado mais rapidamente (0.27s)
    
    # Câmera
    CAMERA_INDEX = 0          # Sua webcam USB
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    
    # Alerta sonoro
    ENABLE_SOUND = True
    ALERT_COOLDOWN = 3.0      # segundos entre alertas
    
    # Visual
    SHOW_LANDMARKS = True
    SHOW_FPS = True
    CALIBRATION_FRAMES = 30   # Frames para calibração inicial
    
    # Interface
    SHOW_INTERFACE = False    # Mostrar interface gráfica (desabilitado para headless)
    
    # Debug (desabilitar para produção)
    DEBUG_YAWN = False        # Logs detalhados de bocejo
    
    # API Backend
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
    VEHICLE_ID = os.getenv("VEHICLE_ID", None)  # UUID do veículo cadastrado
    ENABLE_API = True         # Ativar/desativar envio para API
    
    # Diretório de screenshots
    SCREENSHOTS_DIR = "../uploads"

# ============================================================================
# ÍNDICES DOS LANDMARKS DO MEDIAPIPE FACE MESH (468 pontos)
# ============================================================================

# Olho esquerdo (contorno completo - 16 pontos)
LEFT_EYE_CONTOUR = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]

# Olho direito (contorno completo - 16 pontos)
RIGHT_EYE_CONTOUR = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]

# Olho esquerdo (6 pontos para cálculo EAR)
LEFT_EYE = [33, 160, 158, 133, 153, 144]

# Olho direito (6 pontos para cálculo EAR)
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Lábios - contorno externo (20 pontos)
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

# Lábios - pontos internos para cálculo MAR (20 pontos)
LIPS_INNER = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]

# ============================================================================
# FUNÇÕES DE CÁLCULO
# ============================================================================

def eye_aspect_ratio(eye_landmarks):
    """
    Calcula Eye Aspect Ratio (EAR)
    eye_landmarks: lista de 6 pontos [(x,y), ...]
    """
    # Distâncias verticais
    A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
    B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
    
    # Distância horizontal
    C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
    
    # EAR = (A + B) / (2 * C)
    ear = (A + B) / (2.0 * C)
    return ear


def mouth_aspect_ratio(mouth_landmarks):
    """
    Calcula Mouth Aspect Ratio (MAR) para detectar bocejos
    mouth_landmarks: lista de 20 pontos dos lábios
    """
    if len(mouth_landmarks) < 20:
        return 0.0
    
    try:
        # Calcular distâncias verticais (altura da boca)
        # Pontos superiores e inferiores da boca
        A = dist.euclidean(mouth_landmarks[2], mouth_landmarks[10])   # Centro superior e inferior
        B = dist.euclidean(mouth_landmarks[3], mouth_landmarks[9])    # Esquerda superior e inferior
        C = dist.euclidean(mouth_landmarks[4], mouth_landmarks[8])    # Direita superior e inferior
        
        # Largura horizontal da boca
        D = dist.euclidean(mouth_landmarks[0], mouth_landmarks[6])    # Cantos esquerdo e direito
        
        # MAR = largura / média das alturas (invertido!)
        # Bocejo = boca mais larga = MAR mais alto
        mar = D / ((A + B + C) / 3.0) if (A + B + C) > 0 else 0.0
        
        return mar
    except:
        return 0.0

# ============================================================================
# CLIENTE API
# ============================================================================

class APIClient:
    """Cliente para enviar alertas ao backend"""
    
    def __init__(self, base_url: str, vehicle_id: str = None):
        self.base_url = base_url.rstrip("/")
        self.vehicle_id = vehicle_id
        self.enabled = vehicle_id is not None
        
        if not self.enabled:
            print("⚠️  API desabilitada: VEHICLE_ID não configurado")
        else:
            print(f"✅ API configurada: {self.base_url}")
            print(f"   Vehicle ID: {self.vehicle_id}")
    
    def send_alert(self, alert_data: dict, image_path: str = None) -> bool:
        """
        Envia alerta para o backend
        
        Args:
            alert_data: Dicionário com dados do alerta
            image_path: Caminho da imagem (opcional)
        
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.enabled:
            return False
        
        try:
            # Preparar dados do alerta
            payload = {
                "vehicle_id": self.vehicle_id,
                "timestamp": alert_data["timestamp"].isoformat(),
                "tipo": alert_data["tipo"],
                "severity": alert_data["severity"],
                "ear_value": alert_data["ear_value"],
                "mar_value": alert_data["mar_value"],
            }
            
            # Adicionar nome do arquivo de imagem se fornecido
            if image_path:
                payload["image_filename"] = Path(image_path).name
            
            # Enviar para API
            response = requests.post(
                f"{self.base_url}/api/alerts",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 201:
                print(f"✅ Alerta enviado ao backend com sucesso!")
                return True
            else:
                print(f"❌ Erro ao enviar alerta: HTTP {response.status_code}")
                print(f"   Resposta: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Erro: Não foi possível conectar ao backend em {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            print("❌ Erro: Timeout ao enviar alerta")
            return False
        except Exception as e:
            print(f"❌ Erro ao enviar alerta: {e}")
            return False

# ============================================================================
# SISTEMA DE ALERTA SONORO
# ============================================================================

class AlertSystem:
    """Sistema de alertas sonoros usando beep nativo do sistema"""
    
    @staticmethod
    def beep_simple():
        """Beep simples do sistema"""
        try:
            # Método 1: beep do sistema
            subprocess.run(['beep', '-f', '1000', '-l', '200'], 
                          stderr=subprocess.DEVNULL, timeout=1)
        except:
            try:
                # Método 2: speaker-test (mais compatível)
                subprocess.run(['speaker-test', '-t', 'sine', '-f', '1000', '-l', '1'],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
            except:
                # Método 3: fallback - print beep
                print('\a', end='', flush=True)
    
    @staticmethod
    def beep_critical():
        """Beep triplo para alerta crítico"""
        for _ in range(3):
            AlertSystem.beep_simple()
            time.sleep(0.1)
    
    @staticmethod
    def play_alert_async(level='moderate'):
        """Toca alerta em thread separada para não bloquear"""
        def play():
            if level == 'critical':
                AlertSystem.beep_critical()
            else:
                AlertSystem.beep_simple()
        
        thread = threading.Thread(target=play, daemon=True)
        thread.start()

# ============================================================================
# DETECTOR DE FADIGA
# ============================================================================

class FatigueDetector:
    def __init__(self, config):
        self.config = config
        
        # Inicializar MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.3,  # Reduzido para melhor detecção
            min_tracking_confidence=0.3
        )
        
        # Inicializar câmera CSI com Picamera2
        self.picam2 = Picamera2()
        camera_config = self.picam2.create_preview_configuration(
            main={"size": (self.config.CAMERA_WIDTH, self.config.CAMERA_HEIGHT), 
                  "format": "RGB888"}
        )
        self.picam2.configure(camera_config)
        self.picam2.start()
        
        # Aguardar câmera estabilizar
        print("Aguardando camera estabilizar...")
        time.sleep(2)
        
        self.cap = None  # Manter compatibilidade com código legado
        
        # Contadores
        self.ear_counter = 0
        self.mar_counter = 0
        self.total_blinks = 0
        self.last_alert_time = 0
        
        # Sistema de alerta
        self.alert_system = AlertSystem()
        
        # Cliente API
        self.api_client = None
        if self.config.ENABLE_API:
            self.api_client = APIClient(
                base_url=self.config.API_BASE_URL,
                vehicle_id=self.config.VEHICLE_ID
            )
        
        # Criar diretório de screenshots
        self.screenshots_dir = Path(__file__).parent / self.config.SCREENSHOTS_DIR
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Diretório de screenshots: {self.screenshots_dir}")
        
        # Calibração
        self.calibration_counter = 0
        self.is_calibrated = False
        self.baseline_mar = []  # Para aprender MAR normal do usuário
        
        # FPS
        self.fps = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
        
        # Detecção de rosto
        self.face_detected_counter = 0
        self.no_face_counter = 0
        self.first_face_detected = False
        
        # Filtro simples para evitar falsos positivos
        self.mar_previous = 0.0
        
        # Controle de janela
        self.window_created = False
    
    def get_landmark_coords(self, landmarks, indices, frame_width, frame_height):
        """Extrai coordenadas (x, y) dos landmarks"""
        coords = []
        for idx in indices:
            landmark = landmarks[idx]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            coords.append((x, y))
        return coords
    
    def is_mar_stable(self, mar):
        """Verifica se MAR está estável (mudança não muito brusca)"""
        if self.mar_previous == 0.0:
            self.mar_previous = mar
            return True
        
        # Se mudança for muito brusca (>30%), pode ser landmark instável
        change = abs(mar - self.mar_previous) / self.mar_previous
        is_stable = change < 0.3
        
        self.mar_previous = mar
        return is_stable
    
    def capture_screenshot(self, frame):
        """
        Captura screenshot do frame e salva no diretório de uploads
        
        Args:
            frame: Frame a ser salvo
            
        Returns:
            Caminho do arquivo salvo ou None se falhar
        """
        try:
            # Gerar nome único para o arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            random_id = str(uuid.uuid4())[:8]
            filename = f"alert_{timestamp}_{random_id}.jpg"
            filepath = self.screenshots_dir / filename
            
            # Salvar imagem
            cv2.imwrite(str(filepath), frame)
            
            print(f"📸 Screenshot salvo: {filename}")
            return str(filepath)
            
        except Exception as e:
            print(f"❌ Erro ao salvar screenshot: {e}")
            return None
    
    def process_frame(self, frame_rgb):
        """Processa um frame e retorna métricas"""
        # Frame vem em RGB da Picamera2 e já tem cores corretas
        # Para MediaPipe, usar RGB direto
        # Para visualização, usar RGB direto também
        
        results = self.face_mesh.process(frame_rgb)
        
        metrics = {
            'ear': 0.0,
            'mar': 0.0,
            'is_drowsy': False,
            'drowsy_type': None,
            'face_detected': False
        }
        
        if not results.multi_face_landmarks:
            return metrics, frame_rgb
        
        metrics['face_detected'] = True
        
        # Pegar primeira face
        face_landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = frame_rgb.shape
        
        # Extrair coordenadas dos olhos para cálculo EAR
        left_eye_coords = self.get_landmark_coords(face_landmarks, LEFT_EYE, w, h)
        right_eye_coords = self.get_landmark_coords(face_landmarks, RIGHT_EYE, w, h)
        
        # Extrair contornos completos dos olhos para visualização
        left_eye_contour = self.get_landmark_coords(face_landmarks, LEFT_EYE_CONTOUR, w, h)
        right_eye_contour = self.get_landmark_coords(face_landmarks, RIGHT_EYE_CONTOUR, w, h)
        
        # Calcular EAR
        left_ear = eye_aspect_ratio(left_eye_coords)
        right_ear = eye_aspect_ratio(right_eye_coords)
        ear = (left_ear + right_ear) / 2.0
        metrics['ear'] = ear
        
        # Detectar olhos fechados
        if ear < self.config.EAR_THRESHOLD:
            self.ear_counter += 1
        else:
            if self.ear_counter >= self.config.EAR_CONSEC_FRAMES:
                self.total_blinks += 1
            self.ear_counter = 0
        
        # Extrair coordenadas da boca para visualização e cálculo
        mouth_coords = self.get_landmark_coords(face_landmarks, LIPS_OUTER, w, h)
        
        # Calcular MAR
        mar = mouth_aspect_ratio(mouth_coords)
        metrics['mar'] = mar
        
        # Calibração inicial - aprender MAR normal
        if not self.is_calibrated:
            self.baseline_mar.append(mar)
            self.calibration_counter += 1
            
            if self.calibration_counter >= self.config.CALIBRATION_FRAMES:
                # Calcular MAR médio + margem
                avg_mar = np.mean(self.baseline_mar)
                std_mar = np.std(self.baseline_mar)
                max_mar = np.max(self.baseline_mar)
                min_mar = np.min(self.baseline_mar)
                
                # Threshold mais sensível: média + 0.8 * desvio padrão
                # Mas com limites mínimos e máximos razoáveis
                calculated_threshold = avg_mar + 0.8 * std_mar
                self.config.MAR_THRESHOLD = max(1.25, min(1.35, calculated_threshold))
                
                self.is_calibrated = True
                print(f"✅ Calibração completa!")
                print(f"   📊 Threshold de bocejo: {self.config.MAR_THRESHOLD:.3f}")
                print(f"   🎯 Sistema pronto para detecção!")
        
        # Detectar bocejo (só após calibração)
        if self.is_calibrated:
            # Filtro simples: só conta se MAR está estável (não mudou muito bruscamente)
            mar_stable = self.is_mar_stable(mar)
            
            if mar > self.config.MAR_THRESHOLD and mar_stable:
                self.mar_counter += 1
                if self.config.DEBUG_YAWN:
                    if self.mar_counter == 1:
                        print(f"[DEBUG] Iniciando bocejo - MAR: {mar:.3f} (threshold: {self.config.MAR_THRESHOLD:.3f})")
                    elif self.mar_counter % 5 == 0:
                        print(f"[DEBUG] Bocejo continuando - frames: {self.mar_counter}, MAR: {mar:.3f}")
            else:
                if self.mar_counter > 0:
                    if self.config.DEBUG_YAWN:
                        if not mar_stable:
                            print(f"[DEBUG] Bocejo ignorado - mudança brusca no MAR")
                        else:
                            print(f"[DEBUG] Bocejo interrompido - frames: {self.mar_counter}")
                self.mar_counter = 0
        
        # Determinar se está com fadiga
        if self.ear_counter >= self.config.EAR_CONSEC_FRAMES:
            metrics['is_drowsy'] = True
            metrics['drowsy_type'] = 'eyes_closed'
            metrics['severity'] = 'critical'
        elif self.mar_counter >= self.config.MAR_CONSEC_FRAMES:
            metrics['is_drowsy'] = True
            metrics['drowsy_type'] = 'yawning'
            metrics['severity'] = 'moderate'
        
        # Desenhar visualização (usando contornos completos)
        display_frame = self.draw_visualization(
            frame_rgb, left_eye_contour, right_eye_contour, mouth_coords, metrics
        )
        
        return metrics, display_frame
    
    def draw_visualization(self, frame, left_eye, right_eye, mouth, metrics):
        """Desenha informações no frame"""
        display = frame.copy()
        
        # Desenhar landmarks se habilitado
        if self.config.SHOW_LANDMARKS:
            # Cor dos olhos baseada em EAR
            eye_color = (0, 0, 255) if metrics['ear'] < self.config.EAR_THRESHOLD else (0, 255, 0)
            
            # Desenhar contorno do olho esquerdo
            pts = np.array(left_eye, dtype=np.int32)
            cv2.polylines(display, [pts], True, eye_color, 2)
            
            # Desenhar contorno do olho direito
            pts = np.array(right_eye, dtype=np.int32)
            cv2.polylines(display, [pts], True, eye_color, 2)
            
            # Cor da boca baseada em MAR
            mouth_color = (0, 0, 255) if metrics['mar'] > self.config.MAR_THRESHOLD else (0, 255, 0)
            
            # Desenhar contorno da boca
            pts = np.array(mouth, dtype=np.int32)
            cv2.polylines(display, [pts], True, mouth_color, 2)
        
        # Informações de texto
        y_offset = 30
        
        # Calibração
        if not self.is_calibrated:
            calib_text = f"Calibrando... {self.calibration_counter}/{self.config.CALIBRATION_FRAMES}"
            cv2.putText(display, calib_text, 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y_offset += 30
        
        # EAR
        ear_color = (0, 0, 255) if metrics['ear'] < self.config.EAR_THRESHOLD else (0, 255, 0)
        cv2.putText(display, f"EAR: {metrics['ear']:.3f}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, ear_color, 2)
        y_offset += 30
        
        # MAR
        mar_color = (0, 0, 255) if metrics['mar'] > self.config.MAR_THRESHOLD else (0, 255, 0)
        cv2.putText(display, f"MAR: {metrics['mar']:.3f}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, mar_color, 2)
        y_offset += 30
        
        # Piscadas
        cv2.putText(display, f"Piscadas: {self.total_blinks}", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        y_offset += 30
        
        # FPS
        if self.config.SHOW_FPS:
            cv2.putText(display, f"FPS: {self.fps}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            y_offset += 30
        
        # Contadores ativos
        if self.ear_counter > 0:
            cv2.putText(display, f"Olhos fechados: {self.ear_counter} frames", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            y_offset += 25
        
        if self.mar_counter > 0:
            cv2.putText(display, f"Bocejando: {self.mar_counter}/{self.config.MAR_CONSEC_FRAMES} frames", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
            y_offset += 25
        
        # Status de calibração
        if not self.is_calibrated:
            cv2.putText(display, f"Calibrando boca: {len(self.baseline_mar)}/{self.config.CALIBRATION_FRAMES}", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        # ALERTA DE FADIGA
        if metrics['is_drowsy']:
            # Banner vermelho
            cv2.rectangle(display, (0, display.shape[0]-80), 
                         (display.shape[1], display.shape[0]), (0, 0, 255), -1)
            
            alert_text = "!!! FADIGA DETECTADA !!!"
            if metrics['drowsy_type'] == 'eyes_closed':
                detail = "Olhos fechados"
            else:
                detail = "Bocejando"
            
            cv2.putText(display, alert_text, 
                       (50, display.shape[0]-45), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 3)
            cv2.putText(display, detail, 
                       (200, display.shape[0]-15), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Alerta no console e sonoro
            current_time = time.time()
            if current_time - self.last_alert_time > self.config.ALERT_COOLDOWN:
                alert_icon = "🚨" if metrics.get('severity') == 'critical' else "⚠️"
                print(f"\n{alert_icon} ALERTA DE FADIGA DETECTADO!")
                print(f"   Tipo: {detail}")
                print(f"   EAR: {metrics['ear']:.3f} | MAR: {metrics['mar']:.3f}")
                print(f"   Ação: Descanse ou pare o veículo!")
                
                # Capturar screenshot
                screenshot_path = self.capture_screenshot(frame)
                
                # Enviar ao backend se API estiver habilitada
                if self.api_client and self.api_client.enabled:
                    alert_data = {
                        "timestamp": datetime.now(),
                        "tipo": "eyes_closed" if metrics['drowsy_type'] == 'eyes_closed' else "yawning",
                        "severity": "critical" if metrics.get('severity') == 'critical' else "moderate",
                        "ear_value": float(metrics['ear']),
                        "mar_value": float(metrics['mar']),
                    }
                    
                    # Enviar em thread separada para não bloquear
                    def send_async():
                        self.api_client.send_alert(alert_data, screenshot_path)
                    
                    thread = threading.Thread(target=send_async, daemon=True)
                    thread.start()
                
                # Tocar som se habilitado
                if self.config.ENABLE_SOUND:
                    severity = metrics.get('severity', 'moderate')
                    self.alert_system.play_alert_async(severity)
                
                self.last_alert_time = current_time
        
        return display
    
    def run(self):
        """Loop principal"""
        print("\n" + "="*70)
        print("🚗 SISTEMA DE DETECÇÃO DE FADIGA - MVP")
        print("="*70)
        print("📷 Câmera: CSI (Raspberry Pi)")
        print("🔊 Alerta sonoro: Ativado")
        print("\n🎯 Calibração automática em andamento...")
        print("   Mantenha expressão neutra por 1 segundo")
        print("\n📊 Configurações de Detecção:")
        print(f"   • Olhos fechados: {self.config.EAR_CONSEC_FRAMES/30.0:.1f}s para alerta")
        print(f"   • Bocejo: {self.config.MAR_CONSEC_FRAMES/30.0:.1f}s para alerta")
        print("\n⌨️  Controles:")
        print("   • 'q' - Sair")
        print("   • 'r' - Resetar sistema")
        print("   • 'c' - Recalibrar")
        print("   • 's' - Ligar/Desligar som")
        print("="*70 + "\n")
        
        try:
            while True:
                # Capturar frame da Picamera2 (vem em RGB888)
                frame_rgb = self.picam2.capture_array()
                
                if frame_rgb is None:
                    print("[ERRO] Falha ao capturar frame da camera")
                    break
                
                # Processar frame
                metrics, display_frame = self.process_frame(frame_rgb)
                
                # Monitorar detecção de rosto
                if metrics['face_detected']:
                    if not self.first_face_detected:
                        print("\n" + "="*50)
                        print("👤 ROSTO DETECTADO! Sistema ativo.")
                        print("="*50 + "\n")
                        self.first_face_detected = True
                    
                    self.face_detected_counter += 1
                    if self.no_face_counter >= 30:
                        print(f"[OK] Rosto detectado novamente!")
                    self.no_face_counter = 0
                else:
                    self.no_face_counter += 1
                    if self.no_face_counter == 30:  # 1 segundo sem detecção
                        print("⚠️  Nenhum rosto detectado. Posicione-se na frente da câmera.")
                    elif self.no_face_counter % 150 == 0:  # A cada 5 segundos
                        print(f"⚠️  Ainda sem detecção de rosto... ({self.no_face_counter/30:.0f}s)")
                
                # Mostrar interface
                if self.config.SHOW_INTERFACE:
                    if not self.window_created:
                        cv2.namedWindow('Sistema de Detecção de Fadiga', cv2.WINDOW_AUTOSIZE)
                        self.window_created = True
                    cv2.imshow('Sistema de Detecção de Fadiga', display_frame)
                
                # Calcular FPS
                self.fps_counter += 1
                if time.time() - self.fps_start_time >= 1.0:
                    self.fps = self.fps_counter
                    self.fps_counter = 0
                    self.fps_start_time = time.time()
                
                # Controles de teclado
                if self.config.SHOW_INTERFACE:
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                    elif key == ord('r'):
                        self.ear_counter = 0
                        self.mar_counter = 0
                        self.total_blinks = 0
                        self.is_calibrated = False
                        self.calibration_counter = 0
                        self.baseline_mar = []
                        print("🔄 Sistema resetado - Recalibrando...")
                    elif key == ord('s'):
                        self.config.ENABLE_SOUND = not self.config.ENABLE_SOUND
                        status = "Ativado" if self.config.ENABLE_SOUND else "Desativado"
                        print(f"🔊 Alerta sonoro: {status}")
                    elif key == ord('l'):
                        self.config.SHOW_LANDMARKS = not self.config.SHOW_LANDMARKS
                        status = "Ativado" if self.config.SHOW_LANDMARKS else "Desativado"
                        print(f"👁️  Visualização de landmarks: {status}")
                    elif key == ord('c'):
                        # Recalibrar sistema
                        self.is_calibrated = False
                        self.calibration_counter = 0
                        self.baseline_mar = []
                        self.ear_counter = 0
                        self.mar_counter = 0
                        print("🔄 Sistema recalibrado! Mantenha expressão neutra...")
        
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpar recursos"""
        print("\n🛑 Encerrando sistema...")
        if self.picam2:
            self.picam2.stop()
        cv2.destroyAllWindows()
        print("✅ Sistema encerrado com sucesso")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    config = Config()
    detector = FatigueDetector(config)
    detector.run()

