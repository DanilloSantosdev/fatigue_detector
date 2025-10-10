#!/usr/bin/env python3
"""
Sistema de Detecção de Fadiga usando MediaPipe
Otimizado para Raspberry Pi 5
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
    MAR_THRESHOLD = 0.75      # Mouth Aspect Ratio (aumentado para evitar falsos positivos)
    MAR_CONSEC_FRAMES = 15    # Bocejo precisa ser mais prolongado
    
    # Câmera
    CAMERA_INDEX = 8          # Sua webcam USB
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    
    # Alerta sonoro
    ENABLE_SOUND = True
    ALERT_COOLDOWN = 3.0      # segundos entre alertas
    
    # Visual
    SHOW_LANDMARKS = True
    SHOW_FPS = True
    CALIBRATION_FRAMES = 30   # Frames para calibração inicial

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
    
    # Calcular distâncias verticais (altura da boca)
    # Pontos superiores e inferiores da boca
    A = dist.euclidean(mouth_landmarks[2], mouth_landmarks[10])   # Centro superior e inferior
    B = dist.euclidean(mouth_landmarks[3], mouth_landmarks[9])    # Esquerda superior e inferior
    C = dist.euclidean(mouth_landmarks[4], mouth_landmarks[8])    # Direita superior e inferior
    
    # Largura horizontal da boca
    D = dist.euclidean(mouth_landmarks[0], mouth_landmarks[6])    # Cantos esquerdo e direito
    
    # MAR = média das alturas / largura
    mar = (A + B + C) / (3.0 * D) if D > 0 else 0.0
    
    return mar

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
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Inicializar câmera
        self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Contadores
        self.ear_counter = 0
        self.mar_counter = 0
        self.total_blinks = 0
        self.last_alert_time = 0
        
        # Sistema de alerta
        self.alert_system = AlertSystem()
        
        # Calibração
        self.calibration_counter = 0
        self.is_calibrated = False
        self.baseline_mar = []  # Para aprender MAR normal do usuário
        
        # FPS
        self.fps = 0
        self.fps_counter = 0
        self.fps_start_time = time.time()
    
    def get_landmark_coords(self, landmarks, indices, frame_width, frame_height):
        """Extrai coordenadas (x, y) dos landmarks"""
        coords = []
        for idx in indices:
            landmark = landmarks[idx]
            x = int(landmark.x * frame_width)
            y = int(landmark.y * frame_height)
            coords.append((x, y))
        return coords
    
    def process_frame(self, frame):
        """Processa um frame e retorna métricas"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)
        
        metrics = {
            'ear': 0.0,
            'mar': 0.0,
            'is_drowsy': False,
            'drowsy_type': None
        }
        
        if not results.multi_face_landmarks:
            return metrics, frame
        
        # Pegar primeira face
        face_landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = frame.shape
        
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
                self.config.MAR_THRESHOLD = max(0.65, avg_mar + 0.15)
                self.is_calibrated = True
                print(f"[OK] Calibracao completa! MAR threshold ajustado para: {self.config.MAR_THRESHOLD:.3f}")
        
        # Detectar bocejo (só após calibração)
        if self.is_calibrated and mar > self.config.MAR_THRESHOLD:
            self.mar_counter += 1
        else:
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
            frame, left_eye_contour, right_eye_contour, mouth_coords, metrics
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
            cv2.putText(display, f"Bocejando: {self.mar_counter} frames", 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
        
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
                print(f"\n[!!! ALERTA !!!] {detail} - EAR: {metrics['ear']:.3f}, MAR: {metrics['mar']:.3f}")
                
                # Tocar som se habilitado
                if self.config.ENABLE_SOUND:
                    severity = metrics.get('severity', 'moderate')
                    self.alert_system.play_alert_async(severity)
                
                self.last_alert_time = current_time
        
        return display
    
    def run(self):
        """Loop principal"""
        if not self.cap.isOpened():
            print("[ERRO] Nao foi possivel abrir a camera!")
            return
        
        print("\n" + "="*60)
        print("Sistema de Deteccao de Fadiga - MediaPipe")
        print("="*60)
        print(f"Camera: /dev/video{self.config.CAMERA_INDEX}")
        print(f"Alerta sonoro: {'Ativado' if self.config.ENABLE_SOUND else 'Desativado'}")
        print("\nCalibracao inicial: Mantenha expressao neutra por 1 segundo")
        print("\n--- Configuracoes de Deteccao ---")
        print(f"  Tempo para detectar olhos fechados: {self.config.EAR_CONSEC_FRAMES/30.0:.2f} segundos")
        print(f"  Tempo para detectar bocejo: {self.config.MAR_CONSEC_FRAMES/30.0:.2f} segundos")
        print("\nControles:")
        print("  'q' - Sair")
        print("  'r' - Resetar contadores")
        print("  's' - Toggle som")
        print("  'l' - Toggle landmarks")
        print("="*60 + "\n")
        
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("[ERRO] Falha ao capturar frame da camera")
                    break
                
                # Processar frame
                metrics, display_frame = self.process_frame(frame)
                
                # Mostrar
                cv2.imshow('Detector de Fadiga', display_frame)
                
                # Calcular FPS
                self.fps_counter += 1
                if time.time() - self.fps_start_time >= 1.0:
                    self.fps = self.fps_counter
                    self.fps_counter = 0
                    self.fps_start_time = time.time()
                
                # Controles de teclado
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
                    print("[OK] Sistema resetado - Recalibrando...")
                elif key == ord('s'):
                    self.config.ENABLE_SOUND = not self.config.ENABLE_SOUND
                    status = "Ativado" if self.config.ENABLE_SOUND else "Desativado"
                    print(f"[OK] Alerta sonoro: {status}")
                elif key == ord('l'):
                    self.config.SHOW_LANDMARKS = not self.config.SHOW_LANDMARKS
                    status = "Ativado" if self.config.SHOW_LANDMARKS else "Desativado"
                    print(f"[OK] Visualizacao de landmarks: {status}")
        
        except KeyboardInterrupt:
            print("\n\nInterrompido pelo usuário")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Limpar recursos"""
        print("\nEncerrando...")
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[OK] Sistema encerrado com sucesso")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    config = Config()
    detector = FatigueDetector(config)
    detector.run()

