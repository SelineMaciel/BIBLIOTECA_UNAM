-- ============================================================
--  BIBLIOTECA - Script de Base de Datos Normalizado (MySQL)
--  Aplicando 1FN, 2FN y 3FN
--  Versión final completa con todas las relaciones del diagrama
-- ============================================================

CREATE DATABASE IF NOT EXISTS biblioteca1
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE biblioteca1;

-- ============================================================
-- 1. ROLES
--    Unificado para usuarios, empleados y admins
--    3FN: nombre_rol no depende de ninguna otra entidad
-- ============================================================
CREATE TABLE roles (
    id_rol       INT          NOT NULL AUTO_INCREMENT,
    nombre_rol   VARCHAR(50)  NOT NULL,
    descripcion  VARCHAR(255),
    PRIMARY KEY (id_rol)
);

-- ============================================================
-- 2. PERMISOS
--    Un rol puede tener muchos permisos → tabla intermedia
--    Muchos a muchos: roles ↔ permisos
-- ============================================================
CREATE TABLE permisos (
    id_permiso     INT          NOT NULL AUTO_INCREMENT,
    nombre_permiso VARCHAR(100) NOT NULL,
    descripcion    VARCHAR(255),
    PRIMARY KEY (id_permiso)
);

CREATE TABLE roles_permisos (
    id_rol      INT NOT NULL,
    id_permiso  INT NOT NULL,
    PRIMARY KEY (id_rol, id_permiso),
    CONSTRAINT fk_rp_rol     FOREIGN KEY (id_rol)     REFERENCES roles(id_rol),
    CONSTRAINT fk_rp_permiso FOREIGN KEY (id_permiso) REFERENCES permisos(id_permiso)
);

-- ============================================================
-- 3. SUCURSALES
--    1FN: dirección separada en campos atómicos
-- ============================================================
CREATE TABLE sucursales (
    id_sucursal  INT          NOT NULL AUTO_INCREMENT,
    nombre       VARCHAR(100) NOT NULL,
    calle        VARCHAR(150) NOT NULL,
    ciudad       VARCHAR(100) NOT NULL,
    telefono     VARCHAR(20),
    PRIMARY KEY (id_sucursal)
);

-- ============================================================
-- 4. PERSONAS (tabla base de herencia)
--    3FN: datos comunes no se repiten en Usuario/Empleado/Admin
-- ============================================================
CREATE TABLE personas (
    id_persona  INT          NOT NULL AUTO_INCREMENT,
    nombre      VARCHAR(100) NOT NULL,
    email       VARCHAR(150) NOT NULL UNIQUE,
    phone       VARCHAR(20),
    PRIMARY KEY (id_persona)
);

-- ============================================================
-- 5. MEMBRESÍAS
--    3FN: max_prestamos y dias_prestamo dependen del tipo,
--    no del usuario
-- ============================================================
CREATE TABLE membresias (
    id_membresia    INT         NOT NULL AUTO_INCREMENT,
    tipo_membresia  VARCHAR(50) NOT NULL,
    max_prestamos   INT         NOT NULL DEFAULT 3,
    dias_prestamo   INT         NOT NULL DEFAULT 15,
    PRIMARY KEY (id_membresia)
);

-- ============================================================
-- 6. USUARIOS
--    2FN: id_membresia es FK, no datos embebidos
-- ============================================================
CREATE TABLE usuarios (
    id_usuario    INT NOT NULL AUTO_INCREMENT,
    id_persona    INT NOT NULL,
    edad          INT,
    id_membresia  INT NOT NULL,
    id_rol        INT NOT NULL,
    PRIMARY KEY (id_usuario),
    CONSTRAINT fk_usu_persona    FOREIGN KEY (id_persona)   REFERENCES personas(id_persona),
    CONSTRAINT fk_usu_membresia  FOREIGN KEY (id_membresia) REFERENCES membresias(id_membresia),
    CONSTRAINT fk_usu_rol        FOREIGN KEY (id_rol)       REFERENCES roles(id_rol)
);

-- ============================================================
-- 7. EMPLEADOS
--    3FN: cargo no determina sucursal ni viceversa
-- ============================================================
CREATE TABLE empleados (
    id_empleado  INT          NOT NULL AUTO_INCREMENT,
    id_persona   INT          NOT NULL,
    cargo        VARCHAR(100) NOT NULL,
    id_sucursal  INT          NOT NULL,
    PRIMARY KEY (id_empleado),
    CONSTRAINT fk_emp_persona   FOREIGN KEY (id_persona)  REFERENCES personas(id_persona),
    CONSTRAINT fk_emp_sucursal  FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

-- ============================================================
-- 8. ADMIN USERS
--    2FN: id_rol FK limpia, sin datos embebidos
-- ============================================================
CREATE TABLE admin_users (
    id_admin      INT          NOT NULL AUTO_INCREMENT,
    id_persona    INT          NOT NULL,
    admin_user    VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    id_rol        INT          NOT NULL,
    PRIMARY KEY (id_admin),
    CONSTRAINT fk_adm_persona  FOREIGN KEY (id_persona) REFERENCES personas(id_persona),
    CONSTRAINT fk_adm_rol      FOREIGN KEY (id_rol)     REFERENCES roles(id_rol)
);

-- ============================================================
-- 9. CATEGORÍAS DE LIBROS
-- ============================================================
CREATE TABLE categorias (
    id_categoria      INT          NOT NULL AUTO_INCREMENT,
    nombre_categoria  VARCHAR(100) NOT NULL,
    descripcion       VARCHAR(255),
    PRIMARY KEY (id_categoria)
);

-- ============================================================
-- 10. ESTADOS DEL LIBRO
--     1FN: estado como entidad, no string embebido
-- ============================================================
CREATE TABLE estados_libro (
    id_estado      INT         NOT NULL AUTO_INCREMENT,
    nombre_estado  VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_estado)
);

-- ============================================================
-- 11. LIBROS
--     1FN: un autor principal por fila
--     3FN: editorial no determina categoría
-- ============================================================
CREATE TABLE libros (
    ISBN              VARCHAR(20)  NOT NULL,
    titulo            VARCHAR(200) NOT NULL,
    autor             VARCHAR(150) NOT NULL,
    editorial         VARCHAR(150),
    anio_publicacion  INT,
    id_categoria      INT          NOT NULL,
    id_estado         INT          NOT NULL,
    PRIMARY KEY (ISBN),
    CONSTRAINT fk_lib_categoria  FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria),
    CONSTRAINT fk_lib_estado     FOREIGN KEY (id_estado)    REFERENCES estados_libro(id_estado)
);

-- ============================================================
-- 12. AUTORES
--     Muchos a muchos: libros ↔ autores (coautores)
--     1FN: evita lista de autores en un solo campo
-- ============================================================
CREATE TABLE autores (
    id_autor  INT          NOT NULL AUTO_INCREMENT,
    nombre    VARCHAR(150) NOT NULL,
    PRIMARY KEY (id_autor)
);

CREATE TABLE libros_autores (
    ISBN      VARCHAR(20) NOT NULL,
    id_autor  INT         NOT NULL,
    PRIMARY KEY (ISBN, id_autor),
    CONSTRAINT fk_la_libro  FOREIGN KEY (ISBN)     REFERENCES libros(ISBN),
    CONSTRAINT fk_la_autor  FOREIGN KEY (id_autor) REFERENCES autores(id_autor)
);

-- ============================================================
-- 13. INVENTARIO
--     2FN: cantidad depende de (isbn + sucursal), no solo del libro
-- ============================================================
CREATE TABLE inventario (
    id_inventario        INT         NOT NULL AUTO_INCREMENT,
    isbn                 VARCHAR(20) NOT NULL,
    id_sucursal          INT         NOT NULL,
    cantidad_disponible  INT         NOT NULL DEFAULT 0,
    cantidad_total       INT         NOT NULL DEFAULT 0,
    PRIMARY KEY (id_inventario),
    UNIQUE KEY uq_inv (isbn, id_sucursal),
    CONSTRAINT fk_inv_libro     FOREIGN KEY (isbn)        REFERENCES libros(ISBN),
    CONSTRAINT fk_inv_sucursal  FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

-- ============================================================
-- 14. ESTADOS DE PRÉSTAMO
-- ============================================================
CREATE TABLE estados_prestamo (
    id_estado_prestamo  INT         NOT NULL AUTO_INCREMENT,
    descripcion         VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_estado_prestamo)
);

-- ============================================================
-- 15. PRÉSTAMOS
--     Registra empleado que gestionó y sucursal donde ocurrió
--     3FN: fecha_devolucion depende del préstamo, no del usuario
-- ============================================================
CREATE TABLE prestamos (
    id_prestamo       INT         NOT NULL AUTO_INCREMENT,
    id_usuario        INT         NOT NULL,
    isbn              VARCHAR(20) NOT NULL,
    fecha_prestamo    DATE        NOT NULL,
    fecha_devolucion  DATE,
    id_estado         INT         NOT NULL,
    id_empleado       INT,
    id_sucursal       INT,
    PRIMARY KEY (id_prestamo),
    CONSTRAINT fk_pre_usuario   FOREIGN KEY (id_usuario)  REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_pre_libro     FOREIGN KEY (isbn)        REFERENCES libros(ISBN),
    CONSTRAINT fk_pre_estado    FOREIGN KEY (id_estado)   REFERENCES estados_prestamo(id_estado_prestamo),
    CONSTRAINT fk_pre_empleado  FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    CONSTRAINT fk_pre_sucursal  FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal)
);

-- ============================================================
-- 16. MULTAS
--     2FN: monto depende del préstamo, no del usuario directamente
--     Muchos a muchos implícito: un préstamo puede generar
--     varias multas (recargos por días)
-- ============================================================
CREATE TABLE multas (
    id_multa     INT                        NOT NULL AUTO_INCREMENT,
    id_prestamo  INT                        NOT NULL,
    monto        DECIMAL(8,2)               NOT NULL,
    fecha_multa  DATE                       NOT NULL,
    estado_pago  ENUM('PENDIENTE','PAGADO') NOT NULL DEFAULT 'PENDIENTE',
    PRIMARY KEY (id_multa),
    CONSTRAINT fk_mul_prestamo  FOREIGN KEY (id_prestamo) REFERENCES prestamos(id_prestamo)
);

-- ============================================================
-- 17. ESTADOS DE RESERVA
-- ============================================================
CREATE TABLE estados_reserva (
    id_estado_reserva  INT         NOT NULL AUTO_INCREMENT,
    descripcion        VARCHAR(50) NOT NULL,
    PRIMARY KEY (id_estado_reserva)
);

-- ============================================================
-- 18. RESERVAS
--     Relaciones completas: usuario, libro, sucursal,
--     empleado que gestiona y admin que supervisa
--     3FN: fecha_expiracion depende de fecha_reserva + negocio
-- ============================================================
CREATE TABLE reservas (
    id_reserva         INT         NOT NULL AUTO_INCREMENT,
    id_usuario         INT         NOT NULL,
    isbn               VARCHAR(20) NOT NULL,
    fecha_reserva      DATE        NOT NULL,
    fecha_expiracion   DATE        NOT NULL,
    id_estado_reserva  INT         NOT NULL,
    id_empleado        INT,         -- empleado que gestiona la reserva
    id_sucursal        INT,         -- sucursal donde se recoge el libro
    id_admin           INT,         -- admin que supervisa (del diagrama: AdminUser gestiona Reserva)
    PRIMARY KEY (id_reserva),
    CONSTRAINT fk_res_usuario   FOREIGN KEY (id_usuario)        REFERENCES usuarios(id_usuario),
    CONSTRAINT fk_res_libro     FOREIGN KEY (isbn)              REFERENCES libros(ISBN),
    CONSTRAINT fk_res_estado    FOREIGN KEY (id_estado_reserva) REFERENCES estados_reserva(id_estado_reserva),
    CONSTRAINT fk_res_empleado  FOREIGN KEY (id_empleado)       REFERENCES empleados(id_empleado),
    CONSTRAINT fk_res_sucursal  FOREIGN KEY (id_sucursal)       REFERENCES sucursales(id_sucursal),
    CONSTRAINT fk_res_admin     FOREIGN KEY (id_admin)          REFERENCES admin_users(id_admin)
);

-- ============================================================
-- 19. REPORTES
--     El AdminUser genera reportes (del diagrama: generarReportes)
--     Tabla para trazabilidad de reportes generados
-- ============================================================
CREATE TABLE reportes (
    id_reporte      INT          NOT NULL AUTO_INCREMENT,
    id_admin        INT          NOT NULL,
    tipo_reporte    VARCHAR(100) NOT NULL,
    fecha_generado  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descripcion     TEXT,
    PRIMARY KEY (id_reporte),
    CONSTRAINT fk_rep_admin  FOREIGN KEY (id_admin) REFERENCES admin_users(id_admin)
);

-- ============================================================
-- DATOS INICIALES
-- ============================================================

INSERT INTO roles (nombre_rol, descripcion) VALUES
    ('Administrador', 'Acceso total al sistema'),
    ('Empleado',      'Gestión de préstamos y devoluciones'),
    ('Usuario',       'Consulta y préstamo de libros');

INSERT INTO permisos (nombre_permiso, descripcion) VALUES
    ('gestionar_usuarios',   'Crear, editar y eliminar usuarios'),
    ('gestionar_empleados',  'Crear, editar y eliminar empleados'),
    ('gestionar_libros',     'Agregar y modificar libros'),
    ('registrar_prestamo',   'Registrar nuevos préstamos'),
    ('registrar_devolucion', 'Procesar devoluciones'),
    ('generar_reportes',     'Generar reportes del sistema'),
    ('configurar_sistema',   'Modificar configuración general'),
    ('consultar_catalogo',   'Ver catálogo de libros disponibles'),
    ('hacer_reserva',        'Realizar reservas de libros'),
    ('consultar_multas',     'Ver multas propias');

-- Permisos por rol
INSERT INTO roles_permisos (id_rol, id_permiso) VALUES
    (1,1),(1,2),(1,3),(1,4),(1,5),(1,6),(1,7),(1,8),(1,9),(1,10),  -- Administrador: todos
    (2,4),(2,5),(2,8),(2,9),                                        -- Empleado
    (3,8),(3,9),(3,10);                                             -- Usuario

INSERT INTO estados_libro (nombre_estado) VALUES
    ('Disponible'),
    ('Prestado'),
    ('Reservado'),
    ('Deteriorado'),
    ('Dado de baja');

INSERT INTO estados_prestamo (descripcion) VALUES
    ('Activo'),
    ('Devuelto'),
    ('Vencido');

INSERT INTO estados_reserva (descripcion) VALUES
    ('Pendiente'),
    ('Confirmada'),
    ('Cancelada'),
    ('Expirada');

INSERT INTO membresias (tipo_membresia, max_prestamos, dias_prestamo) VALUES
    ('Básica',    2, 10),
    ('Estándar',  5, 15),
    ('Premium',  10, 30);

INSERT INTO categorias (nombre_categoria, descripcion) VALUES
    ('Novela',        'Ficción narrativa larga'),
    ('Ciencia',       'Libros de divulgación y texto científico'),
    ('Historia',      'Libros de historia universal y local'),
    ('Tecnología',    'Informática, programación e ingeniería'),
    ('Derecho',       'Legislación, jurisprudencia y derecho'),
    ('Arte',          'Pintura, escultura, música y diseño'),
    ('Infantil',      'Literatura para niños y jóvenes'),
    ('Referencia',    'Diccionarios, enciclopedias y atlas');

