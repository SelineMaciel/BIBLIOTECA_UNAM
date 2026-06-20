"""
controladores/libros_controller.py
------------------------------------------
CRUD completo de Libro, con soporte de búsqueda por título y filtro
por categoría/disponibilidad.
"""

from persistencia.repositorio_libros import (
    RepositorioLibros,
    RepositorioCategorias,
    RepositorioEstadosLibro,
)


class ISBNDuplicadoError(Exception):
    pass


class LibrosController:
    def __init__(self):
        self._repo_libros = RepositorioLibros()
        self._repo_categorias = RepositorioCategorias()
        self._repo_estados = RepositorioEstadosLibro()

    def listar(self, texto: str = None, id_categoria: int = None, solo_disponibles: bool = False) -> list:
        if solo_disponibles:
            resultados = self._repo_libros.buscar_disponibles()
        elif texto:
            resultados = self._repo_libros.buscar_por_titulo(texto)
        elif id_categoria:
            resultados = self._repo_libros.buscar_por_categoria(id_categoria)
        else:
            resultados = self._repo_libros.obtener_todos(orden="titulo")

        # Si se pidió texto Y categoría a la vez, se intersectan en memoria
        if texto and id_categoria:
            resultados = [l for l in resultados if l.categoria.id_categoria == id_categoria]

        return resultados

    def obtener(self, isbn: str):
        return self._repo_libros.obtener_por_id(isbn)

    def opciones_categoria(self) -> list:
        return [(c.id_categoria, c.nombre_categoria) for c in self._repo_categorias.obtener_todos(orden="id_categoria")]

    def opciones_estado(self) -> list:
        return [(e.id_estado, e.nombre_estado) for e in self._repo_estados.obtener_todos(orden="id_estado")]

    def crear(self, datos: dict):
        existente = self._repo_libros.obtener_por_id(datos["isbn"])
        if existente is not None:
            raise ISBNDuplicadoError("Ya existe un libro registrado con ese ISBN.")

        categoria = self._repo_categorias.obtener_por_id(datos["id_categoria"])
        estado = self._repo_estados.obtener_por_id(datos["id_estado"])

        from modelos.libro import Libro
        libro = Libro(
            isbn=datos["isbn"],
            titulo=datos["titulo"],
            autor_principal=datos["autor"],
            categoria=categoria,
            estado=estado,
            editorial=datos.get("editorial"),
            anio_publicacion=datos.get("anio_publicacion"),
        )
        return self._repo_libros.crear(libro)

    def actualizar(self, isbn: str, datos: dict) -> bool:
        actual = self._repo_libros.obtener_por_id(isbn)
        if actual is None:
            return False

        categoria = self._repo_categorias.obtener_por_id(datos["id_categoria"])
        estado = self._repo_estados.obtener_por_id(datos["id_estado"])

        from modelos.libro import Libro
        libro = Libro(
            isbn=isbn,
            titulo=datos["titulo"],
            autor_principal=datos["autor"],
            categoria=categoria,
            estado=estado,
            editorial=datos.get("editorial"),
            anio_publicacion=datos.get("anio_publicacion"),
        )
        return self._repo_libros.actualizar(libro, isbn)

    def eliminar(self, isbn: str) -> bool:
        return self._repo_libros.eliminar(isbn)
