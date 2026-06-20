"""
controladores/admins_controller.py
------------------------------------------
CRUD de AdminUser (creación y listado; la edición de password no se
incluye aquí por seguridad/simplicidad académica, solo creación y
gestión básica).
"""

from persistencia.repositorio_personas import RepositorioAdminUsers
from persistencia.repositorio_roles import RepositorioRoles
from servicios.servicio_auth import ServicioAuth


class AdminsController:
    def __init__(self):
        self._repo_admins = RepositorioAdminUsers()
        self._repo_roles = RepositorioRoles()
        self._servicio_auth = ServicioAuth()

    def listar(self) -> list:
        return self._repo_admins.obtener_todos_completo()

    def opciones_rol(self) -> list:
        return [(r.id_rol, r.nombre_rol) for r in self._repo_roles.obtener_todos(orden="id_rol")]

    def crear(self, datos: dict) -> int:
        existente = self._repo_admins.obtener_por_admin_user(datos["admin_user"])
        if existente is not None:
            raise ValueError("Ese nombre de usuario administrador ya está en uso.")
        return self._servicio_auth.registrar_admin(
            nombre=datos["nombre"],
            email=datos["email"],
            phone=datos.get("phone"),
            admin_user=datos["admin_user"],
            password_plano=datos["password"],
            id_rol=datos["id_rol"],
        )

    def eliminar(self, id_admin: int) -> bool:
        admin = self._repo_admins.obtener_por_id_completo(id_admin)
        if admin is None:
            return False
        cursor = self._repo_admins._db.obtener_cursor()
        try:
            cursor.execute("DELETE FROM admin_users WHERE id_admin = %s", (id_admin,))
            cursor.execute("DELETE FROM personas WHERE id_persona = %s", (admin.id_persona,))
            self._repo_admins._db.confirmar()
            return True
        except Exception:
            self._repo_admins._db.cancelar()
            raise
        finally:
            cursor.close()
