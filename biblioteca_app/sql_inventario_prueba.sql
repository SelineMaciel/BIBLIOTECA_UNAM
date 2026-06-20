-- ============================================================
--  Carga de inventario para el caso de prueba reportado:
--  Libro "Don Quijote de la Mancha" (ISBN 123456789) en la
--  sucursal "Biblioteca Ilo".
--
--  IMPORTANTE: revisa primero con el SELECT de abajo cuál es el
--  id_sucursal real de "Biblioteca Ilo" en tu base de datos (puede
--  no ser 1 si la creaste manualmente desde la web). Ajusta el
--  valor de @id_sucursal según el resultado antes de ejecutar el
--  INSERT.
-- ============================================================

USE biblioteca1;

-- Paso 1: ubicar el id_sucursal real de "Biblioteca Ilo"
SELECT id_sucursal, nombre FROM sucursales WHERE nombre LIKE '%Ilo%';

-- Paso 2: ajusta este valor según el resultado del SELECT anterior
SET @id_sucursal = 1;  -- <-- CAMBIA ESTE NÚMERO SI ES NECESARIO

-- Paso 3: insertar el inventario (3 unidades disponibles de 3 totales)
INSERT INTO inventario (isbn, id_sucursal, cantidad_disponible, cantidad_total)
VALUES ('123456789', @id_sucursal, 3, 3);

-- Paso 4: verificar que se insertó correctamente
SELECT i.id_inventario, l.titulo, s.nombre AS sucursal, i.cantidad_disponible, i.cantidad_total
FROM inventario i
INNER JOIN libros l ON l.ISBN = i.isbn
INNER JOIN sucursales s ON s.id_sucursal = i.id_sucursal
WHERE i.isbn = '123456789';
