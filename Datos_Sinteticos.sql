USE CONAFE;
INSERT INTO `CCT` VALUES('CCT0001', 'CONAFE PRUEBA', 'CAMPECHE', '05000', 'PRUEBA 1', 'LOCAL 1', 'PRIMARIA', 'MATUTINO');
INSERT INTO `CCT` VALUES('CCT0002', 'CONAFE PRUEBA2', 'Estado de México', '05000', 'PRUEBA 1', 'LOCAL 1', 'PRIMARIA', 'MATUTINO');
INSERT INTO Usuario (correo, password, acceso) VALUES ('capacitador1@example.com', 'pass123', 'Capacitador');
select * from Usuario;
INSERT INTO Usuario (correo, password, acceso) VALUES ('capacitador2@example.com', 'securepass', 'Capacitador');

INSERT INTO Aspirante (
    id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, 
    apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud
)
VALUES (4, '5555555555', '5551234567', 'capacitador1@example.com', 'CURP1234567890ABC1', '30', 'Juan', 
 'Pérez', 'González', '1993-01-15', 'Masculino', 'Mexicana', 'Asignado');

INSERT INTO Aspirante (
    id_Aspirante, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, 
    apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud
)
VALUES (5, '5555555556', '5557654321', 'capacitador2@example.com', 'CURP0987654321DEF2', '28', 'María', 
 'López', 'Hernández', '1995-03-22', 'Femenino', 'Mexicana', 'Asignado');
 
INSERT INTO LEC (id_Usuario, estadoSalud, genero, edad, capacidadDiferente)
VALUES 
(4, 'Buena', 'Masculino', '30', 'Ninguna'),
(5, 'Excelente', 'Femenino', '28', 'Ninguna');

-- Insertar datos en la tabla CentroEducador usando los mismos id_Usuario de LEC
INSERT INTO CentroEducador (claveCentro, id_LEC)
VALUES 
('CCT0001', 4),
('CCT0002', 5);


INSERT INTO CCT (claveCentro, nombre, estado, codigoPostal, municipio, localidad, nivelEducativo, turno)
VALUES 
('CCT0004', 'CONAFE PRUEBAChihuahua', 'Chihuahua', '31000', 'Chihuahua', 'Centro', 'SECUNDARIA', 'VESPERTINO'),
('CCT0005', 'CONAFE PRUEBADurango 1', 'Durango', '34000', 'Durango', 'Guadiana', 'PRIMARIA', 'MATUTINO'),
('CCT0006', 'CONAFE PRUEBADurango 2', 'Durango', '34020', 'Durango', 'Analco', 'PREESCOLAR', 'VESPERTINO'),
('CCT0007', 'CONAFE PRUEBAEstadoMéxico', 'Estado de México', '52000', 'Toluca', 'Centro', 'SECUNDARIA', 'MATUTINO');


-- Crear nuevos usuarios
INSERT INTO Usuario (correo, password, acceso) 
VALUES 
('aspirante3@example.com', 'pass123', 'Capacitador'),
('aspirante4@example.com', 'pass123', 'Capacitador'),
('aspirante5@example.com', 'pass123', 'Capacitador'),
('aspirante6@example.com', 'pass123', 'Capacitador'),
('aspirante7@example.com', 'pass123', 'Capacitador');

-- Crear datos en Aspirante para cada usuario
INSERT INTO Aspirante (id_Aspirante, convocatoria, telefonoFijo, telefonoMovil, correo, curp, edad, nombres, apellidoPaterno, apellidoMaterno, fechaNacimiento, genero, nacionalidad, estado_solicitud)
VALUES 
(6, 1, '5551112233', '5551234567', 'aspirante3@example.com', 'CURP0000000000EX01', '25', 'Carlos', 'Jiménez', 'Martínez', '1998-05-12', 'Masculino', 'Mexicana', 'Asignado'),
(7, 1, '6141112233', '6147654321', 'aspirante4@example.com', 'CURP0000000000EX02', '29', 'Ana', 'Gómez', 'Pérez', '1994-08-24', 'Femenino', 'Mexicana', 'Asignado'),
(8, 1, '6181112233', '6181234567', 'aspirante5@example.com', 'CURP0000000000EX03', '22', 'Luis', 'Hernández', 'López', '1995-10-02', 'Masculino', 'Mexicana', 'Asignado'),
(9, 1, '6181113344', '6189876543', 'aspirante6@example.com', 'CURP0000000000EX04', '30', 'María', 'Sánchez', 'Torres', '1993-04-15', 'Femenino', 'Mexicana', 'Asignado'),
(10, 1, '7221112233', '7227654321', 'aspirante7@example.com', 'CURP0000000000EX05', '27', 'Jorge', 'López', 'García', '1996-01-30', 'Masculino', 'Mexicana', 'Asignado');

-- Crear datos en LEC para cada aspirante
INSERT INTO LEC (id_Usuario, estadoSalud, genero, edad, capacidadDiferente)
VALUES 
(6, 'Buena', 'Masculino', '25', 'Ninguna'),
(7, 'Regular', 'Femenino', '29', 'Ninguna'),
(8, 'Excelente', 'Masculino', '22', 'Ninguna'),
(9, 'Buena', 'Femenino', '30', 'Ninguna'),
(10, 'Buena', 'Masculino', '27', 'Ninguna');

-- Asignar a cada LEC un CentroEducador
INSERT INTO CentroEducador (claveCentro, id_LEC)
VALUES 
('CCT0006', 6),
('CCT0004', 7),
('CCT0005', 8),
('CCT0006', 9),
('CCT0007', 10);

SELECT * FROM CCT;

