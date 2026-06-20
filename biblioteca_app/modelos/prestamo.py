"""
modelos/prestamo.py
----------------------
EstadoPrestamo, Multa y Prestamo.

COMPOSICIÓN: Prestamo "es dueño" de sus Multa. Una Multa no tiene
sentido de existir de forma aislada: siempre nace asociada a un
préstamo concreto (recargo por días de retraso). Por eso aquí la
lista de multas se gestiona DESDE el propio Prestamo, a diferencia
de la agregación de coautores en Libro, donde el Autor sí vive
independiente.
"""

from datetime import date


class EstadoPrestamo:
    def __init__(self, id_estado_prestamo: int, descripcion: str):
        self._id_estado_prestamo = id_estado_prestamo
        self._descripcion = descripcion

    @property
    def id_estado_prestamo(self) -> int:
        return self._id_estado_prestamo

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def __repr__(self):
        return f"EstadoPrestamo({self._id_estado_prestamo}, '{self._descripcion}')"


class Multa:
    """
    Una Multa SIEMPRE pertenece a un Prestamo (composición). No se
    crea de forma independiente desde fuera de la clase Prestamo.
    """

    def __init__(
        self,
        id_multa: int,
        monto: float,
        fecha_multa: date,
        estado_pago: str = "PENDIENTE",
    ):
        self._id_multa = id_multa
        self._monto = monto
        self._fecha_multa = fecha_multa
        self._estado_pago = estado_pago  # 'PENDIENTE' | 'PAGADO'

    @property
    def id_multa(self) -> int:
        return self._id_multa

    @property
    def monto(self) -> float:
        return self._monto

    @property
    def fecha_multa(self) -> date:
        return self._fecha_multa

    @property
    def estado_pago(self) -> str:
        return self._estado_pago

    def marcar_pagada(self):
        self._estado_pago = "PAGADO"

    def esta_pendiente(self) -> bool:
        return self._estado_pago == "PENDIENTE"

    def __repr__(self):
        return f"Multa({self._id_multa}, monto={self._monto}, estado='{self._estado_pago}')"


class Prestamo:
    """
    ASOCIACIÓN: Prestamo -> Usuario, Prestamo -> Libro, Prestamo ->
    Empleado, Prestamo -> Sucursal (todas son referencias, ninguna
    de estas entidades depende del préstamo para existir).

    COMPOSICIÓN: Prestamo -> lista de Multa (las multas sí dependen
    por completo del préstamo).
    """

    def __init__(
        self,
        id_prestamo: int,
        usuario,             # objeto Usuario (asociación)
        libro,                # objeto Libro (asociación)
        fecha_prestamo: date,
        estado: EstadoPrestamo,
        fecha_devolucion: date = None,
        empleado=None,        # objeto Empleado (asociación, puede ser None)
        sucursal=None,        # objeto Sucursal (asociación, puede ser None)
    ):
        self._id_prestamo = id_prestamo
        self._usuario = usuario
        self._libro = libro
        self._fecha_prestamo = fecha_prestamo
        self._fecha_devolucion = fecha_devolucion
        self._estado = estado
        self._empleado = empleado
        self._sucursal = sucursal
        self._multas: list[Multa] = []  # composición

    @property
    def id_prestamo(self) -> int:
        return self._id_prestamo

    @property
    def usuario(self):
        return self._usuario

    @property
    def libro(self):
        return self._libro

    @property
    def fecha_prestamo(self) -> date:
        return self._fecha_prestamo

    @property
    def fecha_devolucion(self) -> date:
        return self._fecha_devolucion

    @property
    def estado(self) -> EstadoPrestamo:
        return self._estado

    @property
    def empleado(self):
        return self._empleado

    @property
    def sucursal(self):
        return self._sucursal

    @property
    def multas(self) -> list:
        return list(self._multas)

    # ---------------- Comportamiento (composición en acción) ----------------

    def generar_multa(self, id_multa: int, monto: float, fecha_multa: date) -> Multa:
        """
        Crea una nueva Multa DESDE el préstamo. Refleja la composición:
        nadie crea una Multa "suelta"; siempre nace de aquí.
        """
        nueva_multa = Multa(id_multa, monto, fecha_multa)
        self._multas.append(nueva_multa)
        return nueva_multa

    def total_multas_pendientes(self) -> float:
        return sum(m.monto for m in self._multas if m.esta_pendiente())

    def fue_devuelto(self) -> bool:
        return self._fecha_devolucion is not None

    def dias_retraso(self, fecha_referencia: date = None) -> int:
        """Días de retraso respecto a la fecha límite (si ya venció)."""
        fecha_referencia = fecha_referencia or date.today()
        fecha_limite = self._fecha_prestamo  # se recalcula con la membresía en el servicio
        if self.fue_devuelto():
            return max(0, (self._fecha_devolucion - fecha_limite).days)
        return max(0, (fecha_referencia - fecha_limite).days)

    def registrar_devolucion(self, fecha_devolucion: date, estado_devuelto: EstadoPrestamo):
        self._fecha_devolucion = fecha_devolucion
        self._estado = estado_devuelto

    def __repr__(self):
        return (
            f"Prestamo({self._id_prestamo}, usuario='{self._usuario.nombre if self._usuario else None}', "
            f"libro='{self._libro.titulo if self._libro else None}', estado='{self._estado.descripcion}')"
        )
