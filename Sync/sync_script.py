import os
import time
import json
import sqlite3
import requests
import shutil
from datetime import datetime
from sync_local import sync_usuarios, sync_menu, sync_registros, sync_pedidos

CONFIG_FILE = "C:/FoodFlow/config.json"

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"No se encontró el archivo de configuración: {CONFIG_FILE}")

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

config = cargar_config()
sede = config.get("sede")

# Función para verificar la conexión a Internet
def internet_connected():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

def download_from_dropbox(remote_path, local_path):
    # Usa rclone para descargar el archivo desde Dropbox
    result = os.system(f"rclone copy foodflow:{remote_path} {local_path}")
    return result == 0  # True si éxito, False si error

def upload_to_dropbox(local_path, remote_path):
    # Usa rclone para subir el archivo a Dropbox
    os.system(f"rclone copy {local_path} foodflow:{remote_path}")
    
def rename_file(src, dst):
    # Si el archivo destino ya existe, eliminarlo primero
    if os.path.exists(dst):
        os.remove(dst)
        print(f"Archivo existente eliminado: {dst}")
    
    os.rename(src, dst)
    print(f"Archivo renombrado de {src} a {dst}")
    
def copy_and_rename_file(source_path, destination_directory, new_name):
    # Construir la ruta completa del archivo copiado en el destino
    destination_path = os.path.join(destination_directory, new_name)
    
    # Si el archivo ya existe en el destino, lo eliminamos
    if os.path.exists(destination_path):
        os.remove(destination_path)
        print(f"Archivo existente eliminado: {destination_path}")
    
    # Copiar el archivo al destino con el nuevo nombre
    shutil.copy2(source_path, destination_path)
    
    print(f"Archivo copiado de {source_path} a {destination_path}")

# Función para sincronizar las bases de datos
def sync_databases():
    local_db = 'C:/FoodFlow/Desarrollo/Database/marmato_db.db'
    secondary_db = 'db_secundaria.db'

    # Aquí se incluye el script de sincronización previamente definido
    sync_usuarios(local_db, secondary_db)
    sync_menu(local_db, secondary_db)
    sync_registros(local_db, secondary_db)
    sync_pedidos(local_db, secondary_db)

# Ruta del archivo de banderas en Dropbox
flags_path = f'Aplicaciones/FoodFlow/Sedes/{sede}/flags.json'
local_flags_path = 'flags.json'

while True:
    if internet_connected():
        try:
            # Descargar el archivo de banderas
            if download_from_dropbox(flags_path, '.'):
                # Leer el archivo de banderas
                with open(local_flags_path, 'r') as f:
                    flags = json.load(f)

                if flags.get('pull_ready'):
                    # Descargar la base de datos secundaria en la carpeta Sync
                    download_from_dropbox(
                        f'Aplicaciones/FoodFlow/Sedes/{sede}/{sede}_db.db',
                        'C:/FoodFlow/Sync'
                    )
                    
                    # Renombrar la base de datos descargada a db_secundaria.db
                    rename_file(
                        f'C:/FoodFlow/Sync/{sede}_db.db',
                        f'C:/FoodFlow/Sync/db_secundaria.db'
                    )

                    # Ejecutar el script de sincronización
                    sync_databases()
                    
                    # Copiar y renombrar la base de datos local
                    copy_and_rename_file(
                        'C:/FoodFlow/Desarrollo/Database/marmato_db.db',
                        './',
                        f'{sede}_db.db'
                    )

                    # Subir la base de datos local actualizada a Dropbox
                    upload_to_dropbox(f'{sede}_db.db', f'Aplicaciones/FoodFlow/Sedes/{sede}/')

                    # Actualizar las banderas
                    flags['pull_ready'] = False
                    flags['pushed'] = True

                    with open(local_flags_path, 'w') as f:
                        json.dump(flags, f)

                    # Subir el archivo de banderas actualizado
                    upload_to_dropbox(local_flags_path, f'Aplicaciones/FoodFlow/Sedes/{sede}/')
    
                    # Registrar la fecha y hora de la actualización
                    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Actualización realizada correctamente desde {sede}.\n"
                    with open(f'{sede}_update_log.txt', 'a') as log_file:
                        log_file.write(log_entry)

                    upload_to_dropbox(f'{sede}_update_log.txt', 'Aplicaciones/FoodFlow/logs/')
                    break
                else:
                    print("Descarga no lista")
                    break
            else:
                copy_and_rename_file('C:/FoodFlow/Desarrollo/Database/marmato_db.db', './', f'{sede}_db.db')
                upload_to_dropbox(f'{sede}_db.db', f'Aplicaciones/FoodFlow/Sedes/{sede}/')
                # Leer el archivo de banderas
                with open(local_flags_path, 'r') as f:
                    flags = json.load(f)
                # Actualizar las banderas
                flags['pull_ready'] = False
                flags['pushed'] = True
                with open(local_flags_path, 'w') as f:
                        json.dump(flags, f)
                # Subir el archivo de banderas actualizado
                upload_to_dropbox(local_flags_path, f'Aplicaciones/FoodFlow/Sedes/{sede}/')
    
                # Registrar la fecha y hora de la actualización
                log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Actualización realizada correctamente desde {sede}.\n"
                with open(f'{sede}_update_log.txt', 'a') as log_file:
                    log_file.write(log_entry)

                upload_to_dropbox(f'{sede}_update_log.txt', 'Aplicaciones/FoodFlow/logs/')
                break
        except Exception as e:
            print(f"Error durante la sincronización: {e}")
    else:
        print("No hay conexión a internet. Reintentando en 3 minutos.")
        # Esperar 3 minutos (180 segundos) antes de volver a intentar
        time.sleep(180)
