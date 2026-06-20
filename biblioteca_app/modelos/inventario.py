"""
modelos/inventario.py
------------------------
Inventario representa cuántas copias de un Libro hay en una Sucursal
concreta. ASOCIACIÓN doble: Inventario -> Libro, Inventario -> Sucursal.
"""


class Inventario:
    def __init__(
        self,
        id_inventario: int,
        libro,       # objeto Libro
        sucursal,    # objeto Sucursal
        cantidad_disponible: int = 0,
        cantidad_total: int = 0,
    ):
        self._id_inventario = id_inventario
        self._libro = libro
        self._sucursal = sucursal
        self._cantidad_disponible = cantidad_disponible
        self._cantidad_total = cantidad_total

    @property
    def id_inventario(self) -> int:
        return self._id_inventario

    @property
    def libro(self):
        return self._libro

    @property
    def sucursal(self):
        return self._sucursal

    @property
    def cantidad_disponible(self) -> int:
        return self._cantidad_disponible

    @property
    def cantidad_total(self) -> int:
        return self._cantidad_total

    def prestar_unidad(self) -> bool:
        """Disminuye en 1 la disponibilidad si hay stock. Devuelve éxito/fracaso."""
        if self._cantidad_disponible <= 0:
            return False
        self._cantidad_disponible -= 1
        return True

    def devolver_unidad(self):
        """Aumenta en 1 la disponibilidad, sin pasar del total."""
        if self._cantidad_disponible < self._cantidad_total:
            self._cantidad_disponible += 1

    def __repr__(self):
        return (
            f"Inventario(libro='{self._libro.titulo if self._libro else None}', "
            f"sucursal='{self._sucursal.nombre if self._sucursal else None}', "
            f"disponible={self._cantidad_disponible}/{self._cantidad_total})"
        )
