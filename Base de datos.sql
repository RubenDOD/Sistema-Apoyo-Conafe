-- Este es el script que se encarga de crear la base de datos

DROP DATABASE IF EXISTS CONAFE;
CREATE DATABASE CONAFE;
USE CONAFE;

-- Tabla: Usuario
CREATE TABLE Usuario (
    id_Usuario INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    correo NVARCHAR(50),
    password NVARCHAR(50),
    acceso NVARCHAR(50)
);

-- Tabla: LEC
CREATE TABLE LEC (
    id_Usuario INT,
    estadoSalud NVARCHAR(50),
    genero NVARCHAR(50),
    edad NVARCHAR(10),
    capacidadDiferente NVARCHAR(50),
    FOREIGN KEY (id_Usuario) REFERENCES Usuario(id_Usuario)
);

-- Tabla: ConvocatoriaActual
CREATE TABLE ConvocatoriaActual (
    id_Convo INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nombre_convocatoria NVARCHAR(100),
    url_convocatoria NVARCHAR(255),
    url_forms NVARCHAR(255),
    estado_convocatoria NVARCHAR(20)
);

-- Tabla: Aspirante
CREATE TABLE Aspirante (
    id_Aspirante INT PRIMARY KEY,
    convocatoria INT,
    telefonoFijo NVARCHAR(30),
    telefonoMovil NVARCHAR(30),
    correo NVARCHAR(50),
    curp NVARCHAR(18), 
    edad NVARCHAR(10),
    nombres NVARCHAR(50),
    apellidoPaterno NVARCHAR(50),
    apellidoMaterno NVARCHAR(50),
    fechaNacimiento DATE,
    genero NVARCHAR(10),
    nacionalidad NVARCHAR(50),
    estado_solicitud NVARCHAR(10),
    FOREIGN KEY (id_Aspirante) REFERENCES Usuario(id_Usuario),
    FOREIGN KEY (convocatoria) REFERENCES ConvocatoriaActual(id_Convo)
);

-- Tabla: EquipoAspirante
CREATE TABLE EquipoAspirante (
    id_Aspirante INT,
    estatura NVARCHAR(10),
    peso NVARCHAR(10),
    tallaPlayera NVARCHAR(20),
    tallaPantalon NVARCHAR(20),
    tallaCalzado NVARCHAR(10),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: InfoEducativaAspirante
CREATE TABLE InfoEducativaAspirante (
    id_Aspirante INT,
    fechaSolicitud datetime,
    nivelEducativo NVARCHAR(50),
    lenguaIndigena NVARCHAR(50),
    pregunta1 NVARCHAR(255),
    pregunta2 NVARCHAR(255),
    pregunta3 NVARCHAR(255),
    pregunta4 NVARCHAR(255),
    pregunta5 NVARCHAR(255),
    pregunta6 NVARCHAR(255),
    pregunta7 NVARCHAR(255),
    pregunta8 NVARCHAR(255),
    pregunta9 NVARCHAR(255),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: ResidenciaAspirante
CREATE TABLE ResidenciaAspirante (
    id_Aspirante INT,
    codigoPostal NVARCHAR(10),
    estado NVARCHAR(50),
    municipio NVARCHAR(50),
    localidad NVARCHAR(50),
    colonia NVARCHAR(50),
    calle NVARCHAR(50),
    numeroExterior NVARCHAR(10),
    numeroInterior NVARCHAR(10),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: InfoBancariaAspirante
CREATE TABLE InfoBancariaAspirante (
    id_Aspirante INT,
    nombreBanco NVARCHAR(50),
    cuentaBancaria NVARCHAR(20),
    clabe NVARCHAR(20),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: DocumentosAspirante
CREATE TABLE DocumentosAspirante (
    id_Aspirante INT,
    certificado NVARCHAR(255),
    identificacion NVARCHAR(255),
    estadoDeCuenta NVARCHAR(255),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: ParticipacionAspirante
CREATE TABLE ParticipacionAspirante (
    id_Aspirante INT,
    estado NVARCHAR(50),
    cicloEscolar NVARCHAR(10),
    medioDeEnterarse NVARCHAR(50),
    municipio NVARCHAR(50),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: CCT
CREATE TABLE CCT (
    claveCentro NVARCHAR(50) PRIMARY KEY,
    nombre NVARCHAR(50),
    estado NVARCHAR(50),
    codigoPostal NVARCHAR(10),
    municipio NVARCHAR(50),
    localidad NVARCHAR(50),
    nivelEducativo NVARCHAR(50),
    turno NVARCHAR(50),
    cupos_disponibles INT DEFAULT 3,
	latitud DECIMAL(9, 6),  -- Almacena la latitud en formato decimal
    longitud DECIMAL(9, 6) -- Almacena la longitud en formato decimal
);



-- Tabla: CentroEducador
CREATE TABLE CentroEducador (
    claveCentro NVARCHAR(50),
    id_LEC INT,
    FOREIGN KEY (claveCentro) REFERENCES CCT(claveCentro),
    FOREIGN KEY (id_LEC) REFERENCES Usuario(id_Usuario)
);

-- Tabla: FII (CapacitadorAspirante)
CREATE TABLE FII (
    id_Capacitador INT,
    id_Aspirante INT,
    id_CCT NVARCHAR(50),
    estadoCapacitacion NVARCHAR(50),
    fechaInicio DATE,
    fechaFinalizacion DATE,
    observaciones NVARCHAR(255),
    FOREIGN KEY (id_Capacitador) REFERENCES Usuario(id_Usuario),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante),
    FOREIGN KEY (id_CCT) REFERENCES CCT(claveCentro)
);

-- Tabla: alumno
CREATE TABLE alumno (
    CURP NVARCHAR(18) PRIMARY KEY NOT NULL,
    nombres NVARCHAR(80),
    apellido_paterno NVARCHAR(50),
    apellido_materno NVARCHAR(50),
    fechaNacimiento DATE,
    nivel NVARCHAR(255),
    grado NVARCHAR(255)
);

ALTER TABLE alumno MODIFY COLUMN CURP NVARCHAR(18) NOT NULL;

-- Tabla: Materias
CREATE TABLE Materias (
    id_materia INT AUTO_INCREMENT PRIMARY KEY,
    nombre_materia VARCHAR(100) NOT NULL
);

-- Tabla Calificaciones
CREATE TABLE Calificaciones (
    id_calificacion INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno NVARCHAR(18) NOT NULL,
    id_materia INT NOT NULL,
    calificacion DECIMAL(5, 2) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_alumno) REFERENCES alumno(CURP),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia)
);

-- ALTER TABLE Calificaciones MODIFY COLUMN id_alumno NVARCHAR(18) NOT NULL;

-- Tabla: CCTgrupos
CREATE TABLE CCTgrupos (
    id_grupo INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_CCT NVARCHAR(50),
    nombre_grupo NVARCHAR(20),
    id_profesor INT,
    nivel NVARCHAR(15),
    grado NVARCHAR(15),
    FOREIGN KEY (id_CCT) REFERENCES CCT(claveCentro),
	FOREIGN KEY (id_profesor) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: alumnoCCT
CREATE TABLE alumnoCCT (
    id_CCT NVARCHAR(50),
    id_alumno NVARCHAR(18),
    id_grupo INT DEFAULT NULL,
    FOREIGN KEY (id_CCT) REFERENCES CCT(claveCentro),
    FOREIGN KEY (id_alumno) REFERENCES alumno(CURP),
    FOREIGN KEY (id_grupo) REFERENCES CCTgrupos(id_grupo)
);
ALTER TABLE alumnoCCT MODIFY COLUMN id_alumno NVARCHAR(18);

-- Tabla: AsignacionAspiranteCCT
CREATE TABLE AsignacionAspiranteCCT (
    id_asignacion INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_Aspirante INT,
    claveCentro NVARCHAR(50),
    fecha_asignacion DATE,
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante),
    FOREIGN KEY (claveCentro) REFERENCES CCT(claveCentro)
);

-- Tabla: ActualizacionBD
CREATE TABLE ActualizacionBD (
    id_Cambio INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    fechaCambio DATETIME,
    descripcion NVARCHAR(255)
);

CREATE TABLE AreaControlEscolar(
	id_ACT INT PRIMARY KEY NOT NULL,
	CCT NVARCHAR(50),
    FOREIGN KEY (CCT) REFERENCES CCT(claveCentro),
    FOREIGN KEY (id_ACT) REFERENCES Usuario(id_Usuario)
);

-- -----------------------------  Ejecutar esto para equipamiento y tallas    -----------------------------------------------------------

CREATE TABLE tallasPromedio (
    ID INT AUTO_INCREMENT PRIMARY KEY,  -- Identificador único para cada registro
    ESTADO VARCHAR(255) NOT NULL,       -- Nombre del estado
    CUERPO_CHICO INT NOT NULL,          -- Talla pequeña del cuerpo
    CUERPO_MEDIANO INT NOT NULL,        -- Talla mediana del cuerpo
    CUERPO_GRANDE INT NOT NULL,         -- Talla grande del cuerpo
    CALZADO_H_MENOR INT NOT NULL,       -- Talla menor de calzado masculino
    CALZADO_H_MEDIO INT NOT NULL,       -- Talla media de calzado masculino
    CALZADO_H_MAYOR INT NOT NULL,       -- Talla mayor de calzado masculino
    CALZADO_M_MENOR INT NOT NULL,       -- Talla menor de calzado femenino
    CALZADO_M_MEDIO INT NOT NULL,       -- Talla media de calzado femenino
    CALZADO_M_MAYOR INT NOT NULL        -- Talla mayor de calzado femenino
);
INSERT INTO tallasPromedio (
    ESTADO, 
    CUERPO_CHICO, CUERPO_MEDIANO, CUERPO_GRANDE, 
    CALZADO_H_MENOR, CALZADO_H_MEDIO, CALZADO_H_MAYOR, 
    CALZADO_M_MENOR, CALZADO_M_MEDIO, CALZADO_M_MAYOR
)
VALUES
(
    'Durango', 
    25, 35, 40,   -- Tallas del cuerpo
    10, 65, 25,   -- Tallas de calzado masculino
    10, 70, 20    -- Tallas de calzado femenino
);
INSERT INTO tallasPromedio (
    ESTADO, 
    CUERPO_CHICO, CUERPO_MEDIANO, CUERPO_GRANDE, 
    CALZADO_H_MENOR, CALZADO_H_MEDIO, CALZADO_H_MAYOR, 
    CALZADO_M_MENOR, CALZADO_M_MEDIO, CALZADO_M_MAYOR
)
VALUES
(
    'Campeche', 
    25, 40, 35,   -- Tallas del cuerpo
    25, 50, 25,   -- Tallas de calzado masculino
    26, 62, 12    -- Tallas de calzado femenino
);


UPDATE CCT SET latitud=18.15556,longitud=-90.62306 WHERE claveCentro='CCT-1273-163';
UPDATE CCT SET latitud=18.21639,longitud=-90.87972 WHERE claveCentro='CCT-7402-632';
UPDATE CCT SET latitud=17.96889,longitud=-90.83556 WHERE claveCentro='CCT-7548-461';
UPDATE CCT SET latitud=19.68806,longitud=-90.46083 WHERE claveCentro='CCT-4016-580';
UPDATE CCT SET latitud=19.71333,longitud=-90.52361 WHERE claveCentro='CCT-1623-869';
UPDATE CCT SET latitud=18.19722,longitud=-90.65333 WHERE claveCentro='CCT-4597-168';

INSERT INTO Usuario (correo, password, acceso) VALUES ('equipamiento@gmail.com', '12345678', 'Departamento Equipamiento');

-- --------------------------- Para lo de apoyo economico ----------------------------------------

CREATE TABLE apoyo_economico(
    id_apoyo int primary key auto_increment,
    tipo_apoyo varchar(200),
    monto_apoyo int,
    fecha_inicio date,
    periodo_entrega_meses int,
    meses_entrega JSON,
    claveApoyo varchar(30)
);

-- Tabla apoyo_educador
CREATE TABLE apoyo_educador (
    id_apoyo int,
    id_educador int,
    estado_apoyo varchar(50),
    observaciones varchar(255),
    numero_cuenta varchar(20),
    fecha_pago date,
    FOREIGN KEY (id_apoyo) REFERENCES apoyo_economico(id_apoyo),
    FOREIGN KEY (id_educador) REFERENCES Usuario(id_Usuario)
);

-- --------------------------------------------------------------------------------------

-- REINICIAR
DELETE FROM AsignacionAspiranteCCT;
DELETE FROM FII;
UPDATE Aspirante SET estado_solicitud='Aceptado' WHERE id_Aspirante=10;
SELECT * FROM Aspirante;
SELECT * FROM FII;
UPDATE Usuario SET acceso='Aspirante' WHERE id_Usuario=10;

SELECT * FROM CCT;
UPDATE CCT SET cupos_disponibles=3 WHERE claveCentro='CCT-4597-168';

-- SELECTs
SELECT * FROM Usuario;
SELECT * FROM Aspirante;
SELECT * FROM CCT WHERE claveCentro = 'CCT-4597-168';
SELECT * FROM AsignacionAspiranteCCT;

SELECT Aspirante.id_Aspirante AS id, 
       CONCAT(Aspirante.nombres, ' ', Aspirante.apellidoPaterno, ' ', Aspirante.apellidoMaterno) AS nombre
FROM AsignacionAspiranteCCT
JOIN Aspirante ON AsignacionAspiranteCCT.id_Aspirante = Aspirante.id_Aspirante
WHERE AsignacionAspiranteCCT.claveCentro = 'CCT-4597-168';

SELECT * FROM CCTGrupos;
DELETE FROM CCTGrupos WHERE id_grupo = 4;
UPDATE CCTGrupos SET id_profesor=null WHERE id_profesor=10;
UPDATE CCTGrupos SET id_profesor=null WHERE id_profesor=10;

SELECT * FROM CentroEducador;
SELECT * FROM AsignacionAspiranteCCT;
SELECT * FROM calificaciones;
SELECT * FROM alumno;
delete from calificaciones;
delete from CCTGrupos;

SELECT * FROM Aspirante;
SELECT * FROM CentroEducador where id_LEC=10;
SELECT * FROM FII;
SELECT * FROM AsignacionAspiranteCCT;
SELECT * FROM CCTGrupos;
SELECT * FROM alumnoCCT;