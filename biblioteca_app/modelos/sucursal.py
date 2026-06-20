"""
modelos/sucursal.py
---------------------
Sucursal física de la biblioteca. Se asocia con Empleado, Inventario,
Prestamo y Reserva. AGREGACIÓN: una Sucursal agrega una lista de
registros de Inventario (los libros que tiene disponibles), pero el
inventario referencia al libro de forma independiente.
"""


class Sucursal:
    def __init__(
        self,
        id_sucursal: int,
        nombre: str,
        calle: str,
        ciudad: str,
        telefono: str = None,
    ):
        self._id_sucursal = id_sucursal
        self._nombre = nombre
        self._calle = calle
        self._ciudad = ciudad
        self._telefono = telefono
        self._inventario = []  # lista agregada de objetos Inventario

    @property
    def id_sucursal(self) -> int:
        return self._id_sucursal

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def direccion_completa(self) -> str:
        return f"{self._calle}, {self._ciudad}"

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def inventario(self) -> list:
        return list(self._inventario)

    def agregar_item_inventario(self, item_inventario):
        self._inventario.append(item_inventario)

    def __repr__(self):
        return f"Sucursal({self._id_sucursal}, '{self._nombre}')"
