import os
import sys
import subprocess

# --- FUNCIÓN DE AUTO-INSTALACIÓN ---
def install_dependencies():
    required = {'ultralytics', 'opencv-python', 'numpy'}
    installed = {pkg.split('==')[0].lower() for pkg in subprocess.check_output([sys.executable, '-m', 'pip', 'freeze']).decode().split()}
    missing = required - installed

    if missing:
        print(f"Instalando dependencias faltantes: {missing}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("Instalación completada. Iniciando sistema...")

# Ejecutar antes de importar el resto
install_dependencies()

import cv2
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

# --- CONFIGURACIÓN DE LA LÍNEA VERTICAL ---
linea_x = 320  # Mitad de una pantalla estándar de 640px
conteo_entran = 0
conteo_salen = 0
historial_posiciones = {} 

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    results = model.track(frame, persist=True, classes=[0], verbose=False)

    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        ids = results[0].boxes.id.int().cpu().tolist()

        for box, id in zip(boxes, ids):
            # Ahora calculamos el centro en X (Horizontal)
            centro_x = int((box[0] + box[2]) / 2)
            centro_y = int((box[1] + box[3]) / 2)

            if id in historial_posiciones:
                pos_anterior = historial_posiciones[id]

                # LÓGICA DE CRUCE HORIZONTAL (Izquierda a Derecha)
                # Si viene de la izquierda (< linea_x) y pasa a la derecha (> linea_x)
                if pos_anterior < linea_x and centro_x >= linea_x:
                    conteo_entran += 1
                
                # Si viene de la derecha (> linea_x) y pasa a la izquierda (< linea_x)
                elif pos_anterior > linea_x and centro_x <= linea_x:
                    conteo_salen += 1

            # Guardamos la posición X para el siguiente frame
            historial_posiciones[id] = centro_x

    # --- CÁLCULO DE AFORO SEGURO (Sin negativos) ---
    aforo_actual = max(0, conteo_entran - conteo_salen)

    # --- INTERFAZ VISUAL ---
    # Dibujar línea VERTICAL (de arriba a abajo)
    cv2.line(frame, (linea_x, 0), (linea_x, frame.shape[0]), (255, 0, 0), 2)
    
    # Marcador digital
    cv2.rectangle(frame, (10, 10), (220, 120), (0, 0, 0), -1)
    cv2.putText(frame, f"Entradas: {conteo_entran}", (20, 40), 2, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Salidas: {conteo_salen}", (20, 70), 2, 0.7, (0, 0, 255), 2)
    cv2.putText(frame, f"AFORO: {aforo_actual}", (20, 105), 2, 0.8, (255, 255, 255), 2)

    cv2.imshow("SIGAI - Conteo Vertical", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break

cap.release()
cv2.destroyAllWindows()

