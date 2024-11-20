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

-- SELECT * FROM `Aspirante`;
-- Tabla: LEC
CREATE TABLE LEC (
    id_Usuario INT,
    estadoSalud NVARCHAR(50),
    genero NVARCHAR(50),
    edad NVARCHAR(10),
    capacidadDiferente NVARCHAR(50),
    FOREIGN KEY (id_Usuario) REFERENCES Usuario(id_Usuario)
);

-- DROP TABLE ConvocatoriaActual;
CREATE TABLE ConvocatoriaActual (
	id_Convo INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    nombre_convocatoria NVARCHAR(100),
    url_convocatoria nvarchar(255),
    url_forms nvarchar(255),
    estado_convocatoria NVARCHAR(20)
);
-- SELECT * FROM ConvocatoriaActual;
-- Tabla: Aspirante
CREATE TABLE Aspirante (
    id_Aspirante INT PRIMARY KEY,
    convocatoria INT,
    telefonoFijo NVARCHAR(15),
    telefonoMovil NVARCHAR(15),
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
    FOREIGN KEY (id_Aspirante) REFERENCES Usuario(id_Usuario), -- Relación con Usuario
    FOREIGN KEY (convocatoria) REFERENCES ConvocatoriaActual(id_Convo) -- Relación con Usuario
);
SELECT * FROM `Aspirante`;
-- UPDATE `Aspirante` SET estado_solicitud = 'Pendiente' WHERE id_Aspirante = 1;
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
    turno NVARCHAR(50)
);

INSERT INTO `Usuario`(correo, password, acceso) VALUES('gutierrez.viveros.cristianr@gmail.com', '1234', 'Aspirante');



-- Tabla: CentroEducador
CREATE TABLE CentroEducador (
    claveCentro NVARCHAR(50),
    id_LEC INT,
    FOREIGN KEY (claveCentro) REFERENCES CCT(claveCentro),
    FOREIGN KEY (id_LEC) REFERENCES Usuario(id_Usuario)
);

-- Tabla: CapacitadorAspirante
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

CREATE TABLE ActualizacionBD (
	id_Cambio INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    fechaCambio datetime
);



INSERT INTO ConvocatoriaActual (nombre_convocatoria, url_convocatoria, url_forms, estado_convocatoria)
VALUES ('Convocatoria 2024', 'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'Cerrada');

INSERT INTO ConvocatoriaActual (nombre_convocatoria, url_convocatoria, url_forms, estado_convocatoria)
VALUES ('Convocatoria 2025', 'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'Cerrada');



INSERT INTO Usuario (correo, password, acceso) VALUES ('rabos@gmail.com', '1234', 'Aspirante');
INSERT INTO Usuario (correo, password, acceso) VALUES ('capacitador1@example.com', 'pass123', 'Capacitador');
INSERT INTO Usuario (correo, password, acceso) VALUES ('capacitador2@example.com', 'securepass', 'Capacitador');
INSERT INTO Usuario (correo, password, acceso) VALUES ('rubengmail.com', '1234', 'Aspirante');

INSERT INTO Aspirante (
    id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, 
    apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud
)
VALUES (1, '5555555555', '5551234567', 'capacitador1@example.com', 'CURP1234567890ABC1', '30', 'Juan', 
 'Pérez', 'González', '1993-01-15', 'Masculino', 'Mexicana', 'Asignado');

INSERT INTO Aspirante (
    id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, 
    apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud
)
VALUES (2, '5555555556', '5557654321', 'capacitador2@example.com', 'CURP0987654321DEF2', '28', 'María', 
 'López', 'Hernández', '1995-03-22', 'Femenino', 'Mexicana', 'Asignado');
 
INSERT INTO LEC (id_Usuario, estadoSalud, genero, edad, capacidadDiferente)
VALUES 
(1, 'Buena', 'Masculino', '30', 'Ninguna'),
(2, 'Excelente', 'Femenino', '28', 'Ninguna');

-- Insertar datos del CCT
INSERT INTO CCT (claveCentro, nombre, estado, codigoPostal, municipio, localidad, nivelEducativo, turno)
VALUES ('CCT0001', 'CONAFE PRUEBA1', 'Estado de México', '05000', 'NEZA', 'LOCAL 1', 'PRIMARIA', 'MATUTINO');
INSERT INTO CCT (claveCentro, nombre, estado, codigoPostal, municipio, localidad, nivelEducativo, turno)
VALUES ('CCT0002', 'CONAFE PRUEBA2', 'Estado de México', '05000', 'PRUEBA', 'LOCAL 2', 'PRIMARIA', 'MATUTINO');

-- Insertar datos en la tabla CentroEducador usando los mismos id_Usuario de LEC
INSERT INTO CentroEducador (claveCentro, id_LEC)
VALUES 
('CCT0001', 3),
('CCT0002', 4);

-- Insertar datos en la tabla CapacitadorAspirante
INSERT INTO FII (id_Capacitador, id_Aspirante, id_CCT, estadoCapacitacion, fechaInicio, fechaFinalizacion, observaciones)
VALUES (3, 1, 'CCT0001', 'En Inicio', '2024-11-01', '2024-12-01', 'Capacitación enfocada en liderazgo.');
INSERT INTO FII (id_Capacitador, id_Aspirante, id_CCT, estadoCapacitacion, fechaInicio, fechaFinalizacion, observaciones)
VALUES (3, 2, 'CCT0002', 'Finalizado', '2024-10-01', '2024-11-01', NULL);

# DROP TABLE alumno;
CREATE TABLE alumno (
    CURP NVARCHAR(16) PRIMARY KEY NOT NULL,
    nombres NVARCHAR(80),
    apellido_paterno NVARCHAR(50),
    apellido_materno NVARCHAR(50),
    fechaNacimiento DATE,
    nivel NVARCHAR(255),
    grado NVARCHAR(255)
);
select * from alumno;

CREATE TABLE CCTgrupos(
	id_grupo INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	id_CCT NVARCHAR(50),
	nombre_grupo NVARCHAR(20),
    FOREIGN KEY (id_CCT) REFERENCES CCT(claveCentro)
);
DROP TABLE alumnoCCT;
CREATE TABLE alumnoCCT(
	id_CCT NVARCHAR(50),
    id_alumno NVARCHAR(16),
    id_grupo INT,
    FOREIGN KEY (id_CCT) REFERENCES CCT(claveCentro),
    FOREIGN KEY (id_alumno) REFERENCES alumno(CURP),
    FOREIGN KEY (id_grupo) REFERENCES CCTgrupos(id_grupo)
)

ALTER TABLE CCT ADD COLUMN cupos_disponibles INT DEFAULT 5;

-- NOTA DE VERIFICAR LA PARTE DE LA CONCORDANCIA ENTRE LOS GRUPOS Y LOS CCT PARA QUE NO VAYA A CHOCAR CON LAS TABLAS CREADAS INDIVIDUALMENTE

CREATE TABLE AsignacionAspiranteCCT (
    id_asignacion INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    id_Aspirante INT,
    claveCentro NVARCHAR(50),
    fecha_asignacion DATE,
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante),
    FOREIGN KEY (claveCentro) REFERENCES CCT(claveCentro)
);

-- DATOS GENERADOS PARA REALIZAR PRUEBAS PARA LA ASIGNACION DE CCT

INSERT INTO CCT (claveCentro, nombre, estado, codigoPostal, municipio, localidad, nivelEducativo, turno, cupos_disponibles)
VALUES
('CCT001', 'Escuela Primaria Benito Juárez', 'Estado 1', '12345', 'Municipio 1', 'Localidad 1', 'Primaria', 'Matutino', 5),
('CCT002', 'Escuela Secundaria General No. 2', 'Estado 2', '67890', 'Municipio 2', 'Localidad 2', 'Secundaria', 'Vespertino', 3),
('CCT003', 'Colegio de Bachilleres Plantel 1', 'Estado 1', '11223', 'Municipio 3', 'Localidad 3', 'Bachillerato', 'Matutino', 0),
('CCT004', 'Escuela Telesecundaria 15', 'Estado 3', '44556', 'Municipio 4', 'Localidad 4', 'Secundaria', 'Matutino', 2),
('CCT005', 'Escuela Primaria Emiliano Zapata', 'Estado 2', '77889', 'Municipio 5', 'Localidad 5', 'Primaria', 'Vespertino', 4);

SELECT * FROM CCT WHERE nivelEducativo='Bachillerato';

INSERT INTO Usuario (correo, password, acceso)
VALUES
('aspirante1@gmail.com', 'password1', 'Aspirante'),
('aspirante2@gmail.com', 'password2', 'Aspirante'),
('aspirante3@gmail.com', 'password3', 'Aspirante'),
('aspirante4@gmail.com', 'password4', 'Aspirante');

SELECT * FROM Usuario;
SELECT * FROM Aspirante;
SELECT * FROM AsignacionAspiranteCCT;
SELECT * FROM ConvocatoriaActual;

INSERT INTO Aspirante (id_Aspirante, convocatoria, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud)
VALUES
(4, 1, '5551234567', '5557654321', 'aspirante1@gmail.com', 'CURP001', '25', 'Juan', 'Pérez', 'Gómez', '1998-05-10', 'Masculino', 'Mexicana', 'Finalizado'),
(5, 1, '5559876543', '5553456789', 'aspirante2@gmail.com', 'CURP002', '30', 'María', 'López', 'Hernández', '1993-07-15', 'Femenino', 'Mexicana', 'Finalizado'),
(6, 2, '5558765432', '5552345678', 'aspirante3@gmail.com', 'CURP003', '28', 'Carlos', 'Ramírez', 'Martínez', '1995-03-20', 'Masculino', 'Mexicana', 'Finalizado'),
(7, 2, '5557654321', '5551234567', 'aspirante4@gmail.com', 'CURP004', '22', 'Ana', 'Torres', 'Núñez', '2001-11-30', 'Femenino', 'Mexicana', 'Finalizado');

INSERT INTO ResidenciaAspirante (id_Aspirante, codigoPostal, estado, municipio, localidad, colonia, calle, numeroExterior, numeroInterior)
VALUES
(4, '12345', 'Estado 1', 'Municipio 1', 'Localidad 1', 'Colonia 1', 'Calle 1', '10', '1A'),
(5, '67890', 'Estado 2', 'Municipio 2', 'Localidad 2', 'Colonia 2', 'Calle 2', '20', NULL),
(6, '11223', 'Estado 1', 'Municipio 3', 'Localidad 3', 'Colonia 3', 'Calle 3', '30', NULL),
(7, '44556', 'Estado 3', 'Municipio 4', 'Localidad 4', 'Colonia 4', 'Calle 4', '40', '2B');

INSERT INTO InfoEducativaAspirante (id_Aspirante, fechaSolicitud, nivelEducativo, lenguaIndigena, pregunta1, pregunta2, pregunta3, pregunta4, pregunta5, pregunta6, pregunta7, pregunta8, pregunta9)
VALUES
(4, '2024-01-10', 'Primaria', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí'),
(5, '2024-01-12', 'Secundaria', 'Sí', 'Sí', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No'),
(6, '2024-01-15', 'Bachillerato', 'No', 'No', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí', 'No', 'Sí'),
(7, '2024-01-18', 'Primaria', 'No', 'Sí', 'Sí', 'Sí', 'Sí', 'Sí', 'No', 'No', 'Sí', 'Sí');

SELECT id_Aspirante, CONCAT(nombres, ' ', apellidoPaterno, ' ', apellidoMaterno) AS nombre_completo
FROM Aspirante
WHERE estado_solicitud = 'Finalizado';