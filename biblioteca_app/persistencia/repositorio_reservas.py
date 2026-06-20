"""
persistencia/repositorio_reservas.py
----------------------------------------
Repositorios concretos para EstadoReserva, Reserva y Reporte.
"""

from datetime import date
from persistencia.repositorio_base import RepositorioBase
from persistencia.repositorio_personas import RepositorioUsuarios, RepositorioEmpleados, RepositorioAdminUsers
from persistencia.repositorio_libros import RepositorioLibros
from persistencia.repositorio_membresias import RepositorioSucursales
from modelos.reserva import EstadoReserva, Reserva, Reporte


class RepositorioEstadosReserva(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="estados_reserva", columnas_pk="id_estado_reserva")

    def _fila_a_objeto(self, fila: dict) -> EstadoReserva:
        return EstadoReserva(fila["id_estado_reserva"], fila["descripcion"])

    def _objeto_a_valores(self, objeto: EstadoReserva) -> dict:
        return {"descripcion": objeto.descripcion}

    def obtener_por_descripcion(self, descripcion: str) -> EstadoReserva:
        resultados = self.buscar("descripcion", descripcion)
        return resultados[0] if resultados else None


class RepositorioReservas(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="reservas", columnas_pk="id_reserva")
        self._repo_usuarios = RepositorioUsuarios()
        self._repo_libros = RepositorioLibros()
        self._repo_empleados = RepositorioEmpleados()
        self._repo_sucursales = RepositorioSucursales()
        self._repo_admins = RepositorioAdminUsers()
        self._repo_estados = RepositorioEstadosReserva()

    def _fila_a_objeto(self, fila: dict) -> Reserva:
        usuario = self._repo_usuarios.obtener_por_id_completo(fila["id_usuario"])
        libro = self._repo_libros.obtener_por_id(fila["isbn"])
        estado = self._repo_estados.obtener_por_id(fila["id_estado_reserva"])
        empleado = self._repo_empleados.obtener_por_id_completo(fila["id_empleado"]) if fila.get("id_empleado") else None
        sucursal = self._repo_sucursales.obtener_por_id(fila["id_sucursal"]) if fila.get("id_sucursal") else None
        admin = self._repo_admins.obtener_por_id_completo(fila["id_admin"]) if fila.get("id_admin") else None

        return Reserva(
            id_reserva=fila["id_reserva"],
            usuario=usuario,
            libro=libro,
            fecha_reserva=fila["fecha_reserva"],
            fecha_expiracion=fila["fecha_expiracion"],
            estado=estado,
            empleado=empleado,
            sucursal=sucursal,
            admin=admin,
        )

    def _objeto_a_valores(self, objeto: Reserva) -> dict:
        return {
            "id_usuario": objeto.usuario.id_usuario,
            "isbn": objeto.libro.isbn,
            "fecha_reserva": objeto.fecha_reserva,
            "fecha_expiracion": objeto.fecha_expiracion,
            "id_estado_reserva": objeto.estado.id_estado_reserva,
            "id_empleado": objeto.empleado.id_empleado if objeto.empleado else None,
            "id_sucursal": objeto.sucursal.id_sucursal if objeto.sucursal else None,
            "id_admin": objeto.admin.id_admin if objeto.admin else None,
        }

    def obtener_vigentes_por_usuario(self, id_usuario: int) -> list:
        sql = """
            SELECT r.* FROM reservas r
            INNER JOIN estados_reserva e ON e.id_estado_reserva = r.id_estado_reserva
            WHERE r.id_usuario = %s AND e.descripcion IN ('Pendiente', 'Confirmada')
        """
        filas = self.ejecutar_consulta_personalizada(sql, (id_usuario,))
        return [self._fila_a_objeto(fila) for fila in filas]

    def obtener_expiradas(self, fecha_referencia: date) -> list:
        sql = """
            SELECT r.* FROM reservas r
            INNER JOIN estados_reserva e ON e.id_estado_reserva = r.id_estado_reserva
            WHERE e.descripcion IN ('Pendiente', 'Confirmada') AND r.fecha_expiracion < %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (fecha_referencia,))
        return [self._fila_a_objeto(fila) for fila in filas]

    def cambiar_estado(self, id_reserva: int, id_estado_reserva: int) -> bool:
        sql = "UPDATE reservas SET id_estado_reserva = %s WHERE id_reserva = %s"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (id_estado_reserva, id_reserva))
        afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return afectadas > 0


class RepositorioReportes(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="reportes", columnas_pk="id_reporte")
        self._repo_admins = RepositorioAdminUsers()

    def _fila_a_objeto(self, fila: dict) -> Reporte:
        admin = self._repo_admins.obtener_por_id_completo(fila["id_admin"])
        return Reporte(
            id_reporte=fila["id_reporte"],
            admin=admin,
            tipo_reporte=fila["tipo_reporte"],
            descripcion=fila.get("descripcion"),
            fecha_generado=fila["fecha_generado"],
        )

    def _objeto_a_valores(self, objeto: Reporte) -> dict:
        return {
            "id_admin": objeto.admin.id_admin,
            "tipo_reporte": objeto.tipo_reporte,
            "descripcion": objeto.descripcion,
        }
