"""
persistencia/repositorio_roles.py
------------------------------------
Repositorios concretos para Rol y Permiso. Heredan de RepositorioBase
(HERENCIA) e implementan los métodos abstractos según su propia
entidad (POLIMORFISMO: _fila_a_objeto y _objeto_a_valores se comportan
distinto en cada repositorio concreto del sistema).
"""

from persistencia.repositorio_base import RepositorioBase
from modelos.rol import Rol, Permiso


class RepositorioPermisos(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="permisos", columnas_pk="id_permiso")

    def _fila_a_objeto(self, fila: dict) -> Permiso:
        return Permiso(
            id_permiso=fila["id_permiso"],
            nombre_permiso=fila["nombre_permiso"],
            descripcion=fila.get("descripcion"),
        )

    def _objeto_a_valores(self, objeto: Permiso) -> dict:
        return {
            "nombre_permiso": objeto.nombre_permiso,
            "descripcion": objeto.descripcion,
        }


class RepositorioRoles(RepositorioBase):
    def __init__(self):
        super().__init__(nombre_tabla="roles", columnas_pk="id_rol")
        self._repo_permisos = RepositorioPermisos()

    def _fila_a_objeto(self, fila: dict) -> Rol:
        return Rol(
            id_rol=fila["id_rol"],
            nombre_rol=fila["nombre_rol"],
            descripcion=fila.get("descripcion"),
        )

    def _objeto_a_valores(self, objeto: Rol) -> dict:
        return {
            "nombre_rol": objeto.nombre_rol,
            "descripcion": objeto.descripcion,
        }

    def obtener_con_permisos(self, id_rol: int) -> Rol:
        """
        Carga un Rol y completa su lista agregada de Permiso
        consultando la tabla intermedia roles_permisos (JOIN manual).
        """
        rol = self.obtener_por_id(id_rol)
        if rol is None:
            return None

        sql = """
            SELECT p.id_permiso, p.nombre_permiso, p.descripcion
            FROM permisos p
            INNER JOIN roles_permisos rp ON rp.id_permiso = p.id_permiso
            WHERE rp.id_rol = %s
        """
        filas = self.ejecutar_consulta_personalizada(sql, (id_rol,))
        for fila in filas:
            rol.agregar_permiso(self._repo_permisos._fila_a_objeto(fila))
        return rol

    def obtener_todos_con_permisos(self) -> list:
        roles = self.obtener_todos(orden="id_rol")
        return [self.obtener_con_permisos(r.id_rol) for r in roles]

    def asignar_permiso(self, id_rol: int, id_permiso: int):
        sql = "INSERT INTO roles_permisos (id_rol, id_permiso) VALUES (%s, %s)"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (id_rol, id_permiso))
        self._db.confirmar()
        cursor.close()

    def quitar_permiso(self, id_rol: int, id_permiso: int):
        sql = "DELETE FROM roles_permisos WHERE id_rol = %s AND id_permiso = %s"
        cursor = self._db.obtener_cursor()
        cursor.execute(sql, (id_rol, id_permiso))
        self._db.confirmar()
        cursor.close()
