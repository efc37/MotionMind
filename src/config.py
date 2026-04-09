import os

class Config:
    """
    Clase de configuración centralizada para el proyecto MotionMind.
    Se encarga de gestionar rutas absolutas para que el proyecto funcione
    independientemente de desde dónde se ejecute el script.
    """
    def __init__(self):
        # --- GESTIÓN DE RUTAS (SISTEMA DE ARCHIVOS) ---
        
        # Localizamos la raíz del proyecto
        # os.path.abspath(__file__) obtiene la ruta de este archivo.
        # El primer dirname entra en 'src', el segundo sube a la raíz del proyecto.
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Modelo de detección de manos (Ruta absoluta a la carpeta 'models')
        self.model_path = os.path.join(self.base_dir, 'models', 'hand_landmarker.task')
        
        # Rutas de persistencia de datos (Carpeta 'data')
        # Se utilizan rutas absolutas para evitar errores al leer/escribir CSVs.
        self.usuarios_csv = os.path.join(self.base_dir, 'data', 'usuarios.csv')
        self.datos_juego_csv = os.path.join(self.base_dir, 'data', 'datos_juego_serio.csv')
        
        # --- PARÁMETROS DINÁMICOS DEL JUEGO ---
        
        # Margen de seguridad para evitar que los elementos se dibujen pegados al borde
        self.padding = 100
        
        # Tiempo límite total para completar la partida o el nivel (en segundos)
        self.game_time = 90     
        
        # Tiempo de vida de los elementos interactivos antes de ser invalidados
        self.frute_time = 5     

# Instancia única para ser importada en el resto del proyecto.
config = Config()