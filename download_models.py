import requests
import os
import tqdm

def descargar_modelos():
    """
    Descarga el modelo hand_landmarker.task de Google MediaPipe
    y lo guarda en la carpeta /models.
    """
    # URL oficial del modelo Hand Landmarker de MediaPipe
    urls = {
        "hand_landmarker.task": "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/latest/hand_landmarker.task"
    }

    # Determinamos la ruta de la carpeta 'models' en la raíz del proyecto
    # Esto funciona independientemente de si se ejecuta desde la raíz o desde src
    base_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(base_dir, 'models')

    # Crear el directorio de destino si no existe
    if not os.path.exists(models_dir):
        print(f"Creando directorio: {models_dir}")
        os.makedirs(models_dir, exist_ok=True)

    for nombre_archivo, url in urls.items():
        archivo_destino = os.path.join(models_dir, nombre_archivo)

        # Si el archivo ya existe, evitamos la descarga para ahorrar tiempo/datos
        if os.path.exists(archivo_destino):
            print(f"El archivo {nombre_archivo} ya existe en {models_dir}. Omitiendo descarga.")
            continue

        print(f"Descargando {nombre_archivo}...")
        
        try:
            # Descargar el archivo con barra de progreso para feedback visual
            response = requests.get(url, stream=True)
            response.raise_for_status() # Lanza error si la descarga falla (e.g. 404)
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(archivo_destino, 'wb') as f:
                progress_bar = tqdm.tqdm(total=total_size, unit='iB', unit_scale=True, desc=nombre_archivo)
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
                progress_bar.close()
            
            print(f"¡Descarga completada con éxito!: {archivo_destino}")
            
        except Exception as e:
            print(f"Error al descargar {nombre_archivo}: {e}")

if __name__ == "__main__":
    descargar_modelos()