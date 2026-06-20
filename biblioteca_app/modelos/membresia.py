"""
modelos/membresia.py
----------------------
Membresia define las reglas de negocio asociadas al tipo de usuario
(cuántos préstamos puede tener activos, por cuántos días). Se asocia
a Usuario por referencia (ASOCIACIÓN simple vía id_membresia, no
agregación: una membresía no "pertenece" a un usuario, muchos
usuarios comparten el mismo tipo de membresía).
"""


class Membresia:
    def __init__(
        self,
        id_membresia: int,
        tipo_membresia: str,
        max_prestamos: int = 3,
        dias_prestamo: int = 15,
    ):
        self._id_membresia = id_membresia
        self._tipo_membresia = tipo_membresia
        self._max_prestamos = max_prestamos
        self._dias_prestamo = dias_prestamo

    @property
    def id_membresia(self) -> int:
        return self._id_membresia

    @property
    def tipo_membresia(self) -> str:
        return self._tipo_membresia

    @property
    def max_prestamos(self) -> int:
        return self._max_prestamos

    @property
    def dias_prestamo(self) -> int:
        return self._dias_prestamo

    def __repr__(self):
        return (
            f"Membresia({self._id_membresia}, '{self._tipo_membresia}', "
            f"max={self._max_prestamos}, dias={self._dias_prestamo})"
        )
