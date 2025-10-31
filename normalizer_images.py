import os
from PIL import Image
import numpy as np

# Configuración
TARGET_SIZE = (224, 224)
DATASET_ROOT = "./dataset" 
CLASSES = ["famous", "not_famous"]
AGE_RANGES = ["10-20", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "81-90", "91+"]

def is_normalized(image_path):
    """Verifica si una imagen ya está normalizada (224x224 y JPG)"""
    try:
        with Image.open(image_path) as img:
            return img.size == TARGET_SIZE and image_path.lower().endswith('.jpg')
    except:
        return False

def center_crop_square(img):
    """Hace un crop cuadrado centrado de la imagen"""
    width, height = img.size
    
    # Determinar el tamaño del cuadrado (el lado más pequeño)
    size = min(width, height)
    
    # Calcular coordenadas para centrar el crop
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    
    return img.crop((left, top, right, bottom))

def normalize_image(input_path, output_path):
    """Normaliza una imagen: crop cuadrado + resize a 224x224 y guarda como JPG"""
    try:
        with Image.open(input_path) as img:
            # Convertir a RGB si es necesario
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Crop cuadrado centrado
            img_square = center_crop_square(img)
            
            # Resize
            img_resized = img_square.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
            
            # Guardar como JPG
            output_path_jpg = os.path.splitext(output_path)[0] + '.jpg'
            img_resized.save(output_path_jpg, 'JPEG', quality=95)
            
            # Si el archivo original no era JPG, eliminarlo
            if input_path.lower() != output_path_jpg.lower():
                os.remove(input_path)
            
            return True, None
    except Exception as e:
        return False, str(e)

def process_dataset():
    """Procesa todo el dataset"""
    total_processed = 0
    total_skipped = 0
    
    for class_name in CLASSES:
        for age_range in AGE_RANGES:
            folder_path = os.path.join(DATASET_ROOT, class_name, age_range)
            
            # Si la carpeta no existe, continuar
            if not os.path.exists(folder_path):
                continue
            
            folder_processed = 0
            folder_skipped = 0
            folder_errors = []
            
            # Obtener todas las imágenes
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                
                # Solo procesar archivos (no directorios)
                if not os.path.isfile(file_path):
                    continue
                
                # Verificar si es imagen
                if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    continue
                
                # Verificar si ya está normalizada
                if is_normalized(file_path):
                    folder_skipped += 1
                    total_skipped += 1
                    continue
                
                # Normalizar
                success, error = normalize_image(file_path, file_path)
                if success:
                    folder_processed += 1
                    total_processed += 1
                else:
                    folder_errors.append(f"{filename} ({error})")
            
            # Mostrar resumen de la carpeta
            if folder_processed > 0 or folder_skipped > 0:
                print(f"{class_name}/{age_range}: {folder_processed} procesadas, {folder_skipped} saltadas")
                if folder_errors:
                    for error in folder_errors:
                        print(f"  ⚠ Error: {error}")
    
    print(f"\n{'='*50}")
    print(f"Resumen total:")
    print(f"  Imágenes procesadas: {total_processed}")
    print(f"  Imágenes saltadas: {total_skipped}")
    print(f"{'='*50}")

if __name__ == "__main__":
    print("Iniciando normalización de imágenes...")
    print(f"Tamaño objetivo: {TARGET_SIZE}")
    print(f"Formato: JPG")
    print(f"Crop: Cuadrado centrado\n")
    
    if not os.path.exists(DATASET_ROOT):
        print(f"\nError: No se encontró el directorio '{DATASET_ROOT}'")
        print("Cambia la variable DATASET_ROOT al path correcto de tu dataset")
    else:
        process_dataset()