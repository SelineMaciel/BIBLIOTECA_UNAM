# Biblioteca - Proyecto POO + Flask (en construcción)

# Biblioteca - Proyecto POO + Flask (en construcción)

Estado actual: **Fase 2, 3 y 4 completas** (Persistencia + Modelos, Servicios,
y ahora Controladores + Vistas Flask + Formularios + main.py).
Faltan: Fase 5 (Ciencia de Datos), Fase 6 (Integración API REST de email),
Fase 7 (Pulido final).

## Cómo probar la aplicación web completa en tu XAMPP

### 1. Requisitos previos
- XAMPP corriendo, con MySQL activo (puerto 3306, usuario `root`, sin password).
- Python 3.10+ instalado en tu máquina (NO el de XAMPP, sino uno aparte).
- La base de datos `biblioteca1` ya importada (si ya la probaste en la fase
  anterior, no necesitas volver a importarla).

### 2. Instalar dependencias (incluye Flask y Flask-WTF, nuevas en esta fase)
```bash
pip install -r requirements.txt
```

### 3. Crear tu primer AdminUser (si no lo hiciste en la fase anterior)
```python
from servicios.servicio_auth import ServicioAuth

auth = ServicioAuth()
id_admin = auth.registrar_admin(
    nombre="Admin Principal",
    email="admin@biblioteca.com",
    phone="999000000",
    admin_user="admin",
    password_plano="admin123",
    id_rol=1,
)
print("AdminUser creado con id:", id_admin)
```

### 4. Levantar el servidor Flask
```bash
python main.py
```
Verás algo como `Running on http://127.0.0.1:5000`. Abre esa URL en tu navegador.

### 5. Probar el flujo completo
1. En `/login`, ingresa el email del admin (`admin@biblioteca.com`) y su
   password (`admin123`). Deberías llegar al Panel de Administrador.
2. Desde el panel, prueba el CRUD de **Libros**: crear uno nuevo, buscarlo
   por título, filtrar por categoría, editarlo y eliminarlo.
3. Crea un **Usuario** (lector) de prueba desde el menú Usuarios.
4. Crea un **Empleado** de prueba desde el menú Empleados.
5. Cierra sesión y vuelve a entrar usando el email del Usuario o Empleado
   que creaste (sin password) para ver su panel correspondiente.
6. Desde la sesión de admin o empleado, registra un **Préstamo** para el
   usuario de prueba (necesitas que el libro tenga stock en `inventario`;
   si no insertaste inventario todavía, hazlo manualmente en phpMyAdmin
   para esta prueba, o dime y te ayudo con un script de carga).
7. Revisa el dashboard de **Reportes** (todavía con tablas simples; se
   ampliará con gráficos en la Fase 5).

## Qué se agregó en esta fase (Fase 4)

```
biblioteca_app/
├── main.py                    # Punto de entrada: crea la app y registra blueprints
├── utilitarios/
│   ├── decoradores.py          # @login_requerido, @requiere_tipo, @requiere_permiso
│   ├── sesion.py                # Reconstruye el objeto Persona desde la sesión Flask
│   └── validadores.py           # Validaciones reutilizables (email, ISBN, año, teléfono)
├── formularios/                 # Flask-WTF: validaciones declarativas + CSRF
│   ├── login_form.py
│   ├── usuario_form.py
│   ├── empleado_form.py
│   ├── admin_form.py
│   ├── libro_form.py
│   ├── prestamo_form.py         # incluye también ReservaForm
│   └── busqueda_form.py
├── controladores/                # Orquestan repositorios/servicios para las vistas
│   ├── auth_controller.py
│   ├── usuarios_controller.py
│   ├── empleados_controller.py
│   ├── admins_controller.py
│   ├── libros_controller.py
│   ├── inventario_controller.py
│   ├── prestamos_controller.py
│   ├── reservas_controller.py
│   └── reportes_controller.py
└── vistas/                       # Blueprints Flask + templates Bootstrap 5
    ├── auth_views.py, admin_views.py, empleado_views.py, usuario_views.py
    ├── usuarios_views.py, empleados_views.py, admins_views.py
    ├── libros_views.py, inventario_views.py, prestamos_views.py, reservas_views.py, reportes_views.py
    └── templates/                # base.html + carpetas por módulo
```

### Seguridad y permisos implementados
- Login unificado por email (AdminUser con password real vía `werkzeug.security`;
  Empleado y Usuario sin password, según lo decidido).
- `@login_requerido`: exige sesión activa.
- `@requiere_tipo(...)`: exige que la sesión sea de cierto tipo (admin/empleado/usuario).
- `@requiere_permiso(...)`: exige sesión + el permiso específico, verificado a
  través de `ServicioPermisos`, que a su vez usa el **polimorfismo** de
  `Persona.tiene_acceso()` (cada subclase responde distinto, tal como se
  diseñó en la Fase 3).

### CRUD completo implementado
Usuarios, Empleados, Administradores y Libros tienen creación, lectura,
actualización y eliminación vía formularios web con validaciones (Flask-WTF)
y protección CSRF. Libros además tiene búsqueda por título y filtro por
categoría/disponibilidad. Préstamos y Reservas tienen creación y las
transiciones de estado propias de su flujo de negocio (devolver, confirmar,
cancelar), reutilizando las reglas ya construidas en los servicios de la Fase 3.

## Verificación hecha en este entorno (sin BD real)
Se usaron paquetes "stub" temporales de Flask-WTF/WTForms/mysql-connector
(NO incluidos en este paquete) únicamente para validar, con el test client
de Flask, que:
- La app se construye y registra correctamente las ~28 rutas esperadas.
- Las páginas públicas (inicio, login) responden 200.
- Las rutas protegidas redirigen a `/login` (302) sin sesión activa.
- `@requiere_tipo` devuelve 403 si el tipo de sesión no coincide.
- `@requiere_permiso` efectivamente intenta consultar la base de datos real
  para verificar el permiso (se confirmó que llega a intentar la conexión;
  fallará aquí por no haber MySQL en este sandbox, pero funcionará en tu XAMPP).

Lo que falta probar en tu entorno real: el CRUD completo contra datos reales,
y sobre todo el flujo de préstamo (que depende del inventario por sucursal).
Si algo falla, copia el error completo y lo revisamos antes de pasar a Fase 5.

## ⚠️ Dato faltante en el script SQL original: SUCURSALES

El script `biblioteca_db.sql` que diste como punto de partida define la
tabla `sucursales` pero **no inserta ninguna fila inicial** (a diferencia de
roles, permisos, membresías, categorías y estados, que sí tienen datos base).
Sin al menos una sucursal, el desplegable de Sucursal aparece vacío al crear
un Empleado, y tampoco se puede registrar un Préstamo (que también depende
de `id_sucursal`).

**Antes de seguir probando**, ejecuta el archivo `sql_datos_sucursales.sql`
incluido en este paquete desde phpMyAdmin (pestaña SQL, sobre la base
`biblioteca1`). Inserta 3 sucursales de ejemplo y, opcionalmente, un libro
con inventario de prueba para que puedas probar el flujo de préstamo sin
pasos manuales adicionales. Si ya creaste tus propios libros desde el panel,
puedes omitir esa segunda parte o ajustarla a tu propio ISBN.

## Nueva funcionalidad: gestión de Inventario desde la web

Se detectó que crear un Libro (CRUD de Libros) y registrar su stock en una
Sucursal (tabla `inventario`) son dos pasos distintos, y el proyecto no tenía
ninguna pantalla para el segundo paso, obligando a usar phpMyAdmin cada vez
que se necesitaba dar de alta stock. Se agregó un módulo completo:

- `formularios/inventario_form.py`
- `controladores/inventario_controller.py`
- `vistas/inventario_views.py` + `vistas/templates/inventario/`

Accesible desde el menú "Inventario" (visible para admin y empleado, mismo
permiso que Libros: `gestionar_libros`). Permite crear, editar y eliminar
relaciones libro-sucursal con su cantidad disponible y total. Respeta la
restricción de la base de datos de que no puede haber dos registros de
inventario para el mismo libro en la misma sucursal (debes editar el
existente en ese caso, no crear uno nuevo).

### Script puntual para tu caso de prueba actual
Si ya tienes creado el libro "Don Quijote de la Mancha" (ISBN `123456789`)
y la sucursal "Biblioteca Ilo" pero te falta el inventario para poder
prestarlo, ejecuta `sql_inventario_prueba.sql` en phpMyAdmin. Revisa primero
el `SELECT` incluido en el script para confirmar el `id_sucursal` real de
tu "Biblioteca Ilo" antes del `INSERT` (puede no ser 1 si la creaste
manualmente). Alternativamente, ahora puedes hacerlo directamente desde la
nueva pantalla de Inventario en la web, sin necesidad de phpMyAdmin.

## Corrección aplicada (reportada tras pruebas en XAMPP)

Se detectó y corrigió un bug real: `RepositorioAdminUsers` no tenía un método
`obtener_por_id_completo()` (con JOIN contra `personas`) como sí lo tenían
`RepositorioUsuarios` y `RepositorioEmpleados`. Como consecuencia, tres puntos
del código usaban por error el método genérico `obtener_por_id()` (heredado
de `RepositorioBase`, sin JOIN) para reconstruir un `AdminUser`, lo cual
provocaba `KeyError: 'nombre'` porque esa columna vive en `personas`, no en
`admin_users`. Esto rompía: reconstruir la sesión del admin (afectando TODA
ruta protegida con `@requiere_permiso`, de ahí que fallara en Usuarios,
Empleados, Nuevo Libro y Reportes), el listado de administradores, y la
eliminación de administradores.

Se corrigió agregando `obtener_por_id_completo()` y `obtener_todos_completo()`
a `RepositorioAdminUsers` (siguiendo el mismo patrón que ya existía en los
otros dos repositorios), y actualizando los 4 puntos que debían usarlos:
`utilitarios/sesion.py`, `controladores/admins_controller.py` (listar y
eliminar), y `persistencia/repositorio_reservas.py` (en `RepositorioReservas`
y `RepositorioReportes`, que ensamblan un AdminUser asociado).

También se agregó `email-validator` a `requirements.txt`, necesario para que
el validador `Email()` de WTForms funcione.

## Próximas fases
- **Fase 5**: ampliar `servicio_reportes.py` con pandas/numpy/matplotlib/seaborn
  (gráficos de barras, circulares, series temporales, dashboard estadístico)
  y agregar carga masiva de libros desde Excel/CSV.
- **Fase 6**: completar `EnviadorNotificaciones.enviar()` con la llamada real
  a la API REST de SendGrid o Mailgun para los recordatorios de devolución.
- **Fase 7**: pulido, pruebas, documentación final.

