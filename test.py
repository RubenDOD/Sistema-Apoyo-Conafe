import pyodbc

# Configura los detalles de la conexión
server = 'conafe-server.database.windows.net'  # Cambia 'tu-servidor' por el nombre de tu servidor
database = 'conafe-database'               # Nombre de tu base de datos
username = 'admin-conafe'                     # Usuario administrador del servidor
password = 'MateriaAcaba08/01/25'                  # Contraseña del usuario administrador
driver = '{ODBC Driver 17 for SQL Server}'  # Asegúrate de tener el controlador instalado

# Establece la conexión
try:
    conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
    print("Conexión exitosa")
except Exception as e:
    print("Error al conectar a la base de datos:", e)
    exit()  # Salir del script si la conexión falla

# Realizar una consulta
try:
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT estado FROM CCT")  # Consulta corregida
    for row in cursor:
        print(row)
except Exception as e:
    print("Error al ejecutar la consulta:", e)
finally:
    # Cierra la conexión
    conn.close()