# --- CONFIGURACIÓN ESTÁTICA DEL JUEGO ---

# Lista de colores en formato BGR (Blue, Green, Red) para los puntos
# Se utilizan para diferenciar visualmente los elementos en la cuadrícula
COLORES_PUNTOS = [
    (180, 105, 255), (220, 170, 255), (60, 0, 139), 
    (180, 50, 130), (255, 220, 150), (180, 255, 200), (255, 255, 180)
]

# Definición de la progresión del juego
# Estructura: (Nombre del Nivel, Cantidad de puntos a memorizar, Penalización por error, Tiempo de visualización)
NIVELES = [
    ("Facil",   3, 8, 3.0),
    ("Medio",   6, 5, 5.0),
    ("Dificil", 8, 1, 10.0)
]

# Tiempo de espera (en segundos) entre la finalización de un nivel y el comienzo del siguiente
RETARDO_TRANSICION_NIVEL = 1.5

# Estructura del esqueleto de la mano para MediaPipe
# Define qué puntos (landmarks) deben conectarse con líneas para dibujar la mano en pantalla
# Ejemplo: (0, 1) conecta la muñeca con la base del pulgar
CONEXIONES_MANO = [
    (0, 1), (1, 2), (2, 3), (3, 4),           # Pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),           # Índice
    (0, 9), (9, 10), (10, 11), (11, 12),      # Medio
    (0, 13), (13, 14), (14, 15), (15, 16),    # Anular
    (0, 17), (17, 18), (18, 19), (19, 20)     # Meñique
]