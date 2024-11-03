CREATE DATABASE CONAFE;
USE CONAFE;

-- Tabla: Usuario
CREATE TABLE Usuario (
    id_Usuario INT PRIMARY KEY,
    password NVARCHAR(50),
    nombreUsuario NVARCHAR(50),
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

-- Tabla: Aspirante
CREATE TABLE Aspirante (
    id_Aspirante INT PRIMARY KEY,
    telefonoFijo NVARCHAR(15),
    telefonoMovil NVARCHAR(15),
    correo NVARCHAR(50),
    curp NVARCHAR(18),
    nombres NVARCHAR(50),
    apellidoPaterno NVARCHAR(50),
    apellidoMaterno NVARCHAR(50),
    fechaNacimiento DATE,
    genero NVARCHAR(10),
    nacionalidad NVARCHAR(50),
    FOREIGN KEY (id_Aspirante) REFERENCES Usuario(id_Usuario) -- Relación con Usuario
);

-- Tabla: EquipoAspirante
CREATE TABLE EquipoAspirante (
    id_Aspirante INT,
    estatura NVARCHAR(10),
    peso NVARCHAR(10),
    edad NVARCHAR(10),
    tallaPlayera NVARCHAR(10),
    tallaPantalon NVARCHAR(10),
    tallaCalzado NVARCHAR(10),
    FOREIGN KEY (id_Aspirante) REFERENCES Aspirante(id_Aspirante)
);

-- Tabla: InfoEducativaAspirante
CREATE TABLE InfoEducativaAspirante (
    id_Aspirante INT,
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
    certificado NVARCHAR(50),
    identificacion NVARCHAR(50),
    estadoDeCuenta NVARCHAR(50),
    municipio NVARCHAR(50),
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
    Field NVARCHAR(50)
);

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