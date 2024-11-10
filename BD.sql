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

SELECT * FROM `Usuario`;
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
    tallaCalzado NVARCHAR(20),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- ALTER TABLE EquipoAspirante
-- MODIFY COLUMN estatura NVARCHAR(20),
-- MODIFY COLUMN peso NVARCHAR(20),
-- MODIFY COLUMN tallaCalzado NVARCHAR(20);

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
INSERT INTO `CCT` VALUES('CCT0001', 'CONAFE PRUEBA', 'CAMPECHE', '05000', 'PRUEBA 1', 'LOCAL 1', 'PRIMARIA', 'MATUTINO');


-- Tabla: CentroEducador
CREATE TABLE CentroEducador (
    claveCentro NVARCHAR(50),
    id_LEC INT,
    FOREIGN KEY (claveCentro) REFERENCES CCT(claveCentro),
    FOREIGN KEY (id_LEC) REFERENCES LEC(id_Usuario)
);

-- Tabla: CapacitadorAspirante
CREATE TABLE CapacitadorAspirante (
    id_Capacitador INT,
    id_Aspirante INT,
    estadoCapacitacion NVARCHAR(50),
    fechaInicio DATE,
    fechaFinalizacion DATE,
    observaciones NVARCHAR(255),
    FOREIGN KEY (id_Capacitador) REFERENCES Usuario(id_Usuario),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

CREATE TABLE ActualizacionBD (
	id_Cambio INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    fechaCambio datetime
);

SELECT * FROM ConvocatoriaActual;

DELETE FROM ConvocatoriaActual WHERE id_Convo = 8;

INSERT INTO ConvocatoriaActual (nombre_convocatoria, url_convocatoria, url_forms, estado_convocatoria)
VALUES ('Convocatoria 2024', 'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'Cerrada');

INSERT INTO ConvocatoriaActual (nombre_convocatoria, url_convocatoria, url_forms, estado_convocatoria)
VALUES ('Convocatoria 2025', 'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'https://docs.google.com/forms/d/e/1FAIpQLSfQwO8uRMVa1xSL-neCetlOlfCK1sxyPZNGwektNPq6ZvxYBw/viewform?usp=sf_link', 
        'Cerrada');


/*
INSERT INTO Usuario (correo, password, acceso) VALUES ('capacitador1@example.com', 'pass123', 'Capacitador');

INSERT INTO Usuario (correo, password, acceso) VALUES ('capacitador2@example.com', 'securepass', 'Capacitador');

INSERT INTO Aspirante (
    id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, 
    apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud
)
VALUES (2, '5555555555', '5551234567', 'capacitador1@example.com', 'CURP1234567890ABC1', '30', 'Juan', 
 'Pérez', 'González', '1993-01-15', 'Masculino', 'Mexicana', 'Asignado');

INSERT INTO Aspirante (
    id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, 
    apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud
)
VALUES (3, '5555555556', '5557654321', 'capacitador2@example.com', 'CURP0987654321DEF2', '28', 'María', 
 'López', 'Hernández', '1995-03-22', 'Femenino', 'Mexicana', 'Asignado');
 
INSERT INTO LEC (id_Usuario, estadoSalud, genero, edad, capacidadDiferente)
VALUES 
(2, 'Buena', 'Masculino', '30', 'Ninguna'),
(3, 'Excelente', 'Femenino', '28', 'Ninguna');

-- Insertar datos en la tabla CentroEducador usando los mismos id_Usuario de LEC
INSERT INTO CentroEducador (claveCentro, id_LEC)
VALUES 
('CCT0001', 2),
('CCT0001', 3);
*/