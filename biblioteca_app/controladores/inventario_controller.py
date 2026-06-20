"""
controladores/inventario_controller.py
--------------------------------------------
CRUD completo de Inventario. Respeta la restricción UNIQUE(isbn,
id_sucursal) definida en el esquema: no se puede crear una segunda
fila de inventario para el mismo libro en la misma sucursal, solo
editar la existente.
"""

from persistencia.repositorio_inventario import RepositorioInventario
from persistencia.repositorio_libros import RepositorioLibros
from persistencia.repositorio_membresias import RepositorioSucursales


class InventarioDuplicadoError(Exception):
    pass


class InventarioController:
    def __init__(self):
        self._repo_inventario = RepositorioInventario()
        self._repo_libros = RepositorioLibros()
        self._repo_sucursales = RepositorioSucursales()

    def listar(self) -> list:
        return self._repo_inventario.obtener_todos_completo()

    def obtener(self, id_inventario: int):
        return self._repo_inventario.obtener_por_id(id_inventario)

    def opciones_libro(self) -> list:
        return [(l.isbn, f"{l.titulo} - {l.isbn}") for l in self._repo_libros.obtener_todos(orden="titulo")]

    def opciones_sucursal(self) -> list:
        return [(s.id_sucursal, s.nombre) for s in self._repo_sucursales.obtener_todos(orden="id_sucursal")]

    def crear(self, datos: dict) -> int:
        existente = self._repo_inventario.obtener_por_libro_y_sucursal(datos["isbn"], datos["id_sucursal"])
        if existente is not None:
            raise InventarioDuplicadoError(
                "Ya existe un registro de inventario para este libro en esta sucursal. "
                "Edítalo en vez de crear uno nuevo."
            )

        from modelos.inventario import Inventario
        libro = self._repo_libros.obtener_por_id(datos["isbn"])
        sucursal = self._repo_sucursales.obtener_por_id(datos["id_sucursal"])
        item = Inventario(
            id_inventario=None,
            libro=libro,
            sucursal=sucursal,
            cantidad_disponible=datos["cantidad_disponible"],
            cantidad_total=datos["cantidad_total"],
        )
        return self._repo_inventario.crear(item)

    def actualizar(self, id_inventario: int, datos: dict) -> bool:
        actual = self._repo_inventario.obtener_por_id(id_inventario)
        if actual is None:
            return False

        from modelos.inventario import Inventario
        libro = self._repo_libros.obtener_por_id(datos["isbn"])
        sucursal = self._repo_sucursales.obtener_por_id(datos["id_sucursal"])
        item = Inventario(
            id_inventario=id_inventario,
            libro=libro,
            sucursal=sucursal,
            cantidad_disponible=datos["cantidad_disponible"],
            cantidad_total=datos["cantidad_total"],
        )
        return self._repo_inventario.actualizar(item, id_inventario)

    def eliminar(self, id_inventario: int) -> bool:
        return self._repo_inventario.eliminar(id_inventario)
