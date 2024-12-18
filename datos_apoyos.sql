-- CREATE DATABASE conafe_prueba;
USE CONAFE;

-- Insertar datos sintéticos en la tabla AsignacionAspiranteCCT
DELETE FROM AsignacionAspiranteCCT;
INSERT INTO AsignacionAspiranteCCT (id_Aspirante, claveCentro, fecha_asignacion)
VALUES
(19, 'CCT-3289-487', '2024-01-10'),
(20, 'CCT-2069-952', '2024-01-15'),
(21, 'CCT-4028-241', '2024-02-01'),
(22, 'CCT-4002-641', '2024-02-05'),
(23, 'CCT-9159-878', '2024-02-20'),
(23, 'CCT-5251-214', '2024-03-01'),
(24, 'CCT-3988-927', '2024-03-10'),
(25, 'CCT-5748-795', '2024-03-15'),
(26, 'CCT-7945-326', '2024-04-01'),
(27, 'CCT-4933-945', '2024-04-10'),
(28, 'CCT-4933-945', '2024-05-01'),
(29, 'CCT-4933-945', '2024-05-15');

DROP TABLE IF EXISTS apoyo_educador;

DROP TABLE IF EXISTS apoyo_economico;

CREATE TABLE apoyo_economico(
    id_apoyo int primary key auto_increment,
    tipo_apoyo varchar(200),
    monto_apoyo int,
    fecha_inicio date,
    periodo_entrega_meses int,
    meses_entrega JSON,
    claveApoyo varchar(30)
);

-- Datos de prueba
-- Insertar datos de apoyos económicos desde el PDF
INSERT INTO apoyo_economico (tipo_apoyo, monto_apoyo, fecha_inicio, periodo_entrega_meses, meses_entrega, claveApoyo)
VALUES
-- Educador Comunitario de Inicial (EC)
('Educador Comunitario de Inicial (EC)', 2603, '2024-01-01', 12, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'EC inicial'),

-- Educador Comunitario de Preescolar, Primaria y Secundaria (EC)
('Educador Comunitario de Preescolar, Primaria y Secundaria (EC)', 4684, '2024-01-01', 12, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'EC otros'),

-- Educador Comunitario de Acompañamiento (ECA)
('Educador Comunitario de Acompañamiento (ECA)', 6455, '2024-01-01', 12, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'ECA'),

-- Educador Comunitario de Acompañamiento Regional (ECAR)
('Educador Comunitario de Acompañamiento Regional (ECAR)', 8803, '2024-01-01', 12, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'ECAR'),

-- Ex-líder para la educación comunitaria preescolar y primaria
('Ex-líder para la educación comunitaria preescolar y primaria', 1020, '2024-01-01', 10, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'Ex-líder'),

-- Ex-líder para la educación comunitaria secundaria y otros
('Ex-líder para la educación comunitaria secundaria y otros', 1240, '2024-01-01', 10, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'Ex-líder otros'),

-- Apoyo económico paralelo para la continuidad de estudios
('Apoyo económico paralelo para la continuidad de estudios', 1242, '2024-01-01', 12, '["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]', 'Continuidad');


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

-- Insertar los apoyos para los educadores basados en el nivel educativo del CCT asignado
INSERT INTO apoyo_educador (id_apoyo, id_educador, estado_apoyo, observaciones, numero_cuenta)
SELECT 
    CASE 
        WHEN c.nivelEducativo = 'Inicial' THEN (SELECT id_apoyo FROM apoyo_economico WHERE tipo_apoyo = 'Educador Comunitario de Inicial (EC)' LIMIT 1)
        WHEN c.nivelEducativo IN ('Preescolar', 'Primaria', 'Secundaria') THEN (SELECT id_apoyo FROM apoyo_economico WHERE tipo_apoyo = 'Educador Comunitario de Preescolar, Primaria y Secundaria (EC)' LIMIT 1)
        ELSE NULL
    END AS id_apoyo,
    aac.id_Aspirante AS id_educador,
    'Asignado' AS estado_apoyo,
    NULL AS observaciones,
    NULL AS numero_cuenta
FROM AsignacionAspiranteCCT aac
JOIN CCT c ON aac.claveCentro = c.claveCentro
WHERE c.nivelEducativo IN ('Inicial', 'Preescolar', 'Primaria', 'Secundaria');


-- Cambiar algunos roles para que haya LECs
UPDATE usuario SET acceso = 'LEC' where id_Usuario  between 19 and 40;

-- Agregar usuario de departamento de becas
INSERT INTO Usuario (correo, password, acceso) VALUES ('becas@example.com', '12345678', 'Departamento Becas');
