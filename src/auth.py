import cv2
import csv
import os
import sys
from src.utils import escribir_centrado, escribir_centrado_clicable

# --- CONFIGURACIÓN DE RUTAS ---
# Se establece la ruta base del proyecto subiendo un nivel desde la carpeta 'src'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ruta completa al archivo CSV donde se almacenan las credenciales de usuario
ARCHIVO_USUARIOS = os.path.join(BASE_DIR, "data", "usuarios.csv")

# --- MENÚ PRINCIPAL DE AUTENTICACIÓN ---
def menu_autenticacion(cap):
    """
    Gestiona la pantalla inicial del juego. Permite al usuario elegir entre
    registrarse o iniciar sesión mediante clics o teclado.
    """
    cv2.namedWindow("Juego MotionMind")

    # Diccionario para capturar el estado del ratón de forma persistente
    estado_raton = {"x": None, "y": None, "clicked": False}

    def callback_raton(evento, x, y, flags, param):
        """Función interna que captura coordenadas cuando se hace clic izquierdo."""
        if evento == cv2.EVENT_LBUTTONDOWN:
            estado_raton["x"] = x
            estado_raton["y"] = y
            estado_raton["clicked"] = True

    # Vincula el callback a la ventana activa
    cv2.setMouseCallback("Juego MotionMind", callback_raton)

    while True:
        ok, frame = cap.read()
        if not ok:
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)

        # Asegura que el callback siga activo en cada iteración del bucle
        cv2.setMouseCallback("Juego MotionMind", callback_raton)

        frame = cv2.flip(frame, 1)  # Invierte la imagen horizontalmente (efecto espejo)
        h, w = frame.shape[:2]

        # --- DISEÑO VISUAL (OVERLAY VIOLETA) ---
        capa = frame.copy()
        cv2.rectangle(capa, (0, 0), (w, h), (200, 180, 255), -1)
        alpha = 0.45
        frame = cv2.addWeighted(capa, alpha, frame, 1 - alpha, 0)

        # Configuración de textos y posiciones
        titulo = "MotionMind"
        opcion1 = "[1] Registro"
        opcion2 = "[2] Inicio de sesion"
        texto_pista = "Pulsa 1 o 2 o haz clic | ESC para salir"

        y_registro = 250
        y_login = 300

        # Almacén de coordenadas de los botones para detectar clics
        rectangulos_click = {}

        # Dibujado de elementos en pantalla
        escribir_centrado(frame, titulo, 180, 1.7, (255, 255, 255), 3)
        escribir_centrado_clicable(frame, opcion1, y_registro, 1.0, (50, 50, 50), 2, rectangulos_click, "registro")
        escribir_centrado_clicable(frame, opcion2, y_login, 1.0, (50, 50, 50), 2, rectangulos_click, "login")
        escribir_centrado(frame, texto_pista, 370, 0.8, (80, 80, 80), 2)

        cv2.imshow("Juego MotionMind", frame)
        tecla = cv2.waitKey(30) & 0xFF

        # --- CONTROL POR TECLADO ---
        if tecla == 27:  # Salida del programa con ESC
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)
        elif tecla == ord('1'): # Acceso directo a Registro
            usuario, password = registrar_usuario(cap)
            estado_raton = {"x": None, "y": None, "clicked": False}
            cv2.setMouseCallback("Juego MotionMind", callback_raton)
            if usuario is not None:
                return usuario, password
        elif tecla == ord('2'): # Acceso directo a Inicio de Sesión
            usuario, password = iniciar_sesion(cap)
            estado_raton = {"x": None, "y": None, "clicked": False}
            cv2.setMouseCallback("Juego MotionMind", callback_raton)
            if usuario is not None:
                return usuario, password

        # --- CONTROL POR RATÓN ---
        if estado_raton["clicked"]:
            mx, my = estado_raton["x"], estado_raton["y"]
            estado_raton["clicked"] = False

            # Itera sobre los botones dibujados para ver si se hizo clic en uno
            for nombre, (x1, y1, x2, y2) in rectangulos_click.items():
                if x1 <= mx <= x2 and y1 <= my <= y2:
                    if nombre == "registro":
                        usuario, password = registrar_usuario(cap)
                        estado_raton = {"x": None, "y": None, "clicked": False}
                        cv2.setMouseCallback("Juego MotionMind", callback_raton)
                        if usuario is not None:
                            return usuario, password
                    elif nombre == "login":
                        usuario, password = iniciar_sesion(cap)
                        estado_raton = {"x": None, "y": None, "clicked": False}
                        cv2.setMouseCallback("Juego MotionMind", callback_raton)
                        if usuario is not None:
                            return usuario, password
                    break


# --- FUNCIÓN DE REGISTRO ---
def registrar_usuario(cap):
    """Interfaz para capturar nombre y contraseña y guardarlos en el CSV."""
    nombre_usuario = ""
    password = ""
    mensaje_error = ""
    escribiendo_password = False # Alterna el foco entre usuario (False) y contraseña (True)

    cv2.namedWindow("Juego MotionMind")
    estado_raton = {"x": None, "y": None, "clicked": False}

    def callback_raton(evento, x, y, flags, param):
        if evento == cv2.EVENT_LBUTTONDOWN:
            estado_raton["x"], estado_raton["y"], estado_raton["clicked"] = x, y, True

    cv2.setMouseCallback("Juego MotionMind", callback_raton)

    while True:
        ok, frame = cap.read()
        if not ok:
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # Overlay estético
        capa = frame.copy()
        cv2.rectangle(capa, (0, 0), (w, h), (200, 180, 255), -1)
        alpha = 0.45
        frame = cv2.addWeighted(capa, alpha, frame, 1 - alpha, 0)

        # Configuración visual de los campos
        titulo = "Registro - MotionMind"
        texto_usuario = "Nombre de usuario (no puede repetirse):"
        texto_pass = "Contrasena:"
        texto_pista = "ENTER cambia campo/confirma | Clic para elegir campo | ESC para volver"

        # Representación de los campos con cursor (_) y ocultamiento de contraseña (*)
        mostrar_usuario = f"> {nombre_usuario}_"
        mostrar_pass = "> " + ("*" * len(password) + "_")

        y_usuario = 230
        y_pass = 330

        # Cambio de color según el campo activo (Negro si activo, Gris si inactivo)
        color_usuario = (30, 30, 30) if not escribiendo_password else (100, 100, 100)
        color_pass = (30, 30, 30) if escribiendo_password else (100, 100, 100)

        rectangulos_click = {}

        # Dibujado de la interfaz de registro
        escribir_centrado(frame, titulo, 120, 1.2, (255, 255, 255), 3)
        escribir_centrado(frame, texto_usuario, 190, 0.8, (60, 60, 60), 2)
        escribir_centrado_clicable(frame, mostrar_usuario, y_usuario, 0.9, color_usuario, 2, rectangulos_click, "campo_usuario")
        escribir_centrado(frame, texto_pass, 290, 0.8, (60, 60, 60), 2)
        escribir_centrado_clicable(frame, mostrar_pass, y_pass, 0.9, color_pass, 2, rectangulos_click, "campo_pass")
        escribir_centrado(frame, texto_pista, 400, 0.7, (80, 80, 80), 2)

        if mensaje_error:
            escribir_centrado(frame, mensaje_error, 450, 0.7, (0, 0, 255), 2)

        cv2.imshow("Juego MotionMind", frame)
        tecla = cv2.waitKey(30) & 0xFF

        if tecla == 27: # Volver al menú anterior
            return None, None

        # --- LÓGICA DE VALIDACIÓN Y ESCRITURA ---
        elif tecla in (13, 10): # Tecla ENTER
            if not escribiendo_password: # Si estamos en usuario, pasar a password
                if not nombre_usuario.strip():
                    mensaje_error = "El nombre no puede estar vacío."
                else:
                    mensaje_error = ""
                    escribiendo_password = True
            else: # Si estamos en password, intentar guardar
                if not password:
                    mensaje_error = "La contrasena no puede estar vacía."
                else:
                    # Comprobación de usuario duplicado en el archivo
                    existe = False
                    if os.path.exists(ARCHIVO_USUARIOS):
                        with open(ARCHIVO_USUARIOS, newline="", encoding="utf-8") as f:
                            lector = csv.DictReader(f)
                            for fila in lector:
                                if fila["username"] == nombre_usuario:
                                    existe = True
                                    break
                    
                    if existe:
                        mensaje_error = "Ese nombre de usuario ya existe. Elige otro."
                    else:
                        # Guardado de credenciales en modo 'Append'
                        with open(ARCHIVO_USUARIOS, "a", newline="", encoding="utf-8") as f:
                            escritor = csv.writer(f)
                            escritor.writerow([nombre_usuario, password])
                        return nombre_usuario, password

        elif tecla in (8, 127): # Tecla BACKSPACE (borrar último carácter)
            if not escribiendo_password:
                nombre_usuario = nombre_usuario[:-1]
            else:
                password = password[:-1]

        elif 32 <= tecla <= 126: # Entrada de caracteres estándar (ASCII)
            caracter = chr(tecla)
            if not escribiendo_password:
                if len(nombre_usuario) < 20:
                    nombre_usuario += caracter
            else:
                if len(password) < 20:
                    password += caracter

        # Detección de clics para cambiar de campo manualmente
        if estado_raton["clicked"]:
            mx, my = estado_raton["x"], estado_raton["y"]
            estado_raton["clicked"] = False
            for nombre, (x1, y1, x2, y2) in rectangulos_click.items():
                if x1 <= mx <= x2 and y1 <= my <= y2:
                    escribiendo_password = (nombre == "campo_pass")
                    break


# --- FUNCIÓN DE INICIO DE SESIÓN ---
def iniciar_sesion(cap):
    """Verifica si el usuario y contraseña existen en la base de datos CSV."""
    nombre_usuario = ""
    password = ""
    mensaje_error = ""
    escribiendo_password = False

    cv2.namedWindow("Juego MotionMind")
    estado_raton = {"x": None, "y": None, "clicked": False}

    def callback_raton(evento, x, y, flags, param):
        if evento == cv2.EVENT_LBUTTONDOWN:
            estado_raton["x"], estado_raton["y"], estado_raton["clicked"] = x, y, True

    cv2.setMouseCallback("Juego MotionMind", callback_raton)

    while True:
        ok, frame = cap.read()
        if not ok:
            cap.release()
            cv2.destroyAllWindows()
            sys.exit(0)

        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        capa = frame.copy()
        cv2.rectangle(capa, (0, 0), (w, h), (200, 180, 255), -1)
        alpha = 0.45
        frame = cv2.addWeighted(capa, alpha, frame, 1 - alpha, 0)

        titulo = "Inicio de sesion - MotionMind"
        texto_usuario = "Nombre de usuario:"
        texto_pass = "Contrasena:"
        texto_pista = "ENTER cambia campo/confirma | Clic para elegir campo | ESC para volver"

        mostrar_usuario = f"> {nombre_usuario}_"
        mostrar_pass = "> " + ("*" * len(password) + "_")

        y_usuario = 230
        y_pass = 330

        color_usuario = (30, 30, 30) if not escribiendo_password else (100, 100, 100)
        color_pass = (30, 30, 30) if escribiendo_password else (100, 100, 100)

        rectangulos_click = {}

        escribir_centrado(frame, titulo, 120, 1.2, (255, 255, 255), 3)
        escribir_centrado(frame, texto_usuario, 190, 0.8, (60, 60, 60), 2)
        escribir_centrado_clicable(frame, mostrar_usuario, y_usuario, 0.9, color_usuario, 2, rectangulos_click, "campo_usuario")
        escribir_centrado(frame, texto_pass, 290, 0.8, (60, 60, 60), 2)
        escribir_centrado_clicable(frame, mostrar_pass, y_pass, 0.9, color_pass, 2, rectangulos_click, "campo_pass")
        escribir_centrado(frame, texto_pista, 400, 0.7, (80, 80, 80), 2)

        if mensaje_error:
            escribir_centrado(frame, mensaje_error, 450, 0.7, (0, 0, 255), 2)

        cv2.imshow("Juego MotionMind", frame)
        tecla = cv2.waitKey(30) & 0xFF

        if tecla == 27:
            return None, None

        elif tecla in (13, 10):
            if not escribiendo_password:
                if not nombre_usuario.strip():
                    mensaje_error = "El nombre no puede estar vacio."
                else:
                    mensaje_error = ""
                    escribiendo_password = True
            else:
                if not password:
                    mensaje_error = "La contrasena no puede estar vacia."
                else:
                    # Lógica de comprobación de credenciales
                    ok_login = False
                    if os.path.exists(ARCHIVO_USUARIOS):
                        with open(ARCHIVO_USUARIOS, newline="", encoding="utf-8") as f:
                            lector = csv.DictReader(f)
                            for fila in lector:
                                # Compara tanto usuario como password
                                if fila["username"] == nombre_usuario and fila["password"] == password:
                                    ok_login = True
                                    break
                    
                    if ok_login:
                        return nombre_usuario, password
                    else:
                        mensaje_error = "Usuario o contrasena incorrectos."

        elif tecla in (8, 127):
            if not escribiendo_password:
                nombre_usuario = nombre_usuario[:-1]
            else:
                password = password[:-1]

        elif 32 <= tecla <= 126:
            caracter = chr(tecla)
            if not escribiendo_password:
                if len(nombre_usuario) < 20:
                    nombre_usuario += caracter
            else:
                if len(password) < 20:
                    password += caracter

        if estado_raton["clicked"]:
            mx, my = estado_raton["x"], estado_raton["y"]
            estado_raton["clicked"] = False
            for nombre, (x1, y1, x2, y2) in rectangulos_click.items():
                if x1 <= mx <= x2 and y1 <= my <= y2:
                    escribiendo_password = (nombre == "campo_pass")
                    break