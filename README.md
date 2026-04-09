# MotionMind

## Objetivo del Proyecto

**MotionMind** es un juego serio diseñado para la **rehabilitación y fortalecimiento de los brazos** mediante ejercicios interactivos. Combina tecnología de visión por computadora con gamificación para hacer que el proceso de recuperación sea motivador, divertido y efectivo.

### ¿Por qué MotionMind?

La rehabilitación de brazos puede ser tediosa y poco motivadora. MotionMind transforma este proceso en una experiencia interactiva donde:
- Los usuarios mejoran coordinación y alcance de movimiento
- Se proporcionan desafíos progresivos (3 niveles de dificultad)
- Se registra el progreso para seguimiento médico
- Se ofrece feedback visual e inmediato

---

## Cómo Funciona el Juego

### Mecánica Principal

El juego presenta una **cuadrícula de 4×3 (12 puntos)** en pantalla. El usuario debe:

1. **Memorizar una secuencia**: El sistema muestra una secuencia de puntos iluminados que el usuario debe memorizar
2. **Reproducir la secuencia**: El jugador debe tocar los mismos puntos en el mismo orden usando los movimientos de sus manos
3. **Avanzar de nivel**: Al completar el nivel actual, se desbloquea el siguiente con mayor dificultad

### Niveles de Dificultad

| Nivel | Puntos a Memorizar | Tiempo de Visualización | Penalización |
|-------|-------------------|------------------------|--------------|
| **Fácil** | 3 | 3 segundos | 8 puntos |
| **Medio** | 6 | 5 segundos | 5 puntos |
| **Difícil** | 8 | 10 segundos | 1 punto |

### Sistema de Puntuación

- **Puntos Base**: Por acertar cada punto de la secuencia
- **Bonificación de Velocidad**: Puntos extra si completas rápidamente
- **Racha**: Contador de aciertos consecutivos para motivación
- **Penalización**: Se restan puntos al cometer errores

### Detección de Movimientos

MotionMind utiliza **Google MediaPipe** para detectar:
- Hasta 2 manos simultáneamente
- 20 puntos de referencia (landmarks) por mano
- Posición precisa en tiempo real

---

## Requisitos

- Python 3.8 o superior
- Cámara web conectada
- Las siguientes librerías (ver `requirements.txt`):
  - `opencv-python`: Procesamiento de video
  - `mediapipe`: Detección de manos
  - `numpy`: Cálculos numéricos
  - `pandas`: Gestión de datos

---

## Instalación y Uso

### 1. Clonar el repositorio
```bash
git clone https://github.com/usuario/MotionMind.git
cd MotionMind
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Descargar el modelo de detección
```bash
python download_models.py
```

Este script descarga automáticamente el modelo `hand_landmarker.task` de Google MediaPipe.

### 4. Ejecutar el juego
```bash
python app.py
```

---

## Controles

### Menú Principal
- **Tecla 1** o **clic**: Registrarse como nuevo usuario
- **Tecla 2** o **clic**: Iniciar sesión
- **ESC**: Salir del juego

### Durante el Juego
- **Movimientos de manos**: Toca los puntos de la cuadrícula abriendo tu mano
- **Feedback visual**: 
  - Círculos verdes = aciertos
  - Cruz roja = error
  - Puntuación en tiempo real

---

## Estructura del Proyecto

```
MotionMind/
├── app.py                          # Script principal del juego
├── download_models.py              # Descargador de modelos IA
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
├── LICENSE                         # Licencia MIT
├── src/
│   ├── __init__.py                # Exporta módulos disponibles
│   ├── config.py                  # Configuración centralizada
│   ├── settings.py                # Constantes de juego
│   ├── auth.py                    # Sistema de autenticación
│   └── utils.py                   # Funciones auxiliares
├── models/
│   └── hand_landmarker.task       # Modelo de detección (descargado)
└── data/
    ├── usuarios.csv               # Base de datos de usuarios
    └── datos_juego_serio.csv      # Registro de sesiones
```

---

## Arquitectura Técnica

### Componentes Principales

1. **Detección de Manos (MediaPipe)**
   - Procesa 30 FPS en tiempo real
   - Identifica puntos clave de las manos
   - Sincronización temporal con frames de video

2. **Lógica de Juego**
   - Generación aleatoria de secuencias
   - Validación de toques vs. secuencias esperadas
   - Control de niveles progresivos

3. **Persistencia de Datos**
   - Autenticación mediante archivos CSV
   - Registro de resultados de sesiones
   - Seguimiento de progreso por usuario

4. **Interfaz Visual**
   - Overlay transparente con CVs (OpenCV)
   - Cuadrícula interactiva de 4×3
   - HUD con puntuación y estadísticas en tiempo real

---

## Datos Guardados

El sistema registra:
- **Usuarios**: Nombre de usuario y contraseña (hasheada)
- **Sesiones**: 
  - Fecha y hora de juego
  - Nivel alcanzado
  - Puntuación total
  - Racha máxima
  - Tiempo de juego

Estos datos se usan para:
- Mostrar progreso al usuario
- Comparar mejoras entre sesiones
- Facilitar seguimiento médico/terapéutico

---

## Tecnologías Utilizadas

| Tecnología | Uso |
|-----------|-----|
| **Python 3** | Lenguaje base |
| **OpenCV** | Captura y procesamiento de video |
| **MediaPipe** | Detección de manos con IA |
| **NumPy** | Cálculos vectoriales |
| **Pandas** | Gestión de CSV |

---

## Ejemplo de Uso

1. **Inicia la aplicación**: `python app.py`
2. **Regístrate** o **inicia sesión**
3. **Memoriza** la secuencia de puntos mostrada
4. **Toca los puntos** en el mismo orden acercando tu mano
5. **¡Gana puntos** por aciertos y velocidad!
6. **Avanza de nivel** al completar la secuencia

---

## Licencia

Este proyecto está bajo la **Licencia MIT**. Esta permitido usar, modificar y distribuir este software, siempre que se incluya el aviso de copyright original.

Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## Autoras

- **Sara Mora García** 
- **Elena Fernández Cebriaán**