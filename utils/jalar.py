import pandas as pd
import mysql.connector

# ID de la hoja de cálculo
spreadsheet_id = '1jWHTeS4Reph-2TWrQE4r2-Db4sUlBeU5DUcsHbrtvRU'

# URL para descargar el CSV
csv_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv'

# Lee el CSV desde la URL
df = pd.read_csv(csv_url)

# Asegúrate de que la columna de fecha y hora se convierta en tipo datetime
df['Marca temporal'] = pd.to_datetime(df['Marca temporal'])

# Especifica la fecha y hora desde la que quieres filtrar
fecha_hora_inicio = '2024-10-27 15:30:00'

# Filtra los datos desde la fecha y hora especificadas
df_filtrado = df[df['Marca temporal'] >= fecha_hora_inicio]

# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='1234',
    database='pos'
)

# Crear un cursor para ejecutar las consultas SQL
cursor = conn.cursor()

# Iterar sobre las filas del DataFrame filtrado y agregar cada fila a la tabla 'test'
for index, row in df_filtrado.iterrows():
    sql = """
    INSERT INTO test (marca_temporal, correo, opcion, link_pdf) 
    VALUES (%s, %s, %s, %s)
    """
    valores = (row['Marca temporal'], row['Dirección de correo electrónico'], row['Elige 2'], row['Sube un pdf'])
    cursor.execute(sql, valores)

# Confirmar la transacción
conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()

print("Datos insertados exitosamente.")

