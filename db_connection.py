import pyodbc

# Configura los detalles de la conexión
SERVER = 'conafe-server.database.windows.net'  # Servidor
DATABASE = 'conafe-database'                  # Nombre de la base de datos
USERNAME = 'admin-conafe'                     # Usuario administrador
PASSWORD = 'MateriaAcaba08/01/25'             # Contraseña
DRIVER = '{ODBC Driver 17 for SQL Server}'    # Driver ODBC

def get_connection():
    """
    Establece y retorna una conexión a la base de datos.
    """
    try:
        conn = pyodbc.connect(
            f"DRIVER={DRIVER};SERVER={SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}"
        )
        print("Conexión exitosa a la base de datos")
        return conn
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        raise

def execute_query(query, params=None):
    """
    Ejecuta una consulta SQL en la base de datos.
    Args:
        query (str): Consulta SQL a ejecutar.
        params (tuple): Parámetros para consultas parametrizadas (opcional).
    Returns:
        list: Resultado de la consulta como una lista de tuplas.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        print("Consulta ejecutada y conexión cerrada.")
        return results
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        raise

def execute_non_query(query, params=None):
    """
    Ejecuta una consulta SQL en la base de datos que no devuelve resultados.
    Args:
        query (str): Consulta SQL a ejecutar.
        params (tuple): Parámetros para consultas parametrizadas (opcional).
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()  # Confirmar los cambios
        cursor.close()
        conn.close()
        print("Consulta no devuelve resultados ejecutada correctamente y conexión cerrada.")
    except Exception as e:
        print("Error al ejecutar la consulta:", e)
        raise

def execute_query_comb(query, params=None):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Si la consulta es de tipo modificación, haz un commit
        if query.strip().upper().startswith(('INSERT', 'UPDATE', 'DELETE')):
            connection.commit()
            return None  # No se espera un resultado para estas operaciones

        # Si es una consulta SELECT, devuelve los resultados
        return cursor.fetchall()
    except Exception as e:
        print(f"Error ejecutando la consulta: {e}")
        raise e  # Relanza el error para depuración
    finally:
        connection.close()

def close_connection(conn):
    """
    Cierra la conexión a la base de datos.
    Args:
        conn: Objeto de conexión.
    """
    try:
        if conn:
            conn.close()
            print("Conexión cerrada correctamente.")
    except Exception as e:
        print("Error al cerrar la conexión:", e)
        raise
