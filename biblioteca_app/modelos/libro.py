"""
modelos/libro.py
------------------
Categoria, EstadoLibro, Autor y Libro.

ASOCIACIÓN: Libro -> Categoria, Libro -> EstadoLibro (referencias simples).
AGREGACIÓN: Libro agrega una lista de Autor (coautoría). Un Autor
existe de forma independiente del Libro: si se elimina el libro,
el autor sigue existiendo en el catálogo.
"""


class Categoria:
    def __init__(self, id_categoria: int, nombre_categoria: str, descripcion: str = ""):
        self._id_categoria = id_categoria
        self._nombre_categoria = nombre_categoria
        self._descripcion = descripcion

    @property
    def id_categoria(self) -> int:
        return self._id_categoria

    @property
    def nombre_categoria(self) -> str:
        return self._nombre_categoria

    @property
    def descripcion(self) -> str:
        return self._descripcion

    def __repr__(self):
        return f"Categoria({self._id_categoria}, '{self._nombre_categoria}')"


class EstadoLibro:
    def __init__(self, id_estado: int, nombre_estado: str):
        self._id_estado = id_estado
        self._nombre_estado = nombre_estado

    @property
    def id_estado(self) -> int:
        return self._id_estado

    @property
    def nombre_estado(self) -> str:
        return self._nombre_estado

    def __repr__(self):
        return f"EstadoLibro({self._id_estado}, '{self._nombre_estado}')"


class Autor:
    def __init__(self, id_autor: int, nombre: str):
        self._id_autor = id_autor
        self._nombre = nombre

    @property
    def id_autor(self) -> int:
        return self._id_autor

    @property
    def nombre(self) -> str:
        return self._nombre

    def __eq__(self, otro):
        return isinstance(otro, Autor) and self._id_autor == otro._id_autor

    def __hash__(self):
        return hash(self._id_autor)

    def __repr__(self):
        return f"Autor({self._id_autor}, '{self._nombre}')"


class Libro:
    """
    ISBN es la clave primaria natural (no autoincremental), tal como
    está definido en el esquema SQL.
    """

    def __init__(
        self,
        isbn: str,
        titulo: str,
        autor_principal: str,
        categoria: Categoria,
        estado: EstadoLibro,
        editorial: str = None,
        anio_publicacion: int = None,
    ):
        self._isbn = isbn
        self._titulo = titulo
        self._autor_principal = autor_principal  # campo VARCHAR plano del esquema original
        self._editorial = editorial
        self._anio_publicacion = anio_publicacion
        self._categoria = categoria   # asociación
        self._estado = estado         # asociación
        self._coautores: list[Autor] = []  # agregación (tabla libros_autores)

    @property
    def isbn(self) -> str:
        return self._isbn

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str):
        if not valor or not valor.strip():
            raise ValueError("El título no puede estar vacío")
        self._titulo = valor.strip()

    @property
    def autor_principal(self) -> str:
        return self._autor_principal

    @property
    def editorial(self) -> str:
        return self._editorial

    @property
    def anio_publicacion(self) -> int:
        return self._anio_publicacion

    @property
    def categoria(self) -> Categoria:
        return self._categoria

    @property
    def estado(self) -> EstadoLibro:
        return self._estado

    @estado.setter
    def estado(self, nuevo_estado: EstadoLibro):
        self._estado = nuevo_estado

    @property
    def coautores(self) -> list:
        return list(self._coautores)

    def agregar_coautor(self, autor: Autor):
        if autor not in self._coautores:
            self._coautores.append(autor)

    def esta_disponible(self) -> bool:
        return self._estado.nombre_estado == "Disponible"

    def __repr__(self):
        return f"Libro('{self._isbn}', '{self._titulo}')"
