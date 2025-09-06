import os
import time
import json
import sqlite3
import requests
import shutil
from datetime import datetime
from sync_local import sync_usuarios, sync_menu, sync_registros, sync_pedidos

# Función para verificar la conexión a Internet
def internet_connected():
    try:
        requests.get('https://www.google.com', timeout=5)
        return True
    except requests.ConnectionError:
        return False

def download_from_dropbox(remote_path, local_path):
    # Usa rclone para descargar el archivo desde Dropbox
    os.system(f"rclone copy lmdb:{remote_path} {local_path}")

def upload_to_dropbox(local_path, remote_path):
    # Usa rclone para subir el archivo a Dropbox
    os.system(f"rclone copy {local_path} lmdb:{remote_path}")
    
def rename_file(file_path, new_name):
    # Obtener el directorio del archivo
    directory = os.path.dirname(file_path)
    
    # Construir la nueva ruta del archivo con el nuevo nombre
    new_file_path = os.path.join(directory, new_name)
    
    # Renombrar el archivo
    os.rename(file_path, new_file_path)
    print(f"Archivo renombrado a {new_file_path}")
    
def copy_and_rename_file(source_path, destination_directory, new_name):
    # Construir la ruta completa del archivo copiado en el destino
    destination_path = os.path.join(destination_directory, new_name)
    
    # Copiar el archivo al destino con el nuevo nombre
    shutil.copy2(source_path, destination_path)
    
    print(f"Archivo copiado de {source_path} a {destination_path}")

# Función para sincronizar las bases de datos
def sync_databases():
    local_db = '/home/lm/App/Desarrollo/Database/marmato_db.db'
    secondary_db = 'db_secundaria.db'

    # Aquí se incluye el script de sincronización previamente definido
    sync_usuarios(local_db, secondary_db)
    sync_menu(local_db, secondary_db)
    sync_registros(local_db, secondary_db)
    sync_pedidos(local_db, secondary_db)

# Ruta del archivo de banderas en Dropbox
flags_path = 'Aplicaciones/FoodFlow/Planchado/flags.json'
local_flags_path = 'flags.json'

while True:
    if internet_connected():
        try:
            # Descargar el archivo de banderas
            download_from_dropbox(flags_path, '.')

            # Leer el archivo de banderas
            with open(local_flags_path, 'r') as f:
                flags = json.load(f)

            if flags.get('pull_ready'):
                # Descargar la base de datos secundaria
                download_from_dropbox('Aplicaciones/FoodFlow/Planchado/planchado_db.db', '.')
                
                rename_file('/home/lm/App/Sync/planchado_db.db', 'db_secundaria.db')

                # Ejecutar el script de sincronización
                sync_databases()
                
                copy_and_rename_file('/home/lm/App/Desarrollo/Database/marmato_db.db', './', 'planchado_db.db')

                # Subir la base de datos local actualizada a Dropbox
                upload_to_dropbox('planchado_db.db', 'Aplicaciones/FoodFlow/Planchado/')

                # Actualizar las banderas
                flags['pull_ready'] = False
                flags['pushed'] = True

                with open(local_flags_path, 'w') as f:
                    json.dump(flags, f)

                # Subir el archivo de banderas actualizado
                upload_to_dropbox(local_flags_path, 'Aplicaciones/FoodFlow/Planchado/')

                # Registrar la fecha y hora de la actualización
                log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Actualización realizada correctamente desde lm.\n"
                with open('planchado_update_log.txt', 'a') as log_file:
                    log_file.write(log_entry)

                upload_to_dropbox('planchado_update_log.txt', 'Aplicaciones/FoodFlow/logs/')
                break
            else:
                print("Descarga no lista")
                break

        except Exception as e:
            print(f"Error durante la sincronización: {e}")
    else:
        print("No hay conexión a internet. Reintentando en 3 minutos.")
        # Esperar 3 minutos (180 segundos) antes de volver a intentar
        time.sleep(180)
