from flask import Flask, request, jsonify
from flask_cors import CORS  
import pyodbc

app = Flask(__name__)
CORS(app)  

# Conexión a la base de datos
def get_db_connection():
    # Configura los detalles de la conexión
    SERVER = 'conafe-server.database.windows.net'  # Servidor
    DATABASE = 'conafe-database'                  # Nombre de la base de datos
    USERNAME = 'admin-conafe'                     # Usuario administrador
    PASSWORD = 'MateriaAcaba08/01/25'             # Contraseña
    DRIVER = '{ODBC Driver 17 for SQL Server}'    # Driver ODBC

    conn = pyodbc.connect(
        f'DRIVER={DRIVER};SERVER={SERVER};PORT=1433;DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    )
    return conn

@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.form.to_dict()
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO Usuario (correo, password, acceso)
            VALUES (?, ?, 'Aspirante')
        """, (data['email'], 'default_password'))
        # Obtener el último ID insertado
        connection.commit()  # Asegúrate de hacer commit del INSERT antes de continuar
        
        cursor.execute("""
            SELECT id_Usuario FROM Usuario WHERE correo = ?
        """, (data['email'],))
        row = cursor.fetchone()
        if row:
            id_usuario = row[0]
            print(f"ID Usuario recuperado: {id_usuario}")
        else:
            print("No se pudo recuperar el ID del usuario.")
            return jsonify({'message': 'Error interno del servidor: No se pudo recuperar el ID del usuario.'}), 500
                
        cursor.execute("""
            INSERT INTO Aspirante (
                id_Aspirante, convocatoria, telefonoFijo, telefonoMovil, correo,
                curp, edad, nombres, apellidoPaterno, apellidoMaterno, fechaNacimiento,
                genero, nacionalidad, estado_solicitud
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pendiente')
        """, (
            id_usuario, 1, data['telefono-fijo'], data['telefono-movil'], data['email'],
            data['curp'], data['edad'], data['nombre'], data['apellido1'], data['apellido2'],
            data['fecha_nacimiento'], data['genero'], data['nacionalidad']
        ))
        connection.commit()

        cursor.execute("""
            INSERT INTO EquipoAspirante (id_Aspirante, estatura, peso, tallaPlayera, tallaPantalon)
            VALUES (?, ?, ?, ?, ?)
        """, (
            id_usuario, data['estatura'], data['peso'], data['playera'], data['pantalon']
        ))
        connection.commit()

        cursor.execute("""
            INSERT INTO ResidenciaAspirante (
                id_Aspirante, codigoPostal, estado, municipio, localidad, colonia,
                calle, numeroExterior, numeroInterior
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_usuario, data['codigo-postal'], data['estado'], data['municipio'], data['localidad'],
            data['colonia'], data['calle'], data['numero-exterior'], data.get('numero-interior', None)
        ))
        connection.commit()

        cursor.execute("""
            INSERT INTO InfoEducativaAspirante (
                id_Aspirante, nivelEducativo, lenguaIndigena, pregunta1, pregunta2,
                pregunta3, pregunta4, pregunta5, pregunta6, pregunta7
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_usuario,
            data['NivelEdu'],
            data['LengIndi'],
            ','.join(request.form.getlist('pregunta1')),
            ','.join(request.form.getlist('pregunta2')),
            data['pregunta3'],
            data['pregunta4'],
            data['pregunta5'],
            data['pregunta6'],
            data['pregunta7']
        ))
        connection.commit()

        cursor.execute("""
            INSERT INTO InfoBancariaAspirante (id_Aspirante, nombreBanco, cuentaBancaria)
            VALUES (?, ?, ?)
        """, (
            id_usuario, data['banco'], data.get('cuenta BBVA') or data.get('cuenta-otro', None)
        ))
        connection.commit()

        certificado = request.files['certificado']
        identificacion = request.files['identificacion']
        estado_cuenta = request.files['estado-cuenta']

        certificado_path = f"uploads/certificados/{certificado.filename}"
        identificacion_path = f"uploads/identificaciones/{identificacion.filename}"
        estado_cuenta_path = f"uploads/estados_cuenta/{estado_cuenta.filename}"

        certificado.save(certificado_path)
        identificacion.save(identificacion_path)
        estado_cuenta.save(estado_cuenta_path)

        cursor.execute("""
            INSERT INTO DocumentosAspirante (id_Aspirante, certificado, identificacion, estadoDeCuenta)
            VALUES (?, ?, ?, ?)
        """, (
            id_usuario, certificado_path, identificacion_path, estado_cuenta_path
        ))
        connection.commit()


        return jsonify({'message': 'Registro exitoso'}), 200

    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500
    finally:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)