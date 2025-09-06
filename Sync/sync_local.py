import sqlite3
from datetime import datetime

# Función para obtener la conexión a la base de datos
def get_connection(db_path):
    return sqlite3.connect(db_path)

# Sincronización de la tabla Usuarios
def sync_usuarios(local_db, secondary_db):
    conn_local = get_connection(local_db)
    conn_secondary = get_connection(secondary_db)

    cursor_local = conn_local.cursor()
    cursor_secondary = conn_secondary.cursor()

    cursor_secondary.execute("SELECT * FROM usuarios")
    secondary_users = cursor_secondary.fetchall()

    for user in secondary_users:
        cedula = user[1]
        fecha_ultima_modificacion_sec = datetime.strptime(user[5], '%Y-%m-%d %H:%M:%S')

        cursor_local.execute("SELECT * FROM usuarios WHERE cedula = ?", (cedula,))
        local_user = cursor_local.fetchone()

        if local_user:
            fecha_ultima_modificacion_local = datetime.strptime(local_user[5], '%Y-%m-%d %H:%M:%S')
            if fecha_ultima_modificacion_sec > fecha_ultima_modificacion_local:
                cursor_local.execute("""
                    UPDATE usuarios SET nombre = ?, id_tarjeta = ?, rol = ?, flag_retirado = ?, fecha_ultima_modificacion = ?
                    WHERE cedula = ?""", (user[0], user[2], user[3], user[4], user[5], user[1]))
        else:
            cursor_local.execute("""
                INSERT INTO usuarios (nombre, cedula, id_tarjeta, rol, flag_retirado, fecha_ultima_modificacion)
                VALUES (?, ?, ?, ?, ?, ?)""", user)

    conn_local.commit()
    conn_local.close()
    conn_secondary.close()

# Sincronización de la tabla Menu
def sync_menu(local_db, secondary_db):
    conn_local = get_connection(local_db)
    conn_secondary = get_connection(secondary_db)

    cursor_local = conn_local.cursor()
    cursor_secondary = conn_secondary.cursor()

    cursor_secondary.execute("SELECT * FROM menu")
    secondary_menu = cursor_secondary.fetchall()

    for item in secondary_menu:
        cursor_local.execute("SELECT * FROM menu WHERE tipo = ?", (item[0],))
        local_item = cursor_local.fetchone()

        if local_item != item:
            cursor_local.execute("""
                INSERT OR REPLACE INTO menu (tipo, precio, descripcion, flag_horario, hora_inicio, hora_fin)
                VALUES (?, ?, ?, ?, ?, ?)""", item)

    conn_local.commit()
    conn_local.close()
    conn_secondary.close()

# Sincronización de la tabla Registros
def sync_registros(local_db, secondary_db):
    conn_local = get_connection(local_db)
    conn_secondary = get_connection(secondary_db)

    cursor_local = conn_local.cursor()
    cursor_secondary = conn_secondary.cursor()

    cursor_secondary.execute("SELECT id_registro FROM registros")
    secondary_records = cursor_secondary.fetchall()

    #for record in secondary_records:
    #    cursor_local.execute("DELETE FROM registros WHERE id_registro = ?", (record[0],))

    conn_local.commit()
    conn_local.close()
    conn_secondary.close()

# Sincronización de la tabla Pedidos
def sync_pedidos(local_db, secondary_db):
    conn_local = get_connection(local_db)
    conn_secondary = get_connection(secondary_db)

    cursor_local = conn_local.cursor()
    cursor_secondary = conn_secondary.cursor()

    # Eliminar registros aprobados
    cursor_secondary.execute("SELECT id_pedido FROM pedidos WHERE estado = 'Aprobado'")
    approved_orders = cursor_secondary.fetchall()

    for order in approved_orders:
        cursor_local.execute("DELETE FROM pedidos WHERE id_pedido = ?", (order[0],))

    # Agregar registros pendientes
    cursor_secondary.execute("SELECT * FROM pedidos WHERE estado = 'Pendiente'")
    pending_orders = cursor_secondary.fetchall()

    for order in pending_orders:
        cursor_local.execute("SELECT * FROM pedidos WHERE id_pedido = ?", (order[0],))
        local_order = cursor_local.fetchone()

        if not local_order:
            cursor_local.execute("""
                INSERT INTO pedidos (id_pedido, fecha, hora, tipo, cantidad, area, precio, sede, soporte, descripcion, estado, cedula_aprobador, fecha_ultima_modificacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", order)
        else:
            fecha_ultima_modificacion_sec = datetime.strptime(order[12], '%Y-%m-%d %H:%M:%S')
            fecha_ultima_modificacion_local = datetime.strptime(local_order[12], '%Y-%m-%d %H:%M:%S')
            if fecha_ultima_modificacion_sec > fecha_ultima_modificacion_local:
                cursor_local.execute("""
                    UPDATE pedidos SET fecha = ?, hora = ?, tipo = ?, cantidad = ?, area = ?, precio = ?, sede = ?, soporte = ?, descripcion = ?, estado = ?, cedula_aprobador = ?, fecha_ultima_modificacion = ?
                    WHERE id_pedido = ?""", (order[1], order[2], order[3], order[4], order[5], order[6], order[7], order[8], order[9], order[10], order[11], order[12], order[0]))

    conn_local.commit()
    conn_local.close()
    conn_secondary.close()

"""# Rutas de las bases de datos
local_db = '/home/user/Desktop/Admin/Admin/Desarrollo/Database/marmato_db.db'
secondary_db = 'db_secundaria.db'

# Sincronización de las tablas
sync_usuarios(local_db, secondary_db)
sync_menu(local_db, secondary_db)
sync_registros(local_db, secondary_db)
sync_pedidos(local_db, secondary_db)

print("Sincronización completada.")"""
