"""
modelos/reserva.py
---------------------
EstadoReserva, Reserva y Reporte.

ASOCIACIÓN: Reserva -> Usuario, Libro, Empleado, Sucursal, AdminUser.
COMPOSICIÓN: Reporte se compone de su propio contenido de datos
(no referencia un "objeto de análisis" externo reutilizable: el
contenido nace y vive únicamente dentro del reporte generado).
"""

from datetime import date, datetime


class EstadoReserva:
    def __init__(self, id_estado_reserva: int, descripcion: str):
        self._id_estado_reserva = id_estado_reserva
        self._descripcion = descripcion

    @property
    def id_estado_reserva(self) -> int:
        return self._id_estado_reserva

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def __repr__(self):
        return f"EstadoReserva({self._id_estado_reserva}, '{self._descripcion}')"


class Reserva:
    def __init__(
        self,
        id_reserva: int,
        usuario,                 # objeto Usuario (asociación)
        libro,                    # objeto Libro (asociación)
        fecha_reserva: date,
        fecha_expiracion: date,
        estado: EstadoReserva,
        empleado=None,            # objeto Empleado (asociación, opcional)
        sucursal=None,            # objeto Sucursal (asociación, opcional)
        admin=None,                # objeto AdminUser (asociación, opcional)
    ):
        self._id_reserva = id_reserva
        self._usuario = usuario
        self._libro = libro
        self._fecha_reserva = fecha_reserva
        self._fecha_expiracion = fecha_expiracion
        self._estado = estado
        self._empleado = empleado
        self._sucursal = sucursal
        self._admin = admin

    @property
    def id_reserva(self) -> int:
        return self._id_reserva

    @property
    def usuario(self):
        return self._usuario

    @property
    def libro(self):
        return self._libro

    @property
    def fecha_reserva(self) -> date:
        return self._fecha_reserva

    @property
    def fecha_expiracion(self) -> date:
        return self._fecha_expiracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado: EstadoReserva):
        self._estado = nuevo_estado

    @property
    def empleado(self):
        return self._empleado

    @property
    def sucursal(self):
        return self._sucursal

    @property
    def admin(self):
        return self._admin

    def esta_vigente(self, fecha_referencia: date = None) -> bool:
        fecha_referencia = fecha_referencia or date.today()
        return fecha_referencia <= self._fecha_expiracion

    def __repr__(self):
        return (
            f"Reserva({self._id_reserva}, usuario='{self._usuario.nombre if self._usuario else None}', "
            f"libro='{self._libro.titulo if self._libro else None}')"
        )


class Reporte:
    """
    Generado por un AdminUser. COMPOSICIÓN: el contenido (un dict con
    los datos calculados: tablas, estadísticas) se genera y vive
    únicamente dentro de esta instancia de Reporte.
    """

    def __init__(
        self,
        id_reporte: int,
        admin,                 # objeto AdminUser (asociación: quién lo generó)
        tipo_reporte: str,
        descripcion: str = "",
        fecha_generado: datetime = None,
        contenido: dict = None,
    ):
        self._id_reporte = id_reporte
        self._admin = admin
        self._tipo_reporte = tipo_reporte
        self._descripcion = descripcion
        self._fecha_generado = fecha_generado or datetime.now()
        self._contenido = contenido or {}  # compuesto: nace y vive aquí

    @property
    def id_reporte(self) -> int:
        return self._id_reporte

    @property
    def admin(self):
        return self._admin

    @property
    def tipo_reporte(self) -> str:
        return self._tipo_reporte

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @property
    def fecha_generado(self) -> datetime:
        return self._fecha_generado

    @property
    def contenido(self) -> dict:
        return dict(self._contenido)

    def __repr__(self):
        return f"Reporte({self._id_reporte}, tipo='{self._tipo_reporte}')"
