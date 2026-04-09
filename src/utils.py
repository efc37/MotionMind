import cv2
import numpy as np

def contar_dedos_extendidos(puntos_mano):
    """
    Determina cuántos dedos están levantados comparando la posición vertical (y)
    de la punta del dedo con su articulación PIP (segunda articulación).
    En MediaPipe, el valor de 'y' disminuye al subir en la pantalla.
    """
    # Índices de MediaPipe: (Punta del dedo, Articulación PIP)
    pares_dedos = [(8, 6), (12, 10), (16, 14), (20, 18)]
    extendidos = 0
    
    for idx_punta, idx_pip in pares_dedos:
        punta = puntos_mano[idx_punta]
        pip = puntos_mano[idx_pip]
        # Si la punta está por encima de la articulación (y es menor), el dedo está extendido
        if punta.y < pip.y:
            extendidos += 1
    return extendidos

def calcular_puntos_tiempo(dt):
    """
    Calcula una bonificación de puntos basada en la rapidez de la respuesta.
    dt: Diferencia de tiempo (delta time) en segundos.
    """
    if dt <= 1.0: return 10
    elif dt <= 2.0: return 5
    elif dt <= 3.0: return 2
    else: return 0

def dibujar_circulos(frame, centro, radio, color, cantidad):
    """
    Dibuja un patrón de pequeños círculos dentro de un área para representar 
    una cantidad numérica de forma visual.
    """
    cx, cy = centro
    radio_mini = max(8, radio // 6) # Tamaño de los círculos pequeños
    desplazamiento = int(radio * 0.5) # Dispersión de los círculos
    posiciones = []
    
    # Genera una rejilla interna de 3x3 para posicionar los puntos
    for fila in [-1, 0, 1]:
        for col in [-1, 0, 1]:
            px = cx + int(col * desplazamiento / 1.5)
            py = cy + int(fila * desplazamiento / 1.5)
            posiciones.append((px, py))
            
    # Dibuja la cantidad solicitada usando las posiciones generadas
    for i in range(cantidad):
        if i >= len(posiciones): break
        x, y = posiciones[i]
        # Círculo relleno del color del nivel
        cv2.circle(frame, (x, y), radio_mini, color, -1)
        # Borde negro para mejor visibilidad
        cv2.circle(frame, (x, y), radio_mini, (0, 0, 0), 1)

def dibujar_cruz(frame, centro, radio):
    """
    Dibuja una 'X' de color rojo sobre un centro dado para indicar un error.
    """
    x, y = centro
    # Dibuja las dos líneas cruzadas
    cv2.line(frame, (x - radio//3, y - radio//3), (x + radio//3, y + radio//3), (0, 0, 255), 4)
    cv2.line(frame, (x - radio//3, y + radio//3), (x + radio//3, y - radio//3), (0, 0, 255), 4)

def escribir_centrado(frame, texto, y, escala, color, grosor=2):
    """
    Calcula el ancho del texto para dibujarlo exactamente en el centro horizontal.
    """
    fuente = cv2.FONT_HERSHEY_SIMPLEX
    h, w = frame.shape[:2]
    x_centro = w // 2
    # Obtiene las dimensiones del texto en píxeles
    (ancho_texto, alto_texto), _ = cv2.getTextSize(texto, fuente, escala, grosor)
    # Dibuja desplazando el inicio hacia la izquierda la mitad del ancho del texto
    cv2.putText(frame, texto, (x_centro - ancho_texto // 2, y), fuente, escala, color, grosor)

def escribir_centrado_clicable(frame, texto, y, escala, color, grosor, dic_rectangulos, clave):
    """
    Dibuja texto centrado y guarda sus coordenadas en un diccionario
    para que el sistema de gestión del ratón pueda detectar clics sobre él.
    """
    fuente = cv2.FONT_HERSHEY_SIMPLEX
    h, w = frame.shape[:2]
    x_centro = w // 2
    (ancho_texto, alto_texto), base = cv2.getTextSize(texto, fuente, escala, grosor)
    
    x = x_centro - ancho_texto // 2
    cv2.putText(frame, texto, (x, y), fuente, escala, color, grosor)
    
    # Define las coordenadas del rectángulo envolvente (Bounding Box)
    x1, y1 = x, y - alto_texto # Esquina superior izquierda
    x2, y2 = x + ancho_texto, y + base # Esquina inferior derecha
    
    # Almacena el área sensible para el callback del ratón
    dic_rectangulos[clave] = (x1, y1, x2, y2)