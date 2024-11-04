import pandas as pd
import mysql.connector
from datetime import datetime


# Conexión a la base de datos MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='1234',
    database='CONAFE'
)

# Función para insertar en la tabla Aspirante
def insertar_aspirante(id_aspirante, telefono_fijo, telefono_movil, correo, curp, edad, nombres, apellido_paterno, apellido_materno, fecha_nacimiento, genero, nacionalidad, estado_solicitud):
    sql = """
    INSERT INTO Aspirante (id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, telefono_fijo, telefono_movil, correo, curp, edad, nombres, apellido_paterno, apellido_materno, fecha_nacimiento, genero, nacionalidad, estado_solicitud))
    conn.commit()

# Función para insertar en la tabla EquipoAspirante
def insertar_equipo_aspirante(id_aspirante, estatura, peso, talla_playera, talla_pantalon, talla_calzado):
    sql = """
    INSERT INTO EquipoAspirante (id_Aspirante, estatura, peso, tallaPlayera, tallaPantalon, tallaCalzado)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, estatura, peso, talla_playera, talla_pantalon, talla_calzado))
    conn.commit()

# Función para insertar en la tabla InfoEducativaAspirante
def insertar_info_educativa_aspirante(id_aspirante, fecha_solicitud, nivel_educativo, lengua_indigena, pregunta1, pregunta2, pregunta3, pregunta4, pregunta5, pregunta6, pregunta7, pregunta8, pregunta9):
    sql = """
    INSERT INTO InfoEducativaAspirante (id_Aspirante, fechaSolicitud, nivelEducativo, lenguaIndigena, pregunta1, pregunta2, pregunta3, pregunta4, pregunta5, pregunta6, pregunta7, pregunta8, pregunta9)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, fecha_solicitud, nivel_educativo, lengua_indigena, pregunta1, pregunta2, pregunta3, pregunta4, pregunta5, pregunta6, pregunta7, pregunta8, pregunta9))
    conn.commit()

# Función para insertar en la tabla ResidenciaAspirante
def insertar_residencia_aspirante(id_aspirante, codigo_postal, estado, municipio, localidad, colonia, calle, numero_exterior, numero_interior):
    sql = """
    INSERT INTO ResidenciaAspirante (id_Aspirante, codigoPostal, estado, municipio, localidad, colonia, calle, numeroExterior, numeroInterior)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, codigo_postal, estado, municipio, localidad, colonia, calle, numero_exterior, numero_interior))
    conn.commit()

# Función para insertar en la tabla InfoBancariaAspirante
def insertar_info_bancaria_aspirante(id_aspirante, nombre_banco, cuenta_bancaria, clabe):
    sql = """
    INSERT INTO InfoBancariaAspirante (id_Aspirante, nombreBanco, cuentaBancaria, clabe)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, nombre_banco, cuenta_bancaria, clabe))
    conn.commit()

# Función para insertar en la tabla DocumentosAspirante
def insertar_documentos_aspirante(id_aspirante, certificado, identificacion, estado_de_cuenta):
    sql = """
    INSERT INTO DocumentosAspirante (id_Aspirante, certificado, identificacion, estadoDeCuenta)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, certificado, identificacion, estado_de_cuenta))
    conn.commit()

# Función para insertar en la tabla ParticipacionAspirante
def insertar_participacion_aspirante(id_aspirante, estado, ciclo_escolar, medio_de_enterarse, municipio):
    sql = """
    INSERT INTO ParticipacionAspirante (id_Aspirante, estado, cicloEscolar, medioDeEnterarse, municipio)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (id_aspirante, estado, ciclo_escolar, medio_de_enterarse, municipio))
    conn.commit()

# ID de la hoja de cálculo
spreadsheet_id = '1V0eUeAHJD_UfK2SjtSZ46hjc28p2Fa47qqtaYmOGeBs'

# URL para descargar el CSV
csv_url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv'

# Lee el CSV desde la URL
df = pd.read_csv(csv_url)

# Asegúrate de que la columna de fecha y hora se convierta en tipo datetime
df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], dayfirst=True)
#print(df['Marca temporal'].dtypes)
#print(df['Marca temporal'].head())

# Especifica la fecha y hora desde la que quieres filtrar (convertida a datetime)
fecha_hora_inicio = datetime.strptime('2024-10-25 15:30:00', '%Y-%m-%d %H:%M:%S')

# Filtra los datos desde la fecha y hora especificadas
df_filtrado = df[df['Marca temporal'] > fecha_hora_inicio]

# Verifica si el filtro está funcionando correctamente
#print("DataFrame Filtrado:")
#print(df_filtrado)

# Crear un cursor para ejecutar las consultas SQL
cursor = conn.cursor()

# Iterar sobre las filas del DataFrame filtrado y agregar cada fila a la tabla 'test'
for index, row in df_filtrado.iterrows():
    valor = (row['Correo electrónico:'],)  # Nota: Debe ser una tupla
    sql = "SELECT id_Usuario FROM Usuario WHERE correo = %s"
    cursor.execute(sql, valor)
    # Recupera el resultado
    resultado = cursor.fetchone()
    if resultado:
        id_usuario = resultado[0]
        sql_aspirante = "SELECT id_Aspirante FROM Aspirante WHERE id_Aspirante = %s"
        cursor.execute(sql_aspirante, (id_usuario,))
        resultado_aspirante = cursor.fetchone()
        if not resultado_aspirante:
            id_usuario = resultado[0]
            row['Fecha de nacimiento*:'] = pd.to_datetime(row['Fecha de nacimiento*:'], dayfirst=True)
            #print(f"El ID del usuario es: {id_usuario}")
            insertar_aspirante(id_usuario, row['Teléfono fijo:'], row['Teléfono móvil:'], row['Correo electrónico:'], row['CURP*:'], row['Edad:']
                            , row['Nombre(s)*:'], row['Primer apellido*:'], row['Segundo apellido:'], row['Fecha de nacimiento*:'], row['Género*:'], row['Nacionalidad*:']
                            , "Pendiente")
            insertar_equipo_aspirante(id_usuario, row['Estatura*:'], row['Peso*:'], row['Talla de playera*:'], row['Talla de pantalón*:'], row['Calzado*:'])
            insertar_info_educativa_aspirante(id_usuario, row['Marca temporal'], row['Nivel educativo*:'] , "Pendiente", row['1. ¿Hablas alguna lengua indígena?:'], 
                                            row['2. De acuerdo a tus aptitudes, ¿en qué nivel educativo prefieres realizar tu Servicio Social Educativo?:'], row['3. Gusto o experiencia en cuanto a divulgación de la ciencia:'], 
                                            row['4. Habilidades o experiencias previas en materia de arte y cultura:'], row['5. Menciona ¿Cuál es el interés que tienes en el desarrollo comunitario?*:'], 
                                            row['6. ¿Cuál es la principal razón por la que quieres ser un Lider para la Educación Comunitaria?:'], row['7. ¿Cuál es la profesión que más te llama la atención?*:'], 
                                            row['8. ¿Tu participación en el CONAFE te servirá como requisito de titulación universitaria?:'], row['9. Te interesa la incorporación al CONAFE para realizar:'])
            insertar_residencia_aspirante(id_usuario, row['Código postal*:'], row['Estado*:'], row['Municipio o Alcaldía*:'], row['Localidad*:'] ,
                                        row['Colonia*:'], row['Calle*:'], row['Número exterior:'], row['Número interior:'] )
            insertar_info_bancaria_aspirante(id_usuario, row['Banco*:'], row['Cuenta bancaria:'], row['CLABE:'])
            insertar_documentos_aspirante(id_usuario,  row['Anexa el archivo PDF de tu certificado o constancia de último grado de estudios. Da clic en el icono siguiente*:'], 
                                        row['Anexa el archivo PDF de tu identificación oficial. Da clic en el icono siguiente*: '],
                                        row['Anexa el archivo PDF de la carátula de estado de cuenta bancaria que incluya nombre y domicilio del aspirante. Da clic en el icono siguiente*: '])
            insertar_participacion_aspirante(id_usuario, row['Estado en el que deseas participar*:'], row['Ciclo escolar a participar*:'] , row['Medio por el cuál te enteraste*:'],
                                            row['Municipio en el que desea brindar el servicio educativo:']  )
# Confirmar la transacción
conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()
