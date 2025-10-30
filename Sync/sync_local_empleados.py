import sqlite3
from datetime import datetime

def get_connection(db_path):
    return sqlite3.connect(db_path)

def sincronizar_empleados_local(local_db, downloaded_db):
    """
    Sincroniza la base de empleados local con la descargada desde Dropbox.
    La base local se actualiza según la información más reciente en cada registro.
    """
    conn_local = get_connection(local_db)
    conn_downloaded = get_connection(downloaded_db)

    cur_local = conn_local.cursor()
    cur_downloaded = conn_downloaded.cursor()

    cur_downloaded.execute("SELECT cedula, nombre, carnet, cargo, flag_retirado, fecha_ultima_actualizacion FROM empleados")
    empleados_downloaded = cur_downloaded.fetchall()

    for emp in empleados_downloaded:
        cedula, nombre, carnet, cargo, flag_retirado, fecha_ultima = emp

        cur_local.execute("SELECT cedula, nombre, carnet, cargo, flag_retirado, fecha_ultima_actualizacion FROM empleados WHERE cedula = ?", (cedula,))
        local_emp = cur_local.fetchone()

        if local_emp:
            _, nombre_local, carnet_local, cargo_local, flag_retirado_local, fecha_local = local_emp

            # Parsear fechas
            fecha_ultima_dt = datetime.strptime(fecha_ultima, "%Y-%m-%d %H:%M:%S")
            fecha_local_dt = datetime.strptime(fecha_local, "%Y-%m-%d %H:%M:%S")

            # Actualizar si la descargada es más reciente
            if fecha_ultima_dt > fecha_local_dt:
                cur_local.execute("""
                    UPDATE empleados
                    SET nombre = ?, carnet = ?, cargo = ?, flag_retirado = ?, fecha_ultima_actualizacion = ?
                    WHERE cedula = ?
                """, (nombre, carnet, cargo, flag_retirado, fecha_ultima, cedula))
        else:
            # Si el empleado no existe en la base local, insertarlo
            cur_local.execute("""
                INSERT INTO empleados (cedula, nombre, carnet, cargo, flag_retirado, fecha_ultima_actualizacion)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cedula, nombre, carnet, cargo, flag_retirado, fecha_ultima))

    conn_local.commit()
    conn_local.close()
    conn_downloaded.close()

    print("✅ Sincronización de empleados completada (punto secundario).")
