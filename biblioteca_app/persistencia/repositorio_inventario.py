"""
persistencia/repositorio_inventario.py
------------------------------------------
Repositorio concreto para Inventario, ensamblando Libro y Sucursal.
"""

from persistencia.repositorio_base import RepositorioBase
from persistencia.repositorio_libros import RepositorioLibros
from persistencia.repositorio_membresias import RepositorioSucursales
from modelos.inventario import Inventario


class RepositorioInventario(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="inventario", columnas_pk="id_inventario")
        self._repo_libros = RepositorioLibros()
        self._repo_sucursales = RepositorioSucursales()

    def _fila_a_objeto(self, fila: dict) -> Inventario:
        libro = self._repo_libros.obtener_por_id(fila["isbn"])
        sucursal = self._repo_sucursales.obtener_por_id(fila["id_sucursal"])
        return Inventario(
            id_inventario=fila["id_inventario"],
            libro=libro,
            sucursal=sucursal,
            cantidad_disponible=fila["cantidad_disponible"],
            cantidad_total=fila["cantidad_total"],
        )

    def _objeto_a_valores(self, objeto: Inventario) -> dict:
        return {
            "isbn": objeto.libro.isbn,
            "id_sucursal": objeto.sucursal.id_sucursal,
            "cantidad_disponible": objeto.cantidad_disponible,
            "cantidad_total": objeto.cantidad_total,
        }

    def obtener_por_libro_y_sucursal(self, isbn: str, id_sucursal: int) -> Inventario:
        sql = "SELECT * FROM inventario WHERE isbn = %s AND id_sucursal = %s"
        filas = self.ejecutar_consulta_personalizada(sql, (isbn, id_sucursal))
        return self._fila_a_objeto(filas[0]) if filas else None

    def obtener_por_libro(self, isbn: str) -> list:
        return self.buscar("isbn", isbn)

    def obtener_todos_completo(self) -> list:
        """Igual que obtener_todos(), pero con un nombre explícito que
        deja claro que cada fila viene con Libro y Sucursal ya ensamblados
        (consistente con el patrón usado en los demás repositorios)."""
        return self.obtener_todos(orden="id_inventario")

    def ajustar_disponibilidad(self, id_inventario: int, delta: int) -> bool:
        """delta puede ser -1 (al prestar) o +1 (al devolver)."""
        sql = """
            UPDATE inventario
            SET cantidad_disponible = cantidad_disponible + %s
            WHERE id_inventario = %s
              AND cantidad_disponible + %s >= 0
              AND cantidad_disponible + %s <= cantidad_total
        """
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (delta, id_inventario, delta, delta))
        afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return afectadas > 0
