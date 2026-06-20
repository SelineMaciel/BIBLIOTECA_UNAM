"""
servicios/servicio_prestamos.py
------------------------------------
Reglas de negocio relacionadas a préstamos:
  - Verificar que el usuario no exceda su límite de préstamos (según
    su Membresia).
  - Verificar que el libro tenga stock disponible en la sucursal.
  - Calcular la fecha límite de devolución según los días de la
    membresía.
  - Registrar la devolución y actualizar el inventario.

No conoce Flask ni HTML: solo orquesta repositorios y modelos.
"""

from datetime import date, timedelta

from persistencia.repositorio_prestamos import RepositorioPrestamos, RepositorioEstadosPrestamo
from persistencia.repositorio_inventario import RepositorioInventario
from persistencia.repositorio_personas import RepositorioUsuarios


class PrestamoNoPermitidoError(Exception):
    pass


class ServicioPrestamos:
    def __init__(self):
        self._repo_prestamos = RepositorioPrestamos()
        self._repo_estados = RepositorioEstadosPrestamo()
        self._repo_inventario = RepositorioInventario()
        self._repo_usuarios = RepositorioUsuarios()

    def fecha_limite_devolucion(self, usuario, fecha_prestamo: date = None) -> date:
        fecha_prestamo = fecha_prestamo or date.today()
        return fecha_prestamo + timedelta(days=usuario.membresia.dias_prestamo)

    def crear_prestamo(self, id_usuario: int, isbn: str, id_sucursal: int, id_empleado: int = None):
        """
        Valida las reglas de negocio y, si todo es correcto, crea el
        préstamo y descuenta una unidad del inventario.
        Lanza PrestamoNoPermitidoError si alguna regla falla.
        """
        usuario = self._repo_usuarios.obtener_por_id_completo(id_usuario)
        if usuario is None:
            raise PrestamoNoPermitidoError("El usuario no existe")

        if not usuario.puede_solicitar_prestamo():
            raise PrestamoNoPermitidoError(
                f"El usuario alcanzó el máximo de préstamos activos permitido por su "
                f"membresía '{usuario.membresia.tipo_membresia}' "
                f"({usuario.membresia.max_prestamos})"
            )

        # Recargar historial real desde BD para no confiar solo en el objeto recién construido
        activos = self._repo_prestamos.obtener_activos_por_usuario(id_usuario)
        if len(activos) >= usuario.membresia.max_prestamos:
            raise PrestamoNoPermitidoError("Límite de préstamos activos alcanzado")

        item_inventario = self._repo_inventario.obtener_por_libro_y_sucursal(isbn, id_sucursal)
        if item_inventario is None or item_inventario.cantidad_disponible <= 0:
            raise PrestamoNoPermitidoError("No hay unidades disponibles de este libro en la sucursal")

        estado_activo = self._repo_estados.obtener_por_descripcion("Activo")

        cursor_valores = {
            "id_usuario": id_usuario,
            "isbn": isbn,
            "fecha_prestamo": date.today(),
            "fecha_devolucion": None,
            "id_estado": estado_activo.id_estado_prestamo,
            "id_empleado": id_empleado,
            "id_sucursal": id_sucursal,
        }
        id_prestamo = self._insertar_prestamo_directo(cursor_valores)

        # Actualiza inventario (descuenta una unidad disponible)
        self._repo_inventario.ajustar_disponibilidad(item_inventario.id_inventario, -1)

        return id_prestamo

    def _insertar_prestamo_directo(self, valores: dict) -> int:
        """Inserción directa porque RepositorioBase.crear() espera un
        objeto Prestamo completo (con Usuario/Libro ya ensamblados),
        pero aquí construimos el préstamo a partir de IDs crudos para
        evitar cargas innecesarias de objetos completos solo para insertar."""
        columnas = ", ".join(valores.keys())
        marcadores = ", ".join(["%s"] * len(valores))
        sql = f"INSERT INTO prestamos ({columnas}) VALUES ({marcadores})"
        cursor = self._repo_prestamos._db.obtener_cursor()
        cursor.execute(sql, list(valores.values()))
        nuevo_id = cursor.lastrowid
        self._repo_prestamos._db.confirmar()
        cursor.close()
        return nuevo_id

    def registrar_devolucion(self, id_prestamo: int):
        prestamo = self._repo_prestamos.obtener_por_id(id_prestamo)
        if prestamo is None:
            raise PrestamoNoPermitidoError("El préstamo no existe")
        if prestamo.fue_devuelto():
            raise PrestamoNoPermitidoError("Este préstamo ya fue devuelto")

        estado_devuelto = self._repo_estados.obtener_por_descripcion("Devuelto")
        self._repo_prestamos.registrar_devolucion(
            id_prestamo, date.today(), estado_devuelto.id_estado_prestamo
        )

        # Devuelve la unidad al inventario de la sucursal correspondiente
        if prestamo.sucursal is not None:
            item_inventario = self._repo_inventario.obtener_por_libro_y_sucursal(
                prestamo.libro.isbn, prestamo.sucursal.id_sucursal
            )
            if item_inventario is not None:
                self._repo_inventario.ajustar_disponibilidad(item_inventario.id_inventario, 1)

        return prestamo

    def obtener_vencidos_hoy(self) -> list:
        """
        Préstamos activos cuya fecha límite (fecha_prestamo + dias de
        su membresía) ya pasó respecto a hoy. Se usa tanto para marcar
        estado 'Vencido' como para el servicio de notificaciones (Fase 6).
        """
        candidatos = self._repo_prestamos.obtener_activos_por_usuario  # solo referencia, no llamada
        # Como dias_prestamo depende de la membresía de cada usuario,
        # no se puede filtrar con una sola fecha fija en SQL: se filtra en Python.
        todos_activos_sql = """
            SELECT p.* FROM prestamos p
            INNER JOIN estados_prestamo e ON e.id_estado_prestamo = p.id_estado
            WHERE e.descripcion = 'Activo'
        """
        filas = self._repo_prestamos.ejecutar_consulta_personalizada(todos_activos_sql)
        prestamos_activos = [self._repo_prestamos._fila_a_objeto(fila) for fila in filas]

        vencidos = []
        for prestamo in prestamos_activos:
            limite = self.fecha_limite_devolucion(prestamo.usuario, prestamo.fecha_prestamo)
            if date.today() > limite:
                vencidos.append(prestamo)
        return vencidos

    def proximos_a_vencer(self, dias_aviso: int = 2) -> list:
        """
        Préstamos activos cuya fecha límite cae dentro de los próximos
        `dias_aviso` días (para el recordatorio por correo de Fase 6).
        """
        sql = """
            SELECT p.* FROM prestamos p
            INNER JOIN estados_prestamo e ON e.id_estado_prestamo = p.id_estado
            WHERE e.descripcion = 'Activo'
        """
        filas = self._repo_prestamos.ejecutar_consulta_personalizada(sql)
        activos = [self._repo_prestamos._fila_a_objeto(fila) for fila in filas]

        proximos = []
        hoy = date.today()
        for prestamo in activos:
            limite = self.fecha_limite_devolucion(prestamo.usuario, prestamo.fecha_prestamo)
            dias_restantes = (limite - hoy).days
            if 0 <= dias_restantes <= dias_aviso:
                proximos.append(prestamo)
        return proximos
