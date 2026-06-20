"""
persistencia/repositorio_membresias.py
-----------------------------------------
Repositorios concretos simples para Membresia y Sucursal.
"""

from persistencia.repositorio_base import RepositorioBase
from modelos.membresia import Membresia
from modelos.sucursal import Sucursal


class RepositorioMembresias(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="membresias", columnas_pk="id_membresia")

    def _fila_a_objeto(self, fila: dict) -> Membresia:
        return Membresia(
            id_membresia=fila["id_membresia"],
            tipo_membresia=fila["tipo_membresia"],
            max_prestamos=fila["max_prestamos"],
            dias_prestamo=fila["dias_prestamo"],
        )

    def _objeto_a_valores(self, objeto: Membresia) -> dict:
        return {
            "tipo_membresia": objeto.tipo_membresia,
            "max_prestamos": objeto.max_prestamos,
            "dias_prestamo": objeto.dias_prestamo,
        }


class RepositorioSucursales(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="sucursales", columnas_pk="id_sucursal")

    def _fila_a_objeto(self, fila: dict) -> Sucursal:
        return Sucursal(
            id_sucursal=fila["id_sucursal"],
            nombre=fila["nombre"],
            calle=fila["calle"],
            ciudad=fila["ciudad"],
            telefono=fila.get("telefono"),
        )

    def _objeto_a_valores(self, objeto: Sucursal) -> dict:
        return {
            "nombre": objeto.nombre,
            "calle": objeto._calle,
            "ciudad": objeto._ciudad,
            "telefono": objeto.telefono,
        }
