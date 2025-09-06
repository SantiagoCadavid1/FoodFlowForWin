import sqlite3
from datetime import datetime

# Conexión a la base de datos
def connect_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

# Consulta a la base de datos y generación de documento de texto
def generate_report(db_path, output_file):
    # Obtener la fecha actual en formato 'YYYY-MM-DD'
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Consulta SQL
    query = f"""
    SELECT u.nombre, u.cedula, u.rol, r.hora, r.tipo
    FROM registros r
    JOIN usuarios u ON r.cedula = u.cedula
    WHERE r.fecha = ?
    ORDER BY r.hora DESC;
    """

    # Conectar a la base de datos
    conn = connect_db(db_path)
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(query, (current_date,))
        records = cursor.fetchall()

        # Crear archivo de texto y escribir los resultados
        with open(output_file, 'w') as f:
            for row in records:
                f.write(f"Nombre: {row[0]}, Cédula: {row[1]}, Rol: {row[2]}, Hora: {row[3]}, Tipo: {row[4]}\n")

        print(f"Reporte generado correctamente: {output_file}")
    except sqlite3.Error as e:
        print(f"Error al ejecutar la consulta: {e}")
    finally:
        conn.close()

# Ejecutar script
if __name__ == "__main__":
    # Ruta a la base de datos SQLite
    database_path = '/home/casino/App/Desarrollo/Database/marmato_db.db'
    # Nombre del archivo de salida
    output_file = '/home/casino/Desktop/registros_diarios.txt'

    generate_report(database_path, output_file)

