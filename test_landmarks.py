#!/usr/bin/env python3
"""
Script de teste para visualizar landmarks do MediaPipe Face Mesh
Útil para verificar se os índices dos landmarks estão corretos
"""

import cv2
import mediapipe as mp
import numpy as np
import warnings
import os

# Suprimir avisos de depreciação do MediaPipe
warnings.filterwarnings("ignore", category=UserWarning, module=".*protobuf.*")
warnings.filterwarnings("ignore", category=UserWarning, module=".*symbol_database.*")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suprimir avisos do TensorFlow

# Configurações
CAMERA_INDEX = 8
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Landmarks para destacar
LEFT_EYE_CONTOUR = [33, 246, 161, 160, 159, 158, 157, 173, 133, 155, 154, 153, 145, 144, 163, 7]
RIGHT_EYE_CONTOUR = [362, 398, 384, 385, 386, 387, 388, 466, 263, 249, 390, 373, 374, 380, 381, 382]
LIPS_OUTER = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146]

def main():
    # Inicializar MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Inicializar câmera
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    
    show_all_landmarks = False
    show_numbers = True
    
    print("\n" + "="*60)
    print("Visualizador de Landmarks - MediaPipe Face Mesh")
    print("="*60)
    print("\nControles:")
    print("  'q' - Sair")
    print("  'a' - Toggle todos os 468 landmarks")
    print("  'n' - Toggle numeros dos landmarks")
    print("="*60 + "\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERRO] Falha ao capturar frame da camera")
            break
        
        # Processar frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)
        
        display = frame.copy()
        
        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark
            h, w, _ = frame.shape
            
            if show_all_landmarks:
                # Desenhar todos os 468 landmarks
                for idx, landmark in enumerate(face_landmarks):
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    
                    # Destacar os landmarks de interesse
                    if idx in LEFT_EYE_CONTOUR or idx in RIGHT_EYE_CONTOUR:
                        color = (0, 255, 0)  # Verde para olhos
                        radius = 3
                    elif idx in LIPS_OUTER:
                        color = (255, 0, 0)  # Azul para boca
                        radius = 3
                    else:
                        color = (128, 128, 128)  # Cinza para outros
                        radius = 1
                    
                    cv2.circle(display, (x, y), radius, color, -1)
                    
                    # Mostrar número se habilitado
                    if show_numbers and (idx in LEFT_EYE_CONTOUR or idx in RIGHT_EYE_CONTOUR or idx in LIPS_OUTER):
                        cv2.putText(display, str(idx), (x + 5, y - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
            else:
                # Desenhar apenas os contornos de interesse
                # Olho esquerdo
                for idx in LEFT_EYE_CONTOUR:
                    landmark = face_landmarks[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(display, (x, y), 3, (0, 255, 0), -1)
                    if show_numbers:
                        cv2.putText(display, str(idx), (x + 5, y - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                
                # Desenhar linha conectando os pontos do olho esquerdo
                left_eye_pts = [(int(face_landmarks[idx].x * w), int(face_landmarks[idx].y * h)) 
                               for idx in LEFT_EYE_CONTOUR]
                pts = np.array(left_eye_pts, dtype=np.int32)
                cv2.polylines(display, [pts], True, (0, 255, 0), 2)
                
                # Olho direito
                for idx in RIGHT_EYE_CONTOUR:
                    landmark = face_landmarks[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(display, (x, y), 3, (0, 255, 0), -1)
                    if show_numbers:
                        cv2.putText(display, str(idx), (x + 5, y - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                
                # Desenhar linha conectando os pontos do olho direito
                right_eye_pts = [(int(face_landmarks[idx].x * w), int(face_landmarks[idx].y * h)) 
                                for idx in RIGHT_EYE_CONTOUR]
                pts = np.array(right_eye_pts, dtype=np.int32)
                cv2.polylines(display, [pts], True, (0, 255, 0), 2)
                
                # Boca
                for idx in LIPS_OUTER:
                    landmark = face_landmarks[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(display, (x, y), 3, (255, 0, 0), -1)
                    if show_numbers:
                        cv2.putText(display, str(idx), (x + 5, y - 5),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)
                
                # Desenhar linha conectando os pontos da boca
                mouth_pts = [(int(face_landmarks[idx].x * w), int(face_landmarks[idx].y * h)) 
                            for idx in LIPS_OUTER]
                pts = np.array(mouth_pts, dtype=np.int32)
                cv2.polylines(display, [pts], True, (255, 0, 0), 2)
            
            # Informações
            mode = "Todos os landmarks" if show_all_landmarks else "Olhos e Boca"
            cv2.putText(display, f"Modo: {mode}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.putText(display, f"Números: {'ON' if show_numbers else 'OFF'}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        cv2.imshow('Teste de Landmarks', display)
        
        # Controles
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('a'):
            show_all_landmarks = not show_all_landmarks
            print(f"[OK] Mostrar todos landmarks: {'Sim' if show_all_landmarks else 'Nao'}")
        elif key == ord('n'):
            show_numbers = not show_numbers
            print(f"[OK] Mostrar numeros: {'Sim' if show_numbers else 'Nao'}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("[OK] Encerrado com sucesso")

if __name__ == "__main__":
    main()

