"""
servicios/servicio_reservas.py
------------------------------------
Reglas de negocio de reservas: crear una reserva con fecha de
expiración calculada, verificar disponibilidad, y expirar
automáticamente las reservas vencidas.
"""

from datetime import date, timedelta

from persistencia.repositorio_reservas import RepositorioReservas, RepositorioEstadosReserva
from persistencia.repositorio_libros import RepositorioLibros


class ReservaNoPermitidaError(Exception):
    pass


class ServicioReservas:
    DIAS_VIGENCIA_RESERVA = 3  # regla de negocio: cuánto dura una reserva antes de expirar

    def __init__(self):
        self._repo_reservas = RepositorioReservas()
        self._repo_estados = RepositorioEstadosReserva()
        self._repo_libros = RepositorioLibros()

    def crear_reserva(self, id_usuario: int, isbn: str, id_sucursal: int = None, id_empleado: int = None, id_admin: int = None) -> int:
        libro = self._repo_libros.obtener_por_id(isbn)
        if libro is None:
            raise ReservaNoPermitidaError("El libro no existe")

        estado_pendiente = self._repo_estados.obtener_por_descripcion("Pendiente")
        fecha_reserva = date.today()
        fecha_expiracion = fecha_reserva + timedelta(days=self.DIAS_VIGENCIA_RESERVA)

        valores = {
            "id_usuario": id_usuario,
            "isbn": isbn,
            "fecha_reserva": fecha_reserva,
            "fecha_expiracion": fecha_expiracion,
            "id_estado_reserva": estado_pendiente.id_estado_reserva,
            "id_empleado": id_empleado,
            "id_sucursal": id_sucursal,
            "id_admin": id_admin,
        }
        columnas = ", ".join(valores.keys())
        marcadores = ", ".join(["%s"] * len(valores))
        sql = f"INSERT INTO reservas ({columnas}) VALUES ({marcadores})"
        cursor = self._repo_reservas._db.obtener_cursor()
        cursor.execute(sql, list(valores.values()))
        nuevo_id = cursor.lastrowid
        self._repo_reservas._db.confirmar()
        cursor.close()
        return nuevo_id

    def confirmar_reserva(self, id_reserva: int) -> bool:
        estado_confirmada = self._repo_estados.obtener_por_descripcion("Confirmada")
        return self._repo_reservas.cambiar_estado(id_reserva, estado_confirmada.id_estado_reserva)

    def cancelar_reserva(self, id_reserva: int) -> bool:
        estado_cancelada = self._repo_estados.obtener_por_descripcion("Cancelada")
        return self._repo_reservas.cambiar_estado(id_reserva, estado_cancelada.id_estado_reserva)

    def expirar_reservas_vencidas(self) -> int:
        """Marca como 'Expirada' todas las reservas vigentes cuya fecha
        de expiración ya pasó. Devuelve cuántas se actualizaron."""
        estado_expirada = self._repo_estados.obtener_por_descripcion("Expirada")
        vencidas = self._repo_reservas.obtener_expiradas(date.today())
        contador = 0
        for reserva in vencidas:
            if self._repo_reservas.cambiar_estado(reserva.id_reserva, estado_expirada.id_estado_reserva):
                contador += 1
        return contador

    def reservas_vigentes_de_usuario(self, id_usuario: int) -> list:
        return self._repo_reservas.obtener_vigentes_por_usuario(id_usuario)
