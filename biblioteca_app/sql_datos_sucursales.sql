-- ============================================================
--  Datos iniciales faltantes: SUCURSALES
--  El script original (biblioteca_db.sql) define la tabla pero
--  no inserta ninguna fila. Sin al menos una sucursal no se puede
--  crear un Empleado ni registrar un Préstamo (ambos dependen de
--  id_sucursal). Ejecutar este script en phpMyAdmin sobre la base
--  `biblioteca1` para poder continuar con las pruebas.
-- ============================================================

USE biblioteca1;

INSERT INTO sucursales (nombre, calle, ciudad, telefono) VALUES
    ('Sede Central', 'Av. Principal 123', 'Ilo', '053-481000'),
    ('Sede Norte', 'Jr. Los Pinos 456', 'Ilo', '053-481111'),
    ('Sede Moquegua', 'Calle Tacna 789', 'Moquegua', '053-462200');

-- ============================================================
-- OPCIONAL: un libro y su inventario de ejemplo, para poder
-- probar el flujo de Préstamo de extremo a extremo sin tener
-- que crear estos datos manualmente desde la interfaz web.
-- Si ya creaste tus propios libros desde el panel de Admin,
-- puedes omitir este bloque o adaptarlo a tu propio ISBN.
-- ============================================================

INSERT INTO libros (ISBN, titulo, autor, editorial, anio_publicacion, id_categoria, id_estado) VALUES
    ('978-0132350884', 'Clean Code', 'Robert C. Martin', 'Prentice Hall', 2008, 4, 1);

INSERT INTO inventario (isbn, id_sucursal, cantidad_disponible, cantidad_total) VALUES
    ('978-0132350884', 1, 3, 3);
