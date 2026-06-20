-- ============================================================
--  DATOS DE PRUEBA - biblioteca1
--  Mínimo 50 registros distribuidos entre las tablas principales
--  Contexto: Biblioteca en Ilo, Moquegua, Perú
--  Ejecutar en phpMyAdmin sobre la base `biblioteca1`
-- ============================================================

USE biblioteca1;

-- ============================================================
-- 1. SUCURSALES
-- ============================================================
INSERT INTO sucursales (nombre, calle, ciudad, telefono) VALUES
    ('Biblioteca Central Ilo',     'Av. Costanera 245',        'Ilo',      '053-481200'),
    ('Sucursal El Algarrobal',     'Jr. Los Laureles 112',     'Ilo',      '053-481350'),
    ('Sucursal Moquegua Centro',   'Calle Moquegua 318',       'Moquegua', '053-462100'),
    ('Sucursal Pacocha',           'Av. Industrial 89',        'Ilo',      '053-481490'),
    ('Sucursal Mariscal Nieto',    'Jr. Ayacucho 501',         'Moquegua', '053-463200');

-- ============================================================
-- 2. PERSONAS (base para usuarios y empleados)
-- ============================================================
INSERT INTO personas (nombre, email, phone) VALUES
-- Futuros usuarios (15 personas)
    ('Ivan Alvaro Ccaso Carbajal',  'ivan@biblioteca.com',          '987654321'),
    ('Laura Beatriz Bozzo Peralta', 'laura.bozzo@gmail.com',        '976543210'),
    ('Carlos Ramirez Quispe',       'carlos.ramirez@gmail.com',     '965432109'),
    ('María Elena Huanca Flores',   'maria.huanca@hotmail.com',     '954321098'),
    ('Jorge Luis Apaza Mamani',     'jorge.apaza@gmail.com',        '943210987'),
    ('Ana Lucía Condori Torres',    'ana.condori@outlook.com',      '932109876'),
    ('Pedro Pablo Quispe Ramos',    'pedro.quispe@gmail.com',       '921098765'),
    ('Rosa Isabel Mamani Coyla',    'rosa.mamani@gmail.com',        '910987654'),
    ('Luis Alberto Calle Vargas',   'luis.calle@hotmail.com',       '909876543'),
    ('Carmen Rosa Huayhua Puma',    'carmen.huayhua@gmail.com',     '998765432'),
    ('Diego Armando Lajo Pinto',    'diego.lajo@gmail.com',         '987654320'),
    ('Sofía Alejandra Cruz Meza',   'sofia.cruz@outlook.com',       '976543219'),
    ('Roberto Carlos Tito Suni',    'roberto.tito@gmail.com',       '965432108'),
    ('Patricia Luz Flores Catari',  'patricia.flores@gmail.com',    '954321097'),
    ('Miguel Ángel Ramos Huanca',   'miguel.ramos@hotmail.com',     '943210986'),
-- Futuros empleados (5 personas)
    ('Elena Victoria Puma Ticona',  'elena.puma@biblioteca.pe',     '932109875'),
    ('Julio César Mamani Quispe',   'julio.mamani@biblioteca.pe',   '921098764'),
    ('Sandra Paola Roque Flores',   'sandra.roque@biblioteca.pe',   '910987653'),
    ('Fernando José Lajo Cruz',     'fernando.lajo@biblioteca.pe',  '999888777'),
    ('Valeria Rosa Ccoa Apaza',     'valeria.ccoa@biblioteca.pe',   '988777666');

-- ============================================================
-- 3. USUARIOS (id_persona 1-15, id_rol=3=Usuario)
-- ============================================================
INSERT INTO usuarios (id_persona, edad, id_membresia, id_rol) VALUES
    (1,  27, 2, 3),   -- Ivan, Estándar
    (2,  35, 3, 3),   -- Laura, Premium
    (3,  22, 1, 3),   -- Carlos, Básica
    (4,  41, 2, 3),   -- María, Estándar
    (5,  19, 1, 3),   -- Jorge, Básica
    (6,  30, 3, 3),   -- Ana, Premium
    (7,  25, 2, 3),   -- Pedro, Estándar
    (8,  38, 1, 3),   -- Rosa, Básica
    (9,  45, 3, 3),   -- Luis, Premium
    (10, 28, 2, 3),   -- Carmen, Estándar
    (11, 17, 1, 3),   -- Diego, Básica
    (12, 33, 2, 3),   -- Sofía, Estándar
    (13, 52, 3, 3),   -- Roberto, Premium
    (14, 24, 1, 3),   -- Patricia, Básica
    (15, 60, 2, 3);   -- Miguel, Estándar

-- ============================================================
-- 4. EMPLEADOS (id_persona 16-20)
-- ============================================================
INSERT INTO empleados (id_persona, cargo, id_sucursal) VALUES
    (16, 'Bibliotecaria Jefe',  1),
    (17, 'Bibliotecario',       2),
    (18, 'Auxiliar',            3),
    (19, 'Recepcionista',       4),
    (20, 'Auxiliar',            5);

-- ============================================================
-- 5. LIBROS (20 libros, distintas categorías)
-- ============================================================
INSERT INTO libros (ISBN, titulo, autor, editorial, anio_publicacion, id_categoria, id_estado) VALUES
    ('978-9500302371', 'Cien años de soledad',             'Gabriel García Márquez',  'Sudamericana',     1967, 1, 1),
    ('978-8499893501', 'El Señor de los Anillos',          'J.R.R. Tolkien',          'Minotauro',        1954, 1, 1),
    ('978-9874373700', '1984',                             'George Orwell',            'Penguin',          1949, 1, 1),
    ('978-9876547531', 'Sapiens',                          'Yuval Noah Harari',        'Debate',           2011, 2, 1),
    ('978-8484326441', 'Breve historia del tiempo',        'Stephen Hawking',          'Crítica',          1988, 2, 1),
    ('978-8408117117', 'El gen egoísta',                   'Richard Dawkins',          'Salvat',           1976, 2, 1),
    ('978-9500512473', 'Historia de la conquista del Perú','William Prescott',         'Losada',           1847, 3, 1),
    ('978-8420674902', 'Sapiens: Historia de la humanidad','Yuval Noah Harari',        'Debate',           2014, 3, 1),
    ('978-9972450419', 'Historia del Perú republicano',    'Jorge Basadre',            'Universitaria',    1983, 3, 1),
    ('978-0132350884', 'Clean Code',                       'Robert C. Martin',         'Prentice Hall',    2008, 4, 1),
    ('978-0201633610', 'Design Patterns',                  'Gang of Four',             'Addison-Wesley',   1994, 4, 1),
    ('978-0596517748', 'JavaScript: The Good Parts',       'Douglas Crockford',        'O\'Reilly',        2008, 4, 1),
    ('978-9972200106', 'Código Civil Peruano comentado',   'Walter Gutierrez',         'Gaceta Jurídica',  2007, 5, 1),
    ('978-9972209079', 'Derecho Constitucional',           'Marcial Rubio Correa',     'PUCP',             2012, 5, 1),
    ('978-8420686172', 'Historia del Arte',                'Ernst Gombrich',           'Phaidon',          1950, 6, 1),
    ('978-8408135111', 'El arte de la guerra',             'Sun Tzu',                  'Alianza',           500, 6, 1),
    ('978-9585481404', 'El Principito',                    'Antoine de Saint-Exupéry', 'Emecé',            1943, 7, 1),
    ('978-8467521405', 'Harry Potter y la piedra filosofal','J.K. Rowling',            'Salamandra',       1997, 7, 1),
    ('978-9681650681', 'Diccionario de la Real Academia',  'RAE',                      'Espasa',           2014, 8, 1),
    ('978-8467015065', 'Atlas geográfico del Perú',        'Instituto Geográfico',     'Bruño',            2010, 8, 1);

-- ============================================================
-- 6. INVENTARIO (cada libro en al menos 1 sucursal)
-- ============================================================
INSERT INTO inventario (isbn, id_sucursal, cantidad_disponible, cantidad_total) VALUES
-- Sucursal 1 (Central Ilo) — colección completa
    ('978-9500302371', 1, 3, 3),
    ('978-8499893501', 1, 3, 3),
    ('978-9874373700', 1, 3, 3),
    ('978-9500512473', 1, 3, 2),
    ('978-8484326441', 1, 3, 2),
    ('978-8408117117', 1, 3, 2),
    ('978-9972450419', 1, 3, 3),
    ('978-0132350884', 1, 3, 3),
    ('978-0201633610', 1, 2, 2),
    ('978-0596517748', 1, 2, 2),
    ('978-9972200106', 1, 2, 2),
    ('978-9972209079', 1, 2, 2),
    ('978-8420686172', 1, 3, 3),
    ('978-9585481404', 1, 4, 4),
    ('978-8467521405', 1, 4, 4),
    ('978-9681650681', 1, 2, 2),
    ('978-8467015065', 1, 2, 2),
-- Sucursal 2 (El Algarrobal)
    ('978-9500302371', 2, 2, 2),
    ('978-9874373700', 2, 2, 2),
    ('978-9500512473', 2, 1, 1),
    ('978-0132350884', 2, 2, 2),
    ('978-9585481404', 2, 2, 2),
    ('978-8467521405', 2, 2, 2),
    ('978-8420674902', 2, 1, 1),
    ('978-8408135111', 2, 2, 2),
-- Sucursal 3 (Moquegua Centro)
    ('978-9972450419', 3, 2, 2),
    ('978-9972200106', 3, 1, 1),
    ('978-8420686172', 3, 2, 2),
    ('978-9681650681', 3, 1, 1),
    ('978-8467015065', 3, 1, 1),
    ('978-8499893501', 3, 1, 1),
    ('978-8484326441', 3, 1, 1),

-- ============================================================
-- 7. PRÉSTAMOS
-- Hoy asumimos: 2026-06-20
-- Membresía Básica  = 10 días → vence en fecha_prestamo + 10
-- Membresía Estándar= 15 días → vence en fecha_prestamo + 15
-- Membresía Premium = 30 días → vence en fecha_prestamo + 30
-- ============================================================
INSERT INTO prestamos (id_usuario, isbn, fecha_prestamo, fecha_devolucion, id_estado, id_empleado, id_sucursal) VALUES
-- DEVUELTOS (id_estado=2)
    (1,  '978-9500302371', '2026-05-01', '2026-05-14', 2, 1, 1),   -- Ivan, devuelto
    (2,  '978-8499893501', '2026-05-03', '2026-05-25', 2, 2, 2),   -- Laura, devuelto
    (3,  '978-9874373700', '2026-05-10', '2026-05-18', 2, 1, 1),   -- Carlos, devuelto
    (4,  '978-9500512473', '2026-05-15', '2026-05-28', 2, 3, 3),   -- María, devuelto
    (6,  '978-0132350884', '2026-05-20', '2026-06-10', 2, 1, 1),   -- Ana, devuelto
    (9,  '978-8420686172', '2026-04-10', '2026-05-05', 2, 4, 4),   -- Luis, devuelto
    (13, '978-9972200106', '2026-04-20', '2026-05-18', 2, 1, 1),   -- Roberto, devuelto
-- VENCIDOS (id_estado=3): fecha_prestamo hace >15 días, sin devolucion
-- Usuario 3 (Carlos, Básica=10 días): prestado hace 25 días → venció hace 15 días
    (3,  '978-8484326441', '2026-05-26', NULL,          3, 1, 1),
-- Usuario 5 (Jorge, Básica=10 días): prestado hace 20 días → venció hace 10 días
    (5,  '978-9972450419', '2026-05-31', NULL,          3, 2, 2),
-- Usuario 8 (Rosa, Básica=10 días): prestado hace 18 días → venció hace 8 días
    (8,  '978-9972209079', '2026-06-02', NULL,          3, 3, 3),
-- Usuario 11 (Diego, Básica=10 días): prestado hace 16 días → venció hace 6 días
    (11, '978-8408117117', '2026-06-04', NULL,          3, 4, 4),
-- Usuario 14 (Patricia, Básica=10 días): prestado hace 15 días → venció hace 5 días
    (14, '978-8408135111', '2026-06-05', NULL,          3, 1, 1),
-- Usuario 7 (Pedro, Estándar=15 días): prestado hace 20 días → venció hace 5 días
    (7,  '978-9681650681', '2026-05-31', NULL,          3, 2, 2),
-- ACTIVOS (id_estado=1): fecha_prestamo reciente (últimos 5 días)
    (1,  '978-0201633610', '2026-06-17', NULL,          1, 1, 1),   -- Ivan, activo
    (2,  '978-0596517748', '2026-06-18', NULL,          1, 1, 1),   -- Laura, activo
    (4,  '978-9874373700', '2026-06-19', NULL,          1, 3, 3),   -- María, activo
    (6,  '978-8467521405', '2026-06-16', NULL,          1, 2, 2),   -- Ana, activo
    (10, '978-9585481404', '2026-06-18', NULL,          1, 1, 1),   -- Carmen, activo
    (12, '978-8499893501', '2026-06-19', NULL,          1, 3, 3),   -- Sofía, activo
    (15, '978-8420674902', '2026-06-17', NULL,          1, 4, 4);   -- Miguel, activo

-- ============================================================
-- 8. MULTAS (solo para préstamos VENCIDOS)
-- id_prestamo de los vencidos: 8, 9, 10, 11, 12, 13
-- monto = dias_atraso × S/ 1.50
-- ============================================================
INSERT INTO multas (id_prestamo, monto, fecha_multa, estado_pago) VALUES
-- Préstamo 8: Carlos, venció hace 15 días → 15 × 1.50 = S/ 22.50
    (8,  22.50, '2026-06-20', 'PENDIENTE'),
-- Préstamo 9: Jorge, venció hace 10 días → 10 × 1.50 = S/ 15.00
    (9,  15.00, '2026-06-20', 'PENDIENTE'),
-- Préstamo 10: Rosa, venció hace 8 días → 8 × 1.50 = S/ 12.00
    (10, 12.00, '2026-06-20', 'PENDIENTE'),
-- Préstamo 11: Diego, venció hace 6 días → 6 × 1.50 = S/ 9.00
    (11,  9.00, '2026-06-20', 'PENDIENTE'),
-- Préstamo 12: Patricia, venció hace 5 días → 5 × 1.50 = S/ 7.50
    (12,  7.50, '2026-06-20', 'PENDIENTE'),
-- Préstamo 13: Pedro, venció hace 5 días → 5 × 1.50 = S/ 7.50
    (13,  7.50, '2026-06-20', 'PENDIENTE');

-- ============================================================
-- 9. RESERVAS (mínimo 5)
-- ============================================================
INSERT INTO reservas (id_usuario, isbn, fecha_reserva, fecha_expiracion, id_estado_reserva, id_empleado, id_sucursal) VALUES
    (3,  '978-9500302371', '2026-06-18', '2026-06-21', 1, 1, 1),   -- Pendiente
    (5,  '978-0132350884', '2026-06-19', '2026-06-22', 1, 2, 2),   -- Pendiente
    (9,  '978-9972450419', '2026-06-17', '2026-06-20', 2, 1, 1),   -- Confirmada
    (11, '978-8467521405', '2026-06-10', '2026-06-13', 4, 3, 3),   -- Expirada
    (14, '978-9874373700', '2026-06-15', '2026-06-18', 3, 1, 1),   -- Cancelada
    (2,  '978-9972200106', '2026-06-19', '2026-06-22', 1, 4, 4),   -- Pendiente
    (6,  '978-0201633610', '2026-06-18', '2026-06-21', 2, 2, 2),   -- Confirmada
    (10, '978-8420686172', '2026-06-20', '2026-06-23', 1, 1, 1);   -- Pendiente

DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "9";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "10";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "11";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "12";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "13";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "14";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "15";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "16";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "17";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "18";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "19";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "20";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "21";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "22";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "23";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "24";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "25";
DELETE FROM sucursales WHERE `sucursales`.`id_sucursal` = "26";

-- ============================================================
-- VERIFICACIÓN: conteo de registros insertados
-- ============================================================
SELECT 'sucursales'  AS tabla, COUNT(*) AS total FROM sucursales
UNION ALL SELECT 'personas',   COUNT(*) FROM personas
UNION ALL SELECT 'usuarios',   COUNT(*) FROM usuarios
UNION ALL SELECT 'empleados',  COUNT(*) FROM empleados
UNION ALL SELECT 'libros',     COUNT(*) FROM libros
UNION ALL SELECT 'inventario', COUNT(*) FROM inventario
UNION ALL SELECT 'prestamos',  COUNT(*) FROM prestamos
UNION ALL SELECT 'multas',     COUNT(*) FROM multas
UNION ALL SELECT 'reservas',   COUNT(*) FROM reservas;
