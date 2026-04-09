import cv2
import numpy as np
import random
import time
import sys
import os
import csv
import mediapipe as mp

# Importación de todas las constantes y utilidades desde el paquete 'src'
# Gracias al __init__.py, accedemos a config, funciones de dibujo y lógica.
from src import *

# --- CONFIGURACIÓN DE MEDIAPIPE (IA para detección de manos) ---
# Alias para las clases de MediaPipe para facilitar la lectura
BaseOptions = mp.tasks.BaseOptions
MarcadorManos = mp.tasks.vision.HandLandmarker
OpcionesMarcadorManos = mp.tasks.vision.HandLandmarkerOptions
ModoVision = mp.tasks.vision.RunningMode

# Definición de parámetros de la IA
opciones_mano = OpcionesMarcadorManos(
    # Ruta al archivo .task definido en config.py
    base_options=BaseOptions(model_asset_path=config.model_path),
    # Modo VIDEO para procesar frames de forma continua y temporal
    running_mode=ModoVision.VIDEO,
    # Capacidad de detectar hasta 2 manos simultáneamente
    num_hands=2
)

# --- RUTAS DE DATOS ---
# Establece la ruta absoluta para guardar los resultados de las partidas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_DATOS = os.path.join(BASE_DIR, "data", "datos_juego_serio.csv")

# --- INICIO DEL PROGRAMA PRINCIPAL ---
# Inicializamos el detector de manos con las opciones configuradas
with MarcadorManos.create_from_options(opciones_mano) as marcador_manos:
    # Captura de vídeo desde la cámara web (índice 0)
    cap = cv2.VideoCapture(0)
    # Ajuste de la resolución de cámara a HD (1280x720)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Cálculo de tiempos para sincronizar la IA con el vídeo
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0: fps = 30 # Valor por defecto si no se detecta el FPS de la cámara
    ms_por_frame = int(1000 / fps)
    timestamp = 0

    # --- FLUJO INICIAL: AUTENTICACIÓN ---
    # Llama al menú de Registro/Login antes de empezar el juego
    # Retorna el nombre del usuario logueado
    nombre_usuario, _ = menu_autenticacion(cap)

    # --- VARIABLES DE ESTADO Y PUNTUACIÓN ---
    puntuacion_base = 0      # Puntos por aciertos fijos
    puntuacion_tiempo = 0    # Puntos extra por velocidad (rapidez)

    # Gestión de rachas (combos)
    racha = 0                # Aciertos consecutivos actuales
    mejor_racha = 0          # Récord de racha en la sesión actual
    rachas = []              # Lista para guardar todas las rachas y calcular medias

    # Tiempos de control de juego
    inicio_secuencia = None  # Marca temporal de inicio de interacción
    ultimo_acierto = None    # Marca temporal del último acierto
    fin_juego = False        # Bandera para detener la lógica principal

    # Persistencia e histórico
    resultados_guardados = False
    num_sesiones = 0         # Veces que el usuario ha jugado antes
    mejor_puntuacion_hist = 0 # Récord histórico del usuario
    texto_evolucion = ""     # Mensaje comparativo (ej: "¡Has mejorado!")

    # --- VARIABLES DE INTERFAZ (UI) ---
    ultimo_evento_ui = 0.0      # Timestamp para controlar cuánto tiempo aparece un cartel
    SEGUNDOS_MOSTRAR_UI = 2.0   # Duración de las notificaciones visuales
    ultima_puntuacion_ui = 0    # Almacén temporal para mostrar puntos ganados
    ultima_racha_ui = 0         # Almacén temporal para mostrar racha alcanzada
# --- INICIALIZACIÓN DE LA LÓGICA DE NIVELES ---
    indice_nivel_actual = 0  # Controla el progreso: 0=Fácil, 1=Medio, 2=Difícil

    # Estado de la secuencia de memoria
    secuencia_generada = False
    secuencia_actual = []       # Lista de diccionarios con la posición, color y cantidad
    inicio_mostrado_secuencia = None
    esperando_usuario = False   # True cuando termina la muestra y el usuario debe actuar
    paso_actual = 0             # Índice del punto que el usuario debe tocar ahora
    aciertos = []               # Lista de puntos ya tocados correctamente
    indices_desactivados = set() # Evita que un punto ya acertado se procese de nuevo

    # Gestión de errores visuales
    ultimo_error = None         # Coordenadas (x, y) del último fallo para dibujar la cruz
    tiempo_ultimo_error = 0     # Timestamp para controlar cuánto tiempo se ve la cruz
    indice_ultimo_error = None

    # Estado de finalización del nivel
    nivel_completado = False
    tiempo_nivel_completado = None

    # --- BUCLE PRINCIPAL DE JUEGO ---
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # Espejo horizontal y obtención de dimensiones
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # --- PROCESAMIENTO DE IA (Mediapipe) ---
        # Convertimos a RGB ya que Mediapipe no usa el BGR de OpenCV
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagen_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        # Detección de manos vinculada al timestamp del video
        resultado = marcador_manos.detect_for_video(imagen_mp, timestamp)
        timestamp += ms_por_frame

        # --- CÁLCULO DE LA CUADRÍCULA (Geometría 3x4) ---
        # El radio se adapta dinámicamente al tamaño de la ventana
        radio = int(min(w / 16, h / 9))
        margen_x = int(w * 0.18)
        margen_y = int(h * 0.20)
        
        # Generamos 4 puntos en X y 3 en Y distribuidos uniformemente
        posiciones_x = np.linspace(margen_x, w - margen_x, 4, dtype=int)
        posiciones_y = np.linspace(margen_y, h - margen_y, 3, dtype=int)
        
        # Creamos la lista de centros de los 12 círculos (de izquierda a derecha, arriba a abajo)
        centros = [(x, y) for y in posiciones_y for x in posiciones_x]

        # Extraemos la configuración del nivel actual desde las constantes
        nombre_nivel, longitud_nivel, penalizacion_nivel, tiempo_mostrar = NIVELES[indice_nivel_actual]

        # --- GENERACIÓN DE LA SECUENCIA ALEATORIA ---
        if not secuencia_generada:
            # Seleccionamos N índices únicos de los 12 disponibles sin repetir
            indices_elegidos = random.sample(range(len(centros)), longitud_nivel)
            sec = []
            for i, indice_circulo in enumerate(indices_elegidos):
                color = COLORES_PUNTOS[i % len(COLORES_PUNTOS)]
                cantidad = i + 1 # El primer círculo tiene 1 punto, el segundo 2, etc.
                sec.append({"idx": indice_circulo, "color": color, "count": cantidad})
            
            secuencia_actual = sec
            inicio_mostrado_secuencia = time.time()
            secuencia_generada = True

        # --- DIBUJO DE LA ESTRUCTURA DE LA CUADRÍCULA ---
        # Dibujamos las líneas horizontales que conectan los círculos
        for y in posiciones_y:
            for i in range(len(posiciones_x) - 1):
                x1 = posiciones_x[i] + radio
                x2 = posiciones_x[i + 1] - radio
                cv2.line(frame, (x1, y), (x2, y), (200, 200, 200), 2)

        # Dibujamos las líneas verticales que conectan los círculos
        for x in posiciones_x:
            for j in range(len(posiciones_y) - 1):
                y1 = posiciones_y[j] + radio
                y2 = posiciones_y[j + 1] - radio
                cv2.line(frame, (x, y1), (x, y2), (200, 200, 200), 2)
   # --- RENDERIZADO DE LA CUADRÍCULA ---
        # Dibuja los 12 círculos base (negros) que sirven como marcos
        for (cx, cy) in centros:
            cv2.circle(frame, (cx, cy), radio, (0, 0, 0), 2)

        ahora = time.time()

        # Interfaz de usuario: Muestra el nombre del nivel en la esquina superior derecha
        cv2.putText(
            frame, f"Nivel: {nombre_nivel}", (w - 260, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2
        )

        # --- FASE 1: MEMORIZACIÓN (Mostrar secuencia) ---
        if not fin_juego and not nivel_completado:
            # Mientras estemos dentro del tiempo de visualización definido para el nivel
            if ahora - inicio_mostrado_secuencia <= tiempo_mostrar:
                for item in secuencia_actual:
                    idx, color, cantidad = item["idx"], item["color"], item["count"]
                    centro = centros[idx]
                    # Dibuja el patrón de puntos de color dentro del círculo correspondiente
                    dibujar_circulos(frame, centro, radio, color, cantidad)
            else:
                # Una vez pasado el tiempo, se activa la fase de interacción
                if not esperando_usuario:
                    esperando_usuario = True
                    inicio_secuencia = ahora
                    ultimo_acierto = ahora

        # --- FASE 2: INTERACCIÓN (Detección y validación) ---
        if (not fin_juego and not nivel_completado and esperando_usuario and resultado.hand_landmarks):
            seleccion_hecha = False

            # Procesamos cada mano detectada por la IA
            for puntos_mano in resultado.hand_landmarks:
                # Comprobamos si el usuario tiene la mano abierta (gesto para "pulsar")
                dedos_extendidos = contar_dedos_extendidos(puntos_mano)
                mano_abierta = (dedos_extendidos >= 4)

                # Usamos la punta del dedo índice (Landmark 8) como puntero
                punto_indice = puntos_mano[8]
                mano_x = int(punto_indice.x * w)
                mano_y = int(punto_indice.y * h)

                # Dibujo visual de los puntos (landmarks) y el esqueleto de la mano
                for punto in puntos_mano:
                    px, py = int(punto.x * w), int(punto.y * h)
                    cv2.circle(frame, (px, py), 5, (203, 192, 255), -1)

                for idx_inicio, idx_fin in CONEXIONES_MANO:
                    p1, p2 = puntos_mano[idx_inicio], puntos_mano[idx_fin]
                    cv2.line(frame, (int(p1.x * w), int(p1.y * h)), 
                             (int(p2.x * w), int(p2.y * h)), (220, 208, 255), 2)

                # --- LÓGICA DE COLISIÓN (Pulsación de círculos) ---
                if mano_abierta:
                    for idx_circulo, (cx, cy) in enumerate(centros):
                        # Ignoramos círculos que ya han sido acertados en este paso
                        if idx_circulo in indices_desactivados:
                            continue

                        # Cálculo de distancia euclidiana (¿Está el dedo dentro del círculo?)
                        dx = mano_x - cx
                        dy = mano_y - cy
                        if dx * dx + dy * dy <= radio * radio:
                            indice_esperado = secuencia_actual[paso_actual]["idx"]

                            # CASO A: ACIERTO (El círculo tocado es el correcto en la secuencia)
                            if idx_circulo == indice_esperado:
                                item_acertado = secuencia_actual[paso_actual]
                                aciertos.append(item_acertado)
                                indices_desactivados.add(idx_circulo)
                                paso_actual += 1

                                # Cálculo de bonificación por velocidad
                                dt = ahora - (ultimo_acierto if ultimo_acierto else inicio_secuencia)
                                ultimo_acierto = ahora
                                puntos_tiempo = calcular_puntos_tiempo(dt)

                                # Actualización de puntuación y racha
                                racha += 1
                                if racha > mejor_racha: mejor_racha = racha
                                
                                puntuacion_base += 10
                                puntuacion_tiempo += puntos_tiempo

                                # Marcamos el evento para actualizar la interfaz (UI)
                                ultimo_evento_ui = ahora
                                ultima_puntuacion_ui = puntuacion_base + puntuacion_tiempo
                                ultima_racha_ui = racha

                                # Si se han completado todos los pasos de la secuencia
                                if paso_actual >= len(secuencia_actual):
                                    esperando_usuario = False
                                    nivel_completado = True
                                    tiempo_nivel_completado = ahora

                            # CASO B: ERROR (Tocado círculo incorrecto)
                            else:
                                # Anti-rebote: evita penalizar múltiples veces el mismo error en 2 segundos
                                if (ultimo_error and indice_ultimo_error == idx_circulo and 
                                    ahora - tiempo_ultimo_error < 2.0):
                                    seleccion_hecha = True
                                    break

                                # Registramos el error y aplicamos penalización
                                ultimo_error = (cx, cy)
                                tiempo_ultimo_error = ahora
                                indice_ultimo_error = idx_circulo
                                puntuacion_base -= penalizacion_nivel

                                # Reseteo de racha
                                rachas.append(racha)
                                racha = 0

                                ultimo_evento_ui = ahora
                                ultima_puntuacion_ui = puntuacion_base + puntuacion_tiempo
                                ultima_racha_ui = racha

                            seleccion_hecha = True
                            break

                if seleccion_hecha or fin_juego:
                    break
# --- GESTIÓN DE TRANSICIÓN DE NIVELES ---
        # Si el usuario ha completado la secuencia actual
        if not fin_juego and nivel_completado:
            # Esperamos el tiempo de retardo definido en constantes para no saltar de golpe
            if ahora - tiempo_nivel_completado >= RETARDO_TRANSICION_NIVEL:
                # Si aún quedan niveles por jugar (Fácil -> Medio -> Difícil)
                if indice_nivel_actual < len(NIVELES) - 1:
                    indice_nivel_actual += 1

                    # --- RESETEO DE VARIABLES PARA EL NUEVO NIVEL ---
                    secuencia_generada = False
                    secuencia_actual = []
                    aciertos = []
                    indices_desactivados = set() # Volvemos a habilitar todos los círculos
                    paso_actual = 0
                    ultimo_error = None
                    tiempo_ultimo_error = 0
                    indice_ultimo_error = None
                    inicio_secuencia = None
                    ultimo_acierto = None
                    esperando_usuario = False
                    nivel_completado = False
                    tiempo_nivel_completado = None
                else:
                    # Si ya se completó el último nivel, activamos la bandera de fin de partida
                    fin_juego = True
                    nivel_completado = False
                    tiempo_nivel_completado = None

        # --- DIBUJO DE FEEDBACK VISUAL EN LA CUADRÍCULA ---
        
        # Mantener dibujados los círculos que el usuario ya ha acertado en el paso actual
        for acierto in aciertos:
            idx = acierto["idx"]
            color = acierto["color"]
            cantidad = acierto["count"]
            centro = centros[idx]
            dibujar_circulos(frame, centro, radio, color, cantidad)

        # Si hubo un error recientemente, dibujamos una cruz roja sobre el círculo equivocado
        # La cruz permanece visible durante 2 segundos para dar feedback al usuario
        if ultimo_error is not None and ahora - tiempo_ultimo_error < 2.0:
            dibujar_cruz(frame, ultimo_error, radio)

        # --- HUD (Heads-Up Display) / INTERFAZ DE USUARIO ---
        # Solo se muestra el score y la racha si ha habido un evento reciente (acierto o fallo)
        # Esto evita saturar la pantalla constantemente de información
        if not fin_juego and (ahora - ultimo_evento_ui) < SEGUNDOS_MOSTRAR_UI:
            y0 = 80
            # Dibujo de la puntuación acumulada
            cv2.putText(
                frame,
                f"Score: {ultima_puntuacion_ui}",
                (30, y0),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0), # Texto en negro
                2
            )
            # Dibujo de la racha (combo) actual
            cv2.putText(
                frame,
                f"Racha: {ultima_racha_ui}",
                (30, y0 + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 0),
                2
            )
# --- PANTALLA FINAL Y GESTIÓN DE RESULTADOS ---
        if fin_juego:
            # Cálculo de la puntuación total final
            total_score = puntuacion_base + puntuacion_tiempo

            # Bonificación extra por rachas (cada acierto en racha superior a 1 suma puntos extra)
            puntos_por_rachas = sum(r * 2 for r in rachas if r > 1)
            if racha > 1: 
                puntos_por_rachas += racha * 2
            total_score += puntos_por_rachas

            # --- GUARDADO DE DATOS (Solo se ejecuta una vez al terminar) ---
            if not resultados_guardados:
                # Comprobar si el archivo existe para escribir o no la cabecera
                existe_archivo = os.path.exists(ARCHIVO_DATOS)
                with open(ARCHIVO_DATOS, "a", newline="", encoding="utf-8") as f:
                    escritor = csv.writer(f)
                    if not existe_archivo:
                        # Encabezados del CSV
                        escritor.writerow(["nombre", "total_score", "score_time", "best_racha", "timestamp"])
                    
                    # Registro de la sesión actual
                    escritor.writerow([
                        nombre_usuario,
                        total_score,
                        puntuacion_tiempo,
                        mejor_racha,
                        time.strftime("%Y-%m-%d %H:%M:%S")
                    ])

                # --- ANÁLISIS DE EVOLUCIÓN HISTÓRICA ---
                puntuaciones_usuario = []
                try:
                    # Leemos el archivo para comparar con sesiones anteriores del mismo usuario
                    with open(ARCHIVO_DATOS, newline="", encoding="utf-8") as f:
                        lector = csv.DictReader(f)
                        for fila in lector:
                            if fila["nombre"] == nombre_usuario:
                                puntuaciones_usuario.append(float(fila["total_score"]))
                except FileNotFoundError:
                    pass

                num_sesiones = len(puntuaciones_usuario)
                
                # Lógica comparativa para el feedback motivacional
                if num_sesiones >= 2:
                    puntuacion_anterior = puntuaciones_usuario[-2] # Penúltima sesión
                    if total_score > puntuacion_anterior:
                        texto_evolucion = "Has mejorado respecto a tu ultima sesion. Buen trabajo!"
                    elif total_score < puntuacion_anterior:
                        texto_evolucion = "Hoy has bajado un poco, pero es parte del proceso. Sigue asi!"
                    else:
                        texto_evolucion = "Has mantenido la misma puntuacion que en la ultima sesion. Estabilidad"
                else:
                    texto_evolucion = "Esta es tu primera sesion registrada. A partir de aqui veremos tu evolucion."

                # Obtener el récord histórico del usuario
                mejor_puntuacion_hist = max(puntuaciones_usuario) if puntuaciones_usuario else total_score
                resultados_guardados = True

            # --- RENDERIZADO DE LA INTERFAZ DE FIN DE JUEGO ---
            # Crear un efecto de oscurecimiento (overlay) sobre el último frame de la cámara
            capa = frame.copy()
            cv2.rectangle(capa, (0, 0), (w, h), (0, 0, 0), -1)
            alpha = 0.7 # Nivel de transparencia
            frame = cv2.addWeighted(capa, alpha, frame, 1 - alpha, 0)

            # Preparación de textos informativos
            titulo_fin = f"Juego terminado - {nombre_usuario}"
            linea1 = f"Score base (incluye rachas y penalizaciones): {puntuacion_base + puntos_por_rachas}"
            linea2 = f"Puntos por rapidez: {puntuacion_tiempo}"
            linea3 = f"Total partida (3 niveles): {total_score}"
            linea4 = f"Mejor racha en esta sesion: {mejor_racha}"
            linea5 = f"Sesiones registradas: {num_sesiones} | Mejor total historico: {int(mejor_puntuacion_hist)}"
            linea6 = texto_evolucion
            pista_fin = "Pulsa ESC para salir"

            # Dibujado de todas las estadísticas centradas en pantalla
            escribir_centrado(frame, titulo_fin,  140, 1.3, (255, 255, 255), 3)
            escribir_centrado(frame, linea1,      215, 0.8, (255, 220, 220), 2)
            escribir_centrado(frame, linea2,      250, 0.8, (255, 220, 220), 2)
            escribir_centrado(frame, linea3,      285, 0.9, (255, 255, 255), 2)
            escribir_centrado(frame, linea4,      320, 0.8, (255, 255, 200), 2)
            escribir_centrado(frame, linea5,      355, 0.7, (220, 220, 220), 2)
            escribir_centrado(frame, linea6,      390, 0.7, (220, 220, 255), 2)
            escribir_centrado(frame, pista_fin,   430, 0.8, (200, 200, 200), 2)

        # Mostrar el frame resultante en la ventana
        cv2.imshow("Juego MotionMind", frame)
        
        # Salida limpia si se pulsa la tecla ESC (ASCII 27)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    # --- CIERRE DE RECURSOS ---
    cap.release() # Libera la cámara web
    cv2.destroyAllWindows() # Cierra todas las ventanas de OpenCV