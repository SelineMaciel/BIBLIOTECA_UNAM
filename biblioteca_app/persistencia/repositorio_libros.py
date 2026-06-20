"""
persistencia/repositorio_libros.py
--------------------------------------
Repositorios concretos para Categoria, EstadoLibro, Autor y Libro.
RepositorioLibros usa ISBN (VARCHAR) como PK en lugar de un id
autoincremental, demostrando que RepositorioBase es flexible ante
distintos tipos de clave primaria.
"""

from persistencia.repositorio_base import RepositorioBase
from modelos.libro import Categoria, EstadoLibro, Autor, Libro


class RepositorioCategorias(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="categorias", columnas_pk="id_categoria")

    def _fila_a_objeto(self, fila: dict) -> Categoria:
        return Categoria(fila["id_categoria"], fila["nombre_categoria"], fila.get("descripcion"))

    def _objeto_a_valores(self, objeto: Categoria) -> dict:
        return {"nombre_categoria": objeto.nombre_categoria, "descripcion": objeto.descripcion}


class RepositorioEstadosLibro(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="estados_libro", columnas_pk="id_estado")

    def _fila_a_objeto(self, fila: dict) -> EstadoLibro:
        return EstadoLibro(fila["id_estado"], fila["nombre_estado"])

    def _objeto_a_valores(self, objeto: EstadoLibro) -> dict:
        return {"nombre_estado": objeto.nombre_estado}


class RepositorioAutores(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="autores", columnas_pk="id_autor")

    def _fila_a_objeto(self, fila: dict) -> Autor:
        return Autor(fila["id_autor"], fila["nombre"])

    def _objeto_a_valores(self, objeto: Autor) -> dict:
        return {"nombre": objeto.nombre}


class RepositorioLibros(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="libros", columnas_pk="ISBN")
        self._repo_categorias = RepositorioCategorias()
        self._repo_estados = RepositorioEstadosLibro()
        self._repo_autores = RepositorioAutores()

    def _fila_a_objeto(self, fila: dict) -> Libro:
        categoria = self._repo_categorias.obtener_por_id(fila["id_categoria"])
        estado = self._repo_estados.obtener_por_id(fila["id_estado"])
        libro = Libro(
            isbn=fila["ISBN"],
            titulo=fila["titulo"],
            autor_principal=fila["autor"],
            categoria=categoria,
            estado=estado,
            editorial=fila.get("editorial"),
            anio_publicacion=fila.get("anio_publicacion"),
        )
        for coautor in self._obtener_coautores(fila["ISBN"]):
            libro.agregar_coautor(coautor)
        return libro

    def _objeto_a_valores(self, objeto: Libro) -> dict:
        return {
            "ISBN": objeto.isbn,
            "titulo": objeto.titulo,
            "autor": objeto.autor_principal,
            "editorial": objeto.editorial,
            "anio_publicacion": objeto.anio_publicacion,
            "id_categoria": objeto.categoria.id_categoria,
            "id_estado": objeto.estado.id_estado,
        }

    def _obtener_coautores(self, isbn: str) -> list:
        sql = """
            SELECT a.id_autor, a.nombre
            FROM autores a
            INNER JOIN libros_autores la ON la.id_autor = a.id_autor
            WHERE la.ISBN = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (isbn,))
        return [self._repo_autores._fila_a_objeto(fila) for fila in filas]

    def agregar_coautor(self, isbn: str, id_autor: int):
        sql = "INSERT INTO libros_autores (ISBN, id_autor) VALUES (%s, %s)"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (isbn, id_autor))
        self._db.confirmar()
        cursor.close()

    def buscar_por_titulo(self, texto: str) -> list:
        return self.buscar("titulo", f"%{texto}%", "LIKE")

    def buscar_por_categoria(self, id_categoria: int) -> list:
        return self.buscar("id_categoria", id_categoria)

    def buscar_disponibles(self) -> list:
        """Libros cuyo estado es 'Disponible' (filtra por nombre de estado)."""
        sql = """
            SELECT l.* FROM libros l
            INNER JOIN estados_libro e ON e.id_estado = l.id_estado
            WHERE e.nombre_estado = 'Disponible'
        """
        filas = self.ejecutar_consulta_personalizada(sql)
        return [self._fila_a_objeto(fila) for fila in filas]

    def cambiar_estado(self, isbn: str, id_estado: int) -> bool:
        sql = "UPDATE libros SET id_estado = %s WHERE ISBN = %s"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (id_estado, isbn))
        afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return afectadas > 0
