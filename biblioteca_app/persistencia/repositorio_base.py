"""
persistencia/repositorio_base.py
----------------------------------
Clase ABSTRACTA que define el contrato CRUD genérico para cualquier
entidad de la base de datos. Las clases concretas (RepositorioUsuarios,
RepositorioLibros, etc.) heredan de aquí y solo indican el nombre de
tabla, el nombre de la(s) columna(s) clave y cómo convertir una fila
de la BD en un objeto del dominio (modelos/).

Aplica:
- HERENCIA: todos los repositorios concretos heredan de esta clase.
- ENCAPSULAMIENTO: la conexión vive "protegida" (_db) y el SQL crudo
  nunca se expone fuera de esta capa.
- POLIMORFISMO: cada repositorio concreto implementa _fila_a_objeto()
  y _objeto_a_valores() de forma distinta según su entidad.
"""

from abc import ABC, abstractmethod
from persistencia.conexion_db import ConexionDB


class RepositorioBase(ABC):
    """
    Repositorio genérico. Soporta tanto clave primaria simple
    (un solo campo, ej. id_usuario) como clave primaria compuesta
    (una tupla de campos, ej. (id_rol, id_permiso)).
    """

    def __init__(self, nombre_tabla: str, columnas_pk):
        """
        :param nombre_tabla: nombre real de la tabla en MySQL.
        :param columnas_pk: nombre de la PK como string ("id_usuario")
                             o tupla de strings para PK compuesta
                             (("id_rol", "id_permiso")).
        """
        self._db = ConexionDB()
        self._tabla = nombre_tabla
        # Normalizamos siempre a tupla internamente para simplificar la lógica
        self._columnas_pk = (
            (columnas_pk,) if isinstance(columnas_pk, str) else tuple(columnas_pk)
        )

    # ---------------- Métodos abstractos (cada repositorio concreto los define) ----------------

    @abstractmethod
    def _fila_a_objeto(self, fila: dict):
        """Convierte una fila (dict) devuelta por MySQL en un objeto del dominio."""
        raise NotImplementedError

    @abstractmethod
    def _objeto_a_valores(self, objeto) -> dict:
        """Convierte un objeto del dominio en un dict {columna: valor} para INSERT/UPDATE."""
        raise NotImplementedError

    # ---------------- CRUD genérico ----------------

    def obtener_todos(self, orden: str = None) -> list:
        cursor = self._db.obtener_cursor()
        sql = f"SELECT * FROM {self._tabla}"
        if orden:
            sql += f" ORDER BY {orden}"
        cursor.execute(sql)
        filas = cursor.fetchall()
        cursor.close()
        return [self._fila_a_objeto(fila) for fila in filas]

    def obtener_por_id(self, *valores_pk):
        """
        Acepta uno o varios valores según la PK sea simple o compuesta.
        Ejemplos:
            repo.obtener_por_id(5)
            repo.obtener_por_id(1, 3)   # PK compuesta (id_rol=1, id_permiso=3)
        """
        condiciones = " AND ".join(f"{col} = %s" for col in self._columnas_pk)
        sql = f"SELECT * FROM {self._tabla} WHERE {condiciones}"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, valores_pk)
        fila = cursor.fetchone()
        cursor.close()
        return self._fila_a_objeto(fila) if fila else None

    def crear(self, objeto):
        datos = self._objeto_a_valores(objeto)
        columnas = ", ".join(datos.keys())
        marcadores = ", ".join(["%s"] * len(datos))
        sql = f"INSERT INTO {self._tabla} ({columnas}) VALUES ({marcadores})"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, list(datos.values()))
        nuevo_id = cursor.lastrowid
        self._db.confirmar()
        cursor.close()
        return nuevo_id

    def actualizar(self, objeto, *valores_pk) -> bool:
        datos = self._objeto_a_valores(objeto)
        set_clause = ", ".join(f"{col} = %s" for col in datos.keys())
        condiciones = " AND ".join(f"{col} = %s" for col in self._columnas_pk)
        sql = f"UPDATE {self._tabla} SET {set_clause} WHERE {condiciones}"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, list(datos.values()) + list(valores_pk))
        filas_afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return filas_afectadas > 0

    def eliminar(self, *valores_pk) -> bool:
        condiciones = " AND ".join(f"{col} = %s" for col in self._columnas_pk)
        sql = f"DELETE FROM {self._tabla} WHERE {condiciones}"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, valores_pk)
        filas_afectadas = cursor.rowcount
        self._db.confirmar()
        cursor.close()
        return filas_afectadas > 0

    def buscar(self, columna: str, valor, comparador: str = "=") -> list:
        """
        Búsqueda genérica por una columna. Permite además filtros tipo LIKE.
        Ejemplo: repo.buscar("titulo", "%harry%", "LIKE")
        """
        sql = f"SELECT * FROM {self._tabla} WHERE {columna} {comparador} %s"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (valor,))
        filas = cursor.fetchall()
        cursor.close()
        return [self._fila_a_objeto(fila) for fila in filas]

    def ejecutar_consulta_personalizada(self, sql: str, parametros: tuple = ()) -> list:
        """
        Vía de escape controlada para consultas más complejas (JOINs,
        agregaciones) que no encajan en el CRUD genérico. Se usa sobre
        todo desde los repositorios concretos, no directamente desde
        servicios/controladores.
        """
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, parametros)
        filas = cursor.fetchall()
        cursor.close()
        return filas
